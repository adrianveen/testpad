from pathlib import Path

import h5py
import numpy as np
import yaml


def get_pnp_from_files(sweep_files: list[str]) -> float:
    """Get the minimum pressure from a list of sweep files.

    Args:
        sweep_files (list[str]): A list of paths to sweep files.

    Returns:
        float: The minimum pressure in MPa.

    """
    for file in sweep_files:
        min_MPa_hdf5_per_file = []

        with h5py.File(file, "r") as f:
            min_Pa_hdf5 = f["/Scan/Min output pressure (Pa)"]
            min_MPa_hdf5_per_file.append(np.min(np.multiply(min_Pa_hdf5, 1e-6)))

        # Convert to numpy array and average across trials
        min_MPa_hdf5_per_file = np.min(np.mean(min_MPa_hdf5_per_file, axis=0))
    return float(
        np.abs(np.min(min_MPa_hdf5_per_file))
    )  # Return the maximum value across trials


def _get_unified_vol2press_and_peak_pressure_across_trials(
    folder_path: str, freq_str: str, transducer_serial: str
) -> float:
    # List all the files in the folder with .hdf5 extension
    folder = Path(folder_path)
    file_list = [str(f) for f in folder.iterdir() if f.suffix == ".hdf5"]

    sweep_list = []

    for file in file_list:
        file_path = Path(file)
        # Skip the file if it does not match the expected format
        if (
            freq_str not in file
            or transducer_serial not in file
            or "sweep" not in file
            or not file_path.is_file()
        ):
            continue

        sweep_list.append(file)

    if len(sweep_list) == 0:
        print(f"Error: No sweep files found in folder {folder_path}")
        return 0

    PNP_MPa = get_pnp_from_files(sweep_list)

    if not isinstance(PNP_MPa, float):
        print(f"Error: peak_pressure_MPa is not a float: {PNP_MPa}")

    return PNP_MPa


def _get_peak_pressure_MPa_by_cycle(
    folder_path: str, freq_str: str, transducer_serial: str
) -> list:
    # List all the directories in the folder
    folder_base = Path(folder_path)
    folder_list = [f.name for f in folder_base.iterdir() if f.is_dir()]

    # Initialize a numpy array with NaN values matching the number of subfolders
    PNP_MPa_ray = np.full(len(folder_list), np.nan)
    for folder in folder_list:
        if "_cycles" in folder:
            # try:
            num_cycles = int(folder.split("_")[0])
            PNP_MPa = _get_unified_vol2press_and_peak_pressure_across_trials(
                str(folder_base / folder), freq_str, transducer_serial
            )
            PNP_MPa_ray[num_cycles - 1] = PNP_MPa
            # except Exception as e:
            #     print(f"Error processing ncycle sweep data in folder {folder}: {e}")
            #     continue

    # Trim remaining NaN values at the end of the array (caused by folders that do not
    # contain cycle sweep data)
    trailing_nan_count = 0
    for i in range(len(PNP_MPa_ray) - 1, -1, -1):
        if np.isnan(PNP_MPa_ray[i]):
            trailing_nan_count += 1
        else:
            break

    if trailing_nan_count > 0:
        PNP_MPa_ray = PNP_MPa_ray[:-trailing_nan_count]
    return PNP_MPa_ray


def _parse_info_from_ncycle_sweep_directory(
    results_directory: str, transducer_sn: str | None = None
) -> tuple[str, list[str], list[str]]:
    r"""Return transducer serial number, frequency strings, and ncycle sweep subfolders.

    Args:
        results_directory (str): The directory containing ncycle sweep data for one or
            more frequencies for a given transducer. The structure of this directory
            should be as follows:
                Top level: one or more directories of format like
                "...\612_T550H825_sweep_550kHz_ncycle_sweep_data"
                Subfolders:
                "1_cycles", "2_cycles", "3_cycles", etc. containing the ncycle sweep
                    data for that number of cycles containing one or more files like:
                    "612_T550H825_sweep_550kHz_ncycle_sweep_data\1_cycles\612_T550H825_sweep_550kHz_01.hdf5"
                    with a certain number of trials per cycle count (the extension).
        transducer_sn (str, optional): The serial number of the transducer. If None, it
            will be extracted from the filename of the first subfolder in the results

    Returns:
        tuple: A tuple containing the transducer serial number, frequency strings, and
            ncycle sweep subfolders.

    """
    results_path = Path(results_directory)
    subfolders = [str(f) for f in results_path.iterdir() if f.is_dir()]
    ncycle_sweep_subfolders = []
    freq_strs = []

    for subfolder in subfolders:
        if "ncycle_sweep" in subfolder:
            ncycle_sweep_subfolders.append(subfolder)
            split_folder_name = Path(subfolder).name.split("_")

            # Get the transducer serial if it was not provided explicitly
            if transducer_sn is None and len(split_folder_name) >= 2:
                transducer_sn = f"{split_folder_name[0]}_{split_folder_name[1]}"

            # Placeholder for if the filename does not contain 'Hz' (not case-sensitive)
            freq_str = "unknown_frequency"
            for item in split_folder_name:
                if "Hz".upper() in item.upper():
                    freq_str = item

            if freq_str == "unknown_frequency":
                print(f"Warning: Could not find frequency in folder name {subfolder}")

            freq_strs.append(freq_str)

    if transducer_sn is None:
        # Case where transducer SN was not given and was not found based on the filename
        transducer_sn = "unknown_transducer"

    return transducer_sn, freq_strs, ncycle_sweep_subfolders


def add_ncycle_sweep_to_transducer_file(
    results_directory: str, transducer_config_file: str
) -> list[tuple[np.ndarray, np.ndarray]]:
    r"""Add data to the transducer config file.

    for each frequency at which ncycle sweep data was collected, containing data for how
        to derate pressure for low numbers of cycles.

    A list of floats will be added to keys such as
        612-T550H825\\550000.0\\normalized_pnp_by_num_cycles
    containing the normalized peak pressure for each cycle count. The final value of the
        lists should be 1, since the values should be normalized to the greatest number
        of cycles.

    :param results_directory, A directory containing ncycle sweep data for one or more
        frequencies for a given
    transducer. The structure of this directory should be as follows:
    Top level: one or more directories of format like
    "...\\612_T550H825_sweep_550kHz_ncycle_sweep_data"
    Subfolders:
    "1_cycles", "2_cycles", "3_cycles", etc. containing the ncycle sweep data for that
        number of cycles
    containing one or more files like:
    "612_T550H825_sweep_550kHz_ncycle_sweep_data\\1_cycles\\612_T550H825_sweep_550kHz_01.hdf5"
    with a certain number of trials per cycle count (the extension)

    :param transducer_config_file: The path to the transducer config file to be updated.
        If none, no data will be saved
    :return: ncycle_axis: list of (np.ndarray, np.ndarray), where each item is a tuple
        consisting of:
    The frequency in Hz (ex: 550000 for 550kHz)
    The x-axis for the number of cycles, e.g. [1, 2, 3, ...]
    normalized_PNP_MPa_by_cycle: np.ndarray
    A list of floats containing the normalized peak pressure for each cycle count.
        The final value of the lists
    Note: Keys such as 612-T550H825\\550000.0\\normalized_pnp_by_num_cycles
        will be added or overwritten.
    """
    transducer_sn, freq_strs, ncycle_sweep_subfolders = (
        _parse_info_from_ncycle_sweep_directory(results_directory)
    )
    yaml_dict = yaml.load(Path(transducer_config_file).open(), Loader=yaml.FullLoader)
    plot_data = []

    for freq_str, ncycle_sweep_subfolder in zip(
        freq_strs, ncycle_sweep_subfolders, strict=False
    ):
        PNP_MPa_by_cycle = _get_peak_pressure_MPa_by_cycle(
            ncycle_sweep_subfolder, freq_str, transducer_sn
        )

        # Normalize peak pressure to the standard peak pressure to the last value in the
        # list
        normalized_PNP_MPa_by_cycle = [
            x / PNP_MPa_by_cycle[-1] for x in PNP_MPa_by_cycle
        ]
        print(f"Normalized sensitivity by cycle for frequency: {freq_str}")
        for i in range(len(PNP_MPa_by_cycle)):
            print(f"{normalized_PNP_MPa_by_cycle[i]}")

        if "kHz" in freq_str:
            freq_int = int(freq_str.split("kHz")[0]) * 1000
        elif "MHz" in freq_str:
            freq_int = int(freq_str.split("MHz")[0]) * 1000000
        else:
            msg = f"Frequency string {freq_str} does not contain 'kHz' or 'MHz'"
            raise Exception(msg)

        key1 = next(iter(yaml_dict.keys()))
        frequency_key_found = False
        for key2 in yaml_dict[key1]:
            if str(freq_int) in str(key2):
                if isinstance(normalized_PNP_MPa_by_cycle, np.ndarray):
                    normalized_PNP_MPa_by_cycle = normalized_PNP_MPa_by_cycle.tolist()
                normalized_PNP_MPa_by_cycle = [
                    float(x) for x in normalized_PNP_MPa_by_cycle
                ]
                ncycle_axis = np.arange(1, len(normalized_PNP_MPa_by_cycle) + 1)
                plot_data.append(
                    (freq_int, ncycle_axis, np.array(normalized_PNP_MPa_by_cycle))
                )
                yaml_dict[key1][key2]["vol2press_adjustment_by_num_cycles"] = (
                    normalized_PNP_MPa_by_cycle
                )
                frequency_key_found = True
                break
        if not frequency_key_found:
            print(
                f"Warning: Did not find frequency key for {freq_int} "
                f"in the transducer config file."
            )

    with Path(transducer_config_file).open("w") as file:
        yaml.dump(yaml_dict, file)

    return plot_data


def run_example() -> None:
    # Example usage. Ncycle adjustment data added to the transducer config file.
    results_dir = (
        r"G:\\Shared drives\\FUS_Team\\Transducers Calibration and RFB"
        r"\\612-T550H825_DUAL_FREQUENCY\\Scan Data\\Cycle_sweeps_Feb_20"
    )
    tx_config = (
        r"G:\\Shared drives\\FUS_Team\\Transducers Calibration and "
        r"RFB\\612-T550H825_DUAL_FREQUENCY\\612-T550H825_DUAL_FREQUENCY - Copy.yaml"
    )
    plot_data = add_ncycle_sweep_to_transducer_file(results_dir, tx_config)
    for frequency_Hz, ncycle_axis, normalized_PNP_MPa_by_cycle in plot_data:
        print(f"Frequency: {frequency_Hz}")
        print(f"ncycle_axis: {ncycle_axis}")
        print(f"normalized_PNP_MPa_by_cycle: {normalized_PNP_MPa_by_cycle}")


if __name__ == "__main__":
    run_example()
