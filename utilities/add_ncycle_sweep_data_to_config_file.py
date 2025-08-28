import os
from typing import Tuple, List, Union
import numpy as np
import yaml
import h5py

def get_pnp_from_files(sweep_files: List[str]) -> float:
    for file in sweep_files:
        min_MPa_hdf5_per_file = []

        with h5py.File(file, 'r') as f:
            min_Pa_hdf5 = f['/Scan/Min output pressure (Pa)']
            min_MPa_hdf5_per_file.append(np.min(np.multiply(min_Pa_hdf5, 1e-6)))

        # Convert to numpy array and average across trials
        min_MPa_hdf5_per_file = np.min(np.mean(min_MPa_hdf5_per_file, axis=0))
    return float(np.abs(np.min(min_MPa_hdf5_per_file)))  # Return the maximum value across trials

def _get_unified_vol2press_and_peak_pressure_across_trials(folder_path,
                                                           freq_str: str,
                                                           transducer_serial: str
                                                           ) -> float:
    # List all the files in the folder with .hdf5 extension
    file_list = [f for f in os.listdir(folder_path) if f.endswith('.hdf5')]

    for i in range(len(file_list)):
        file_list[i] = os.path.join(folder_path, file_list[i])

    sweep_list = []

    for file in file_list:
        # Skip the file if it does not match the expected format
        if freq_str not in file:
            continue
        elif transducer_serial not in file:
            continue
        elif 'sweep' not in file:
            continue
        elif not os.path.isfile(os.path.join(folder_path, file)):
            continue

        sweep_list.append(file)

    if len(sweep_list) == 0:
        print(f"Error: No sweep files found in folder {folder_path}")
        return 0

    PNP_MPa = get_pnp_from_files(sweep_list)

    if not isinstance(PNP_MPa, float):
        print(f"Error: peak_pressure_MPa is not a float: {PNP_MPa}")

    return PNP_MPa


def _get_peak_pressure_MPa_by_cycle(folder_path, freq_str: str, transducer_serial: str):
    # List all the files in the folder with .hdf5 extension
    folder_list = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

    # Initialize a numpy array with NaN values matching the number of subfolders
    PNP_MPa_ray = np.full(len(folder_list), np.nan)
    for folder in folder_list:
        if '_cycles' in folder:
            # try:
            num_cycles = int(folder.split('_')[0])
            PNP_MPa = _get_unified_vol2press_and_peak_pressure_across_trials(os.path.join(folder_path,
                                                                                             folder),
                                                                                freq_str,
                                                                                transducer_serial)
            PNP_MPa_ray[num_cycles - 1] = PNP_MPa
            # except Exception as e:
            #     print(f"Error processing ncycle sweep data in folder {folder}: {e}")
            #     continue

    # Trim remaining NaN values at the end of the array (caused by folders that do not contain cycle sweep data)
    trailing_nan_count = 0
    for i in range(len(PNP_MPa_ray) - 1, -1, -1):
        if np.isnan(PNP_MPa_ray[i]):
            trailing_nan_count += 1
        else:
            break

    if trailing_nan_count > 0:
        PNP_MPa_ray = PNP_MPa_ray[:-trailing_nan_count]
    return PNP_MPa_ray


def _parse_info_from_ncycle_sweep_directory(results_directory: str,
                                            transducer_sn: Union[str, None] = None) -> Tuple[str, List[str], List[str]]:
    """
    Return:
    transducer_sn: str
        The serial number of the transducer
    freq_strs: List[str]
        A list of frequency strings found in the folder names, e.g. ['1.65MHz', '550kHz']
    ncycle_sweep_subfolders: List[str]
        A list of subfolder paths that contain ncycle sweep data
        e.g. ["C:<path_to_file>\\612_T550H825_sweep_550kHz_ncycle_sweep_data",
              "C:<path_to_file>\\612_T550H825_sweep_1650kHz_ncycle_sweep_data"]
    """
    subfolders = [f.path for f in os.scandir(results_directory) if f.is_dir()]
    ncycle_sweep_subfolders = []
    freq_strs = []

    for subfolder in subfolders:
        if "ncycle_sweep" in subfolder:
            ncycle_sweep_subfolders.append(subfolder)
            split_folder_name = os.path.basename(subfolder).split("_")

            # Get the transducer serial if it was not provided explicitly
            if transducer_sn is None and len(split_folder_name) >= 2:
                transducer_sn = f"{split_folder_name[0]}_{split_folder_name[1]}"

            freq_str = 'unknown_frequency'  # Placeholder for if the filename does not contain 'Hz' (not case-sensitive)
            for item in split_folder_name:
                if "Hz".upper() in item.upper():
                    freq_str = item

            if freq_str == 'unknown_frequency':
                print(f"Warning: Could not find frequency in folder name {subfolder}")

            freq_strs.append(freq_str)

    if transducer_sn is None:
        # Case where transducer SN was not given and was not found based on the filename
        transducer_sn = 'unknown_transducer'

    return transducer_sn, freq_strs, ncycle_sweep_subfolders


def add_ncycle_sweep_to_transducer_file(results_directory: str, transducer_config_file: str
                                        ) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Adds data to the transducer config file for each frequency at which ncycle sweep data was collected, containing
    data for how to derate pressure for low numbers of cycles.

    A list of floats will be added to keys such as 612-T550H825\\550000.0\\normalized_pnp_by_num_cycles
    containing the normalized peak pressure for each cycle count. The final value of the lists should be 1, since the
    values should be normalized to the greatest number of cycles.

    :param results_directory, A directory containing ncycle sweep data for one or more frequencies for a given
    transducer. The structure of this directory should be as follows:
    Top level: one or more directories of format like
    "...\\612_T550H825_sweep_550kHz_ncycle_sweep_data"
    Subfolders:
    "1_cycles", "2_cycles", "3_cycles", etc. containing the ncycle sweep data for that number of cycles
    containing one or more files like:
    "612_T550H825_sweep_550kHz_ncycle_sweep_data\\1_cycles\\612_T550H825_sweep_550kHz_01.hdf5"
    with a certain number of trials per cycle count (the extension)

    :param transducer_config_file: The path to the transducer config file to be updated. If none, no data will be saved
    :return: ncycle_axis: list of (np.ndarray, np.ndarray), where each item is a tuple consisting of:
    The frequency in Hz (ex: 550000 for 550kHz)
    The x-axis for the number of cycles, e.g. [1, 2, 3, ...]
    normalized_PNP_MPa_by_cycle: np.ndarray
    A list of floats containing the normalized peak pressure for each cycle count. The final value of the lists
    Note: Keys such as 612-T550H825\\550000.0\\normalized_pnp_by_num_cycles will be added or overwritten.
    """
    transducer_sn, freq_strs, ncycle_sweep_subfolders = _parse_info_from_ncycle_sweep_directory(results_directory)
    yaml_dict = yaml.load(open(transducer_config_file), Loader=yaml.FullLoader)
    plot_data = []

    for freq_str, ncycle_sweep_subfolder in zip(freq_strs, ncycle_sweep_subfolders):
        PNP_MPa_by_cycle = _get_peak_pressure_MPa_by_cycle(ncycle_sweep_subfolder,
                                                           freq_str,
                                                           transducer_sn)

        # Normalize peak pressure to the standard peak pressure to the last value in the list
        normalized_PNP_MPa_by_cycle = [x / PNP_MPa_by_cycle[-1] for x in PNP_MPa_by_cycle]
        print(f"Normalized sensitivity by cycle for frequency: {freq_str}")
        for i in range(len(PNP_MPa_by_cycle)):
            print(f"{normalized_PNP_MPa_by_cycle[i]}")

        if 'kHz' in freq_str:
            freq_int = int(freq_str.split('kHz')[0]) * 1000
        elif 'MHz' in freq_str:
            freq_int = int(freq_str.split('MHz')[0]) * 1000000
        else:
            raise Exception(f"Frequency string {freq_str} does not contain 'kHz' or 'MHz'")

        key1 = list(yaml_dict.keys())[0]
        frequency_key_found = False
        for key2 in yaml_dict[key1]:
            if str(freq_int) in str(key2):
                if isinstance(normalized_PNP_MPa_by_cycle, np.ndarray):
                    normalized_PNP_MPa_by_cycle = normalized_PNP_MPa_by_cycle.tolist()
                normalized_PNP_MPa_by_cycle = [float(x) for x in normalized_PNP_MPa_by_cycle]
                ncycle_axis = np.arange(1, len(normalized_PNP_MPa_by_cycle) + 1)
                plot_data.append((freq_int, ncycle_axis, np.array(normalized_PNP_MPa_by_cycle)))
                yaml_dict[key1][key2]['vol2press_adjustment_by_num_cycles'] = normalized_PNP_MPa_by_cycle
                frequency_key_found = True
                break
        if not frequency_key_found:
            print(f"Warning: Did not find frequency key for {freq_int} in the transducer config file.")

    with open(transducer_config_file, 'w') as file:
        yaml.dump(yaml_dict, file)

    return plot_data


def run_example():
    # Example usage. Ncycle adjustment data will be added to the transducer config file.
    results_dir = (r"G:\\Shared drives\\FUS_Team\\Transducers Calibration and RFB\\612-T550H825_DUAL_FREQUENCY\\Scan Data\\Cycle_sweeps_Feb_20")
    tx_config = (r"G:\\Shared drives\\FUS_Team\\Transducers Calibration and "
                r"RFB\\612-T550H825_DUAL_FREQUENCY\\612-T550H825_DUAL_FREQUENCY - Copy.yaml")
    plot_data = add_ncycle_sweep_to_transducer_file(results_dir, tx_config)
    for (frequency_Hz, ncycle_axis, normalized_PNP_MPa_by_cycle) in plot_data:
        print(f"Frequency: {frequency_Hz}")
        print(f"ncycle_axis: {ncycle_axis}")
        print(f"normalized_PNP_MPa_by_cycle: {normalized_PNP_MPa_by_cycle}")


if __name__ == '__main__':
    run_example()

