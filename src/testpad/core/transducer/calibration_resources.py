import re
from pathlib import Path

import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from PySide6.QtWidgets import QTextBrowser
from scipy.interpolate import RegularGridInterpolator, interp1d

from testpad.core.transducer.calibration_figure_2 import SweepGraph
from testpad.core.transducer.cm_data import cm_data

# PARULA MAP! (list of colormap data is in separate file)
parula_map = LinearSegmentedColormap.from_list("parula", cm_data)

# SOME STYLISTIC DEFAULTS
style_1 = {
    # 'font.size': 22,
    "font.family": "calibri",
    "grid.color": "gainsboro",
    "axes.labelsize": 20,  # change to 20?
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    # 'savefig.dpi': 960,
    # 'xtick.minor.pad': 20,
    "axes.labelpad": 10,
    # 'font.weight': 'light'
    # 'xtick.major.pad'
}

"""
EB-50 METHODS COPIED FROM UNIFIED CALIBRATION RESOURCES
"""


# find the closest frequency to the requested frequency (parsing YAML file)
def closest_frequency(
    frequency: float, filename: str | Path, textbox: QTextBrowser
) -> tuple[str, dict]:
    """Find the closest frequency to the requested frequency.

    Args:
        frequency (float): The requested frequency.
        filename (str | Path): The path to the EB-50 file.
        textbox (QTextBrowser): The text box to which to write any errors or warnings.

    Returns:
        tuple: A tuple containing the closest frequency and the EB-50 dictionary.

    """
    # requested frequency
    frequency, ending = fmt(frequency)
    textbox.append("Requested frequency: " + str(frequency) + ending)

    # opens the eb50 file to get the frequencies
    with Path(filename).open() as file:
        lines = yaml.safe_load(file)

    # find closest frequency (can later be changed into interpolation of two
    # frequencies)
    frequencies = list(
        lines["frequencies"].keys()
    )  # for all the frequencies in the eb50 file
    for i in range(len(frequencies)):
        frequencies[i] = float(frequencies[i][:-3])

    closest_frequency = (
        str(find_nearest(frequencies, float(frequency))) + ending
    )  # closest frequency to requested frequency
    textbox.append("Closest frequency in EB-50 file: " + closest_frequency)

    eb50_dict = lines["frequencies"][
        closest_frequency
    ]  # fetch the eb-50 data for the closest frequency

    return (closest_frequency, eb50_dict)


# find number in array closest to value
def find_nearest(array: list | np.ndarray, value: float) -> np.floating:
    """Find the number in an array closest to a given value.

    Args:
        array (list | np.ndarray): The array to search.
        value (float): The value to find.

    Returns:
        np.floating: The number in the array closest to the given value.

    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


# convert Hz to kHz, MHz
def fmt(freq: float) -> tuple[float, str]:
    """Convert a frequency from Hz to kHz or MHz.

    Args:
        freq (float): The frequency to convert.

    Returns:
        tuple: A tuple containing the converted frequency and the frequency unit.

    """
    SI_Frequency = [(1, "kHz"), (1000, "MHz")]
    useFactor, useName = SI_Frequency[0]
    for factor, name in SI_Frequency:
        if freq >= factor:
            useFactor, useName = factor, name
    return freq / useFactor, useName


def _split_array(data_mtx: list[str], col1: int) -> np.ndarray:
    array1 = np.array([])

    for i in range(len(data_mtx)):
        line = data_mtx[i].split(" ")
        array1 = np.append(array1, float(line[col1]))

    return array1


# extracts eb50 data, returns eb50 dictionary
def eb50_dictionary(closest_frequency: str, filename: Path) -> dict:
    # start_time = timeit.default_timer()
    """Extract the eb50 data from a .txt file given the closest frequency.

    Args:
        closest_frequency : str
            The closest frequency to the requested frequency, in Hz, kHz, or MHz.
        filename : Path
            The path to the .txt file containing the eb50 data.

    Returns:
        dict : A dictionary containing the relevant data from the .txt file, including
            the amplitude, input power, output power, output voltage, power gain, and
            voltage gain. If the resistance is not 50 ohms, the output voltage will be
            incorrect.

    """
    with filename.open() as file:  # file for input power
        lines = file.readlines()
    indices = [
        i for i, x in enumerate(lines) if x == "#\n"
    ]  # find the indices of all the line endings

    # extract the relevant data and store it as a list
    first_index = -1  # Initialize to avoid unbound variable
    for line in lines:
        if closest_frequency in line:
            first_index = lines.index(line)  # find the index of the requested frequency
            break

    if first_index == -1:
        msg = f"Frequency '{closest_frequency}' not found in file"
        raise ValueError(msg)

    last_index = indices[
        next(x[0] for x in enumerate(indices) if x[1] >= first_index)
    ]  # find the last line of relevant data
    eb50_data = lines[
        (first_index + 2) : last_index
    ]  # this is the relevant data from the .txt for the
    # aforementioned frequency
    # print(data)

    input_power = _split_array(eb50_data, 1)
    output_power = _split_array(eb50_data, 2)
    amplitude = _split_array(eb50_data, 0)
    output_voltage = np.sqrt(8 * output_power * 50)

    return {
        "all data": eb50_data,
        "amplitudes": amplitude,
        "input power": input_power,
        "output power": output_power,
        "output voltage": output_voltage,  # assuming the resistance is 50 ohms
        "power gain": 10 * np.log10(output_power / input_power),  # power gain
        "gain": 20 * np.log10(output_voltage / amplitude),  # voltage gain
        # "interpolated input power": interpolate.interp1d(output_power,
        # input_power, fill_value="extrapolate"),
        # "interpolated output power": interpolate.interp1d(input_power,
        # output_power, fill_value="extrapolate")
    }

    # print("Time for eb50 data extraction: ", end='')
    # print(timeit.default_timer() - start_time)


"""
UTILITY METHODS
"""


# fetch data for axial/lateral scan graphs
def fetch_data(
    filename: str | Path, axial_or_lateral: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list | None]:
    """Fetch data from a .h5 file.

    Args:
        filename (str | Path): The path to the .h5 file.
        axial_or_lateral (str): The type of scan (axial or lateral).

    Returns:
        tuple: A tuple containing the x, y, z, pressure, intensity, and pointer location
            arrays.

    """
    # full_filename = os.path.join(folder, filename)

    with h5py.File(filename, "r") as f:
        pressure_hdf5 = f["/Scan/Min Pressure (Pa)"]  # pressure
        pressure = np.zeros(pressure_hdf5.shape)
        pressure_hdf5.read_direct(pressure)
        # pressure.reshape(-1, pressure.shape[-1])

        x_data_hdf5 = f["/Scan/X coordinate array (mm)"]  # x values
        x_data = np.zeros(x_data_hdf5.shape)
        x_data_hdf5.read_direct(x_data)

        y_data_hdf5 = f["/Scan/Y coordinate array (mm)"]  # y values
        y_data = np.zeros(y_data_hdf5.shape)
        y_data_hdf5.read_direct(y_data)

        z_data_hdf5 = f["/Scan/Z coordinate array (mm)"]  # z values
        z_data = np.zeros(z_data_hdf5.shape)
        z_data_hdf5.read_direct(z_data)

        if axial_or_lateral == "axial":
            # reshape pressure array to fit y and z
            pressure = np.reshape(
                pressure, (y_data_hdf5.shape[0], z_data_hdf5.shape[0])
            )
        else:
            # reshape pressure array to fit x and z
            pressure = np.reshape(
                pressure, (x_data_hdf5.shape[0], z_data_hdf5.shape[0])
            )
        pressure = np.abs(pressure)
        intensity = pressure**2

    with h5py.File(filename, "r") as f:
        try:
            pointer_location = list(f["Scan"]["Pointer location"])
        except KeyError:
            pointer_location = None

    return x_data, y_data, z_data, pressure, intensity, pointer_location


def fwhmx(
    horizontal: np.ndarray,
    pressure_or_intensity: np.ndarray,
    left_field_length: float,
    right_field_length: float,
    axis: str,
    type_of_scan: str,
    type_of_data: str,
    textbox: QTextBrowser,
) -> tuple[float | str, float]:
    """FWHMX CALCULATION.

    Args:
        horizontal: horizontal array
        pressure_or_intensity: pressure or intensity array
        left_field_length: left field length
        right_field_length: right field length
        axis: axis of scan
        type_of_scan: axial or lateral
        type_of_data: pressure or intensity
        textbox: QTextBrowser

    Returns:
        Full width half max in mm (or error string), offset (or zero if error).

    """
    minimum = pressure_or_intensity.min()
    maximum = pressure_or_intensity.max()

    norm_pressure = np.divide(
        pressure_or_intensity, maximum
    )  # normalisation of pressure to 1 and below
    maximum_location = np.where(
        norm_pressure == 1.0
    )  # where is the maximum pressure value?
    # which curve (column) does the maximum pressure value belong to in the
    # norm_pressure array?
    max_curve = maximum_location[1][0]

    new_pressure_or_intensity = []  # list for isolating the maximum pressure curve

    # for loop to isolate the maximum pressure curve
    new_pressure_or_intensity = [
        norm_pressure[i][max_curve] for i in range(len(pressure_or_intensity))
    ]

    new_pressure_or_intensity = np.array(
        new_pressure_or_intensity
    )  # convert list to numpy array

    # INTERPOLATED
    # x = np.arange(np.min(horizontal), (np.max(horizontal)+interp_step), interp_step)
    # new x array to interpolate over
    # y = np.interp(x, horizontal, new_pressure_or_intensity)
    # interpolated pressure/intensity array

    # NONINTERPOLATED
    x = horizontal
    y = new_pressure_or_intensity

    """
    THE MULTIPLE PEAK PROBLEM (to address graphs with multiple peaks)
    """
    # THE INTERSECTION METHOD
    half_max_line = np.zeros(x.shape)
    half_max_line.fill(0.5)
    indices = np.argwhere(np.diff(np.sign(y - half_max_line))).flatten()
    max_location = np.argwhere(y == 1)[0][0]  # position of peak
    try:
        first_index = x[indices[np.argwhere(indices < max_location)[-1]]][
            0
        ]  # first intersection with half_max_line, to the left of the peak
        last_index = x[indices[np.argwhere(indices > max_location)[0]]][
            0
        ]  # last intersection with half_max_line, to the right of the peak
    except IndexError as e:
        textbox.append(f"{e}: couldn't output fwhmx")
        return (str(e)), 0
    # print("Intersection", indices)

    # THE FOV METHOD (OBSOLETE)
    # idx = np.argwhere(y >= 0.5) # indices of values where y is bigger than 0.5
    # # print("FOV:", idx[0], idx[-1])
    # idx = idx[x[idx] >= left_field_length] # limits the first index to be greater than
    # the left field length (in case there are multiple peaks)
    # idx = idx[x[idx] <= right_field_length] # limits the last index to be greater than
    # the right field length
    # # # print(x[idx])
    # first_index = x[idx[0]] # first x-coordinate where the 0.5 line is crossed
    # last_index = x[idx[-1]] # last x-coordinate where the 0.5 line is crossed

    fwhmx = last_index - first_index  # FWHMX calculation
    # print(axis, type_of_scan+type_of_data+':', '{0:.1f}'.format(last_index),
    # "-", '{0:.1f}'.format(first_index), "=", '{0:.1f}'.format(fwhmx)+'\n')
    # print statements for testing purposes

    offset = (first_index + last_index) / 2
    return fwhmx, offset


"""
FILE CREATION METHODS
"""


# sweep file creation, returns an averaged file of all sweeps
def create_sweep_file(
    sweep_list: list[str],
    save_folder: str,
    transducer: str,
    freq: str,
    save: bool,
    eb50_file: str = "",
    textbox: QTextBrowser | None = None,
) -> None | tuple[()] | FigureCanvas:
    """Create a sweep file.

    Args:
        sweep_list (list[str]): A list of paths to the sweep files.
        save_folder (str): The path to the folder where the sweep file should be saved.
        transducer (str): The transducer serial number.
        freq (str): The frequency of the sweep.
        save (bool): Whether to save the sweep file.
        eb50_file (str, optional): The path to the EB-50 file. Defaults to "".
        textbox (QTextBrowser | None, optional): The text box to which to write any
            errors or warnings. Defaults to None.

    Returns:
        None | tuple[()] | FigureCanvas: None if save is False, otherwise a tuple
            containing the sweep file path and a FigureCanvas object.

    """
    if eb50_file is None:
        eb50_file = ""
    # filename = os.path.join(folder, sweep_filename)
    original_freq = freq  # preserve original frequency for file name purposes
    number_freq = float(
        re.sub("[^0-9.]", "", freq)
    )  # find the frequency without the kHz/MHz ending
    eb50_dict: dict = {}  # Initialize to avoid unbound variable
    if eb50_file != "" and textbox is not None:
        freq, eb50_dict = closest_frequency(number_freq, eb50_file, textbox)

    fn_gen_amplitudes = []  # amplitudes in each file
    pressures = []  # pressures in each file
    powers = []
    ref_powers = []

    for sweep_filename in sweep_list:
        with h5py.File(sweep_filename, "r") as f:
            input_mV_hdf5 = f["/Scan/Input voltage amplitude (mV)"]
            input_mV = np.zeros(input_mV_hdf5.shape)
            input_mV_hdf5.read_direct(input_mV)

            v_in = input_mV * 1e-3  # mV to V

            # try-catch to deal with old code that used MPa instead of Pa
            try:
                min_mV_hdf5 = f["/Scan/Min output pressure (MPa)"]
                min_mV = np.zeros(min_mV_hdf5.shape)
                min_mV_hdf5.read_direct(min_mV)
            except KeyError:
                min_mV_hdf5 = f["/Scan/Min output pressure (Pa)"]
                min_mV = np.zeros(min_mV_hdf5.shape)
                min_mV_hdf5.read_direct(min_mV)

            # try-catch to deal with old code that didn't have power readings in it
            try:
                fwd_pwr_hdf5 = f["Scan/Forward power meter readings (W)"]
                fwd_pwr = np.zeros(fwd_pwr_hdf5.shape)
                fwd_pwr_hdf5.read_direct(fwd_pwr)
                powers.append(fwd_pwr)
                if eb50_file != "" and textbox is not None:
                    textbox.append(
                        "\nUsing the power values in the sweep instead of inferring \
                            with the EB-50 YAML file.\n"
                    )
                    eb50_file = ""

                # Get the reflected power meter data, this is less important
                # so we can fill it with float(nan) if it is missing.
                # Only attempt this if we already got f meter data.
                try:
                    ref_pwr_hdf5 = f["Scan/Reverse power meter readings (W)"]
                    ref_pwr = np.zeros(ref_pwr_hdf5.shape)
                    ref_pwr_hdf5.read_direct(ref_pwr)
                    ref_powers.append(ref_pwr)
                except KeyError:
                    # Append a ndarray of nans equal in shape to fwd_pwr
                    print(
                        "Warning, fwd power found but not ref power in the "
                        "sweep file. This is unusual."
                    )
                    ref_powers.append(np.full(fwd_pwr.shape, np.nan))
            except KeyError as e:
                if textbox is not None:
                    textbox.append("KeyError: " + str(e))
                    if eb50_file == "":
                        textbox.append(
                            "WARNING: No power reading found in sweep file. "
                            "Please enter an EB-50 file.\n"
                        )
                        return None
                    textbox.append(
                        "No power reading found in sweep file - switching to "
                        "EB-50 file for power inference.\n"
                    )

            neg_pressure = np.multiply(abs(min_mV), 1e-6)  # Pa to MPa
            # print(neg_pressure)
            pressures.append(neg_pressure)  # add the pressure to the list of pressures
            fn_gen_amplitudes.append(
                v_in
            )  # add the amplitude to the list of amplitudes

    # list of pressures bundled up into an array of tuples with EQUAL length
    pressures = list(zip(*pressures, strict=False))
    # print(len(pressures))
    pressure_list_to_array = np.zeros(
        (len(pressures), len(pressures[0]))
    )  # x dimensions: rows of pressures, y dimensions: columns of pressures
    for i in range(len(pressures[0])):
        pressure_list_to_array[:, i] = np.array(
            [x[i] for x in pressures]
        )  # convert the tuple columns to numpy arrays

    # find the average pressure
    averaged_pressures = np.average(pressure_list_to_array, axis=1)

    # list of amplitudes bundled up into an array of tuples with EQUAL length
    fn_gen_amplitudes = list(zip(*fn_gen_amplitudes, strict=False))
    fn_gen_amplitudes_list_to_array = np.zeros(
        (len(fn_gen_amplitudes), len(fn_gen_amplitudes[0]))
    )  # x dimensions: rows of pressures, y dimensions: columns of pressures
    for i in range(len(fn_gen_amplitudes[0])):
        fn_gen_amplitudes_list_to_array[:, i] = np.array(
            [x[i] for x in fn_gen_amplitudes]
        )  # convert the tuple columns to numpy arrays

    # find the average amplitudes
    averaged_fn_gen_amplitudes = np.average(fn_gen_amplitudes_list_to_array, axis=1)

    # if an EB-50 file exists:
    eb50 = ""  # Initialize to avoid unbound variable
    if eb50_file != "":
        # EB-50 GAINS
        raw_gain = eb50_dict["gain"]
        interpolated_gain = interp1d(
            eb50_dict["amplitudes"],
            raw_gain,
            fill_value="extrapolate",
            kind="linear",  # type: ignore[arg-type]
        )  # interpolate the gain
        # v_in = averaged_fn_gen_amplitudes * 1e-3  # in Vpp
        gain_EB50 = interpolated_gain(averaged_fn_gen_amplitudes)
        v_out = averaged_fn_gen_amplitudes * (10 ** (gain_EB50 / 20.0))
        fwd_pwr = v_out**2 / 8.0 / 50.0  # electrical power
        ref_pwr = np.full(len(averaged_pressures), np.nan)  # No ref power from EB-50
        eb50 = eb50_file.split("/")[-1]
        # EB-50 sanity test graph
        # data_mtx_2 = np.zeros((len(averaged_pressures), 4))
    # otherwise, take the power directly from the files
    else:
        # print("hello")
        powers = list(zip(*powers, strict=False))
        # print(len(powers))
        powers_list_to_array = np.zeros(
            (len(powers), len(powers[0]))
        )  # x dimensions: rows of pressures, y dimensions: columns of pressures
        # print(len(powers[0]))
        for i in range(len(powers[0])):
            powers_list_to_array[:, i] = np.array(
                [x[i] for x in powers]
            )  # convert the tuple columns to numpy arrays

        # find the average amplitudes
        averaged_powers = np.average(powers_list_to_array, axis=1)
        fwd_pwr = averaged_powers
        # print(averaged_powers)
        # print(averaged_powers.shape)
        v_out = np.sqrt(fwd_pwr * 8 * 50)
        # print(v_out.shape)

        try:
            # Repeat this process for reflected power (except the vout)
            ref_powers = list(zip(*ref_powers, strict=False))
            ref_powers_list_to_array = np.zeros((len(ref_powers), len(ref_powers[0])))
            for i in range(len(ref_powers[0])):
                ref_powers_list_to_array[:, i] = np.array([x[i] for x in ref_powers])
            averaged_ref_powers = np.average(ref_powers_list_to_array, axis=1)
            ref_pwr = averaged_ref_powers
        except (ValueError, TypeError, IndexError) as e:
            print("Error averaging reflected power data across files:", e)
            ref_pwr = np.full(fwd_pwr.shape, np.nan)

    """
    Write to file
    """
    data_mtx = np.zeros((len(averaged_pressures), 5))

    try:
        data_mtx[:, 0] = averaged_pressures  # pnp
        data_mtx[:, 1] = v_out  # voltage across transducer
        data_mtx[:, 2] = fwd_pwr  # electrical power
        data_mtx[:, 3] = (
            averaged_fn_gen_amplitudes  # amplitudes from function generator
        )
        data_mtx[:, 4] = ref_pwr  # reflected power
    except ValueError as e:
        if textbox is not None:
            textbox.append("\nValueError: " + str(e))
            textbox.append(
                "\nThe sizes of the data are incompatible with each other. "
                "Did you select sweep files from the same batch? "
                "Does one of your files have an error in it?"
            )
        return ()

    # set the marker size of the sweep graph
    if number_freq < 1000 and number_freq >= 500:  # less than 1000 kHz
        markersize = 4
    elif number_freq < 500:
        markersize = 3
    else:
        markersize = 6

    # generate sweep graph using Marc's program
    sweep_freq, sweep_freq_ending = fmt(number_freq)
    if textbox is None:
        return None
    graph = SweepGraph(
        data_mtx,
        transducer,
        str(sweep_freq) + " " + sweep_freq_ending,
        save_folder,
        markersize,
        textbox,
    )
    returned_graph = graph.generate_graph()
    # graph.generate_graph()

    # get the m-value and the matlab r squared to put into the sweep file
    m = graph.m
    r_trunc_out = graph.r2_trunc_out

    # header array in the txt file, m-value rounded to 6 decimal places
    if eb50_file != "":  # if the EB-50 exists, add it to the header array
        header_arr = (
            f"Frequency: {original_freq}\nEB-50: {eb50}\n"
            f"m-value: {m:.6f} MPa/Vpp\nr squared: {r_trunc_out}\n\n"
            f"Peak Negative Pressure (MPa), Voltage Across the Transducer (Vpp), "
            f"Electrical Power (W), Input Voltage (Vpp), Reflected Power (W)"
        )
    else:
        header_arr = (
            f"Frequency: {original_freq}\nm-value: {m:.6f} MPa/Vpp\n"
            f"r squared: {r_trunc_out}\n\n"
            f"Peak Negative Pressure (MPa), Voltage Across the Transducer (Vpp), "
            f"Electrical Power (W), Input Voltage (Vpp), Reflected Power (W)"
        )

    # SAVE FILE
    if save:
        graph.save_graph()  # save the sweep graph from Marc's program

        counter = 1
        f = None  # Initialize to avoid unbound variable

        while True:
            try:
                filename = str(
                    Path(save_folder) / f"sweep_{transducer}_{original_freq}"
                )
                # DATA WITH HEADER ARRAY
                full_filename2 = filename + "_" + str(counter) + ".txt"
                with Path(full_filename2).open("x"):
                    np.savetxt(
                        full_filename2,
                        data_mtx,
                        header=header_arr,
                        comments="",
                        fmt="%.3f",
                        delimiter=",",
                    )

                # DATA TXT FILE
                # Remove reflected power column
                data_mtx = np.delete(data_mtx, 4, 1)
                # Remove input voltage column
                data_mtx = np.delete(data_mtx, 3, 1)
                full_filename1 = filename + "_DATA_" + str(counter) + ".txt"
                with Path(full_filename1).open("x"):
                    np.savetxt(full_filename1, data_mtx, fmt="%.3f", delimiter=",")

                break

            except FileExistsError:
                counter += 1
        # print(data_mtx)

        # print(f"\nSaving sweep to {full_filename1}...")
        # print(f"Saving sweep data to {full_filename2}...")

        if f is not None:
            f.close()

    return returned_graph


# field graph svg
@mpl.rc_context(style_1)  # use plot style style_1 above
def field_graph(
    horizontal: np.ndarray,
    vertical: np.ndarray,
    pressure_or_intensity: np.ndarray,
    left_field_length: float,
    right_field_length: float,
    field_height: float,
    name: str,
    type_of_scan: str,
    type_of_data: str,
    interp_step: float,
    save: bool,
    save_folder: str,
    textbox: QTextBrowser,
) -> FigureCanvas:
    """Generate a field graph (2D heatmap) for a given transducer at a given frequency.

    Args:
        horizontal : array-like
            The horizontal positions of the transducer at which the data was taken.
        vertical : array-like
            The vertical positions of the transducer at which the data was taken.
        pressure_or_intensity : array-like
            The pressure or intensity values at each position of the transducer.
        left_field_length : float
            The length of the field in the negative x direction.
        right_field_length : float
            The length of the field in the positive x direction.
        field_height : float
            The height of the field.
        name : str
            The name of the transducer.
        type_of_scan : str
            The type of scan (lateral or axial).
        type_of_data : str
            The type of data (pressure or intensity).
        interp_step : float
            The step size for interpolation in mm.
        save : bool
            If True, saves the field graph as an SVG file.
        save_folder : str
            The folder in which to save the field graph.
        textbox : QTextBrowser
            The text box to which to write any errors or warnings.

    Returns:
        FigureCanvas :
            The canvas object representing the figure.

    """
    fig1, ax1 = plt.subplots(1, 1)
    canvas = FigureCanvas(fig1)
    ax1.tick_params(
        axis="both", direction="in", pad=7
    )  # sets the ticks to be inside the plot frame and also adds padding space between
    # the axis and the tick labels
    # fig1.canvas.manager.set_window_title(name+"field_plot") # names window
    # fig1.set_size_inches(7, 4) # actual graph window size
    ax1.set_aspect("equal")  # makes 1:1 aspect ratio
    cmap = parula_map  # uses custom parula_map above

    """
    Interpolation testing grounds
    """
    # SCIPY METHOD (WORKING)

    # print(pressure_or_intensity.shape)
    # print(horizontal.shape)
    # print(vertical.shape)

    pressure_or_intensity = pressure_or_intensity / np.amax(pressure_or_intensity)
    # print(np.amax(pressure_or_intensity))
    interp = RegularGridInterpolator(
        (horizontal, vertical),
        pressure_or_intensity,
        bounds_error=False,
        fill_value=0.0,
        method="cubic",
    )  # interpolator method
    # interp = RectBivariateSpline(horizontal, vertical, pressure_or_intensity)

    # new arrays for interpolation
    x = np.array([])  # Initialize to avoid unbound variable
    y = np.array([])  # Initialize to avoid unbound variable
    try:
        x = np.arange(
            np.min(horizontal), (np.max(horizontal) + interp_step), interp_step
        )
        # print(x.shape)
        y = np.arange(np.min(vertical), (np.max(vertical) + interp_step), interp_step)
        # print(y.shape)
    except ValueError as e:
        textbox.append("ValueError: " + str(e))
        textbox.append("Did you enter an interpolation value?")

    X1, Y1 = np.meshgrid(
        x, y, indexing="ij"
    )  # meshgrid of arrays for interpolation, needed if using pcolormesh
    pts = np.column_stack((X1.flatten(), Y1.flatten()))
    Z1 = interp(pts)  # pressure interpolated over X1, Y1 shape
    # print(Z1)
    # Z1 = Z1/np.amax(pressure_or_intensity)
    Z1 = Z1.reshape(X1.shape)

    # fname = r"C:\Users\RKPC\Documents\transducer_calibrations\538-T550H825\
    # 550kHz\report\pressure_values.txt"

    # try:
    #     with open(fname, 'x') as f:
    #         np.savetxt(f, Z1, fmt='%.4e')
    # except:
    #     pass

    pcm = ax1.pcolormesh(
        X1, Y1, Z1, cmap=cmap, shading="nearest", rasterized=True
    )  # the actual pcolormesh, rasterized NEEDS to be set to True to prevent SVGs
    # saving weirdly

    # if 'lateral' in name and 'pressure' in name:
    #     matlab_raw = pd.read_excel(r"C:\Users\RKPC\Documents\summer_2023\
    # Calibration Reports\514_MATLAB_raw.xlsx", header=None)
    #     # print(matlab_raw)
    #     print(Z1)
    # print(np.allclose(matlab_raw, Z1))

    # IMSHOW (WORKS, BUT THE AXIAL IMAGE IS WARPED...)
    # pcm = ax1.imshow(pressure, extent=(np.min(horizontal), np.max(horizontal),
    # np.min(vertical), np.max(vertical)), cmap=cmap, interpolation='none')
    # print(np.min(horizontal), np.max(horizontal), np.min(vertical), np.max(vertical))
    # print(-field_length, field_length, -field_height, field_height)

    # interp = RegularGridInterpolator((horizontal, vertical), pressure)
    # # print(interp)

    # pcm = ax1.imshow(
    #     interp((X1, Y1)),
    #     extent=(
    #         np.min(horizontal), np.max(horizontal),
    #         np.min(vertical), np.max(vertical)
    #     ),
    #     cmap=cmap,
    #     interpolation='none',
    # )

    # NO INTERPOLATION METHOD
    # pcm = ax1.pcolormesh(X1, Y1, pressure, cmap=cmap)

    minimum = 0
    maximum = 1

    pcm.set_clim(
        vmin=minimum, vmax=maximum
    )  # limits the pcolormesh between these two values

    """
    x axis
    """
    left_field_length = abs(left_field_length)
    right_field_length = abs(right_field_length)

    ax1.set_xlim(-left_field_length, right_field_length)
    x_ticks = list(range(-int(left_field_length), int(right_field_length) + 1))
    ax1.set_xticks(x_ticks)  # adds only the integer x-tick values
    ax1.set_xlabel(type_of_scan + "Position, mm")

    """
    y axis 
    """
    ax1.set_ylim(-field_height, field_height)
    y_ticks = list(range(-int(field_height), int(field_height + 1)))
    ax1.set_yticks(y_ticks)  # adds only the integer y-tick values

    """
    Colorbar
    """

    interval = abs(
        (maximum - minimum) / 5
    )  # intervals of 1/5th to locate ticks on colorbar at 0, 0.2, 0.4, 0.6, 0.8, 1.
    positions = [
        minimum,
        minimum + interval,
        minimum + interval * 2,
        minimum + interval * 3,
        minimum + interval * 4,
        maximum,
    ]  # where to put each tick on the colorbar
    divider = make_axes_locatable(ax1)  # aspect ratio of colorbar, same as ax1
    cax = divider.append_axes(
        "right", size="8%", pad=0.15
    )  # size and position of colorbar
    cax.tick_params(direction="in")  # make colorbar ticks point inward

    cbar = fig1.colorbar(pcm, cax=cax)  # colour bar called

    # cbar.ax.invert_yaxis() # To invert the colourbar stripe

    cbar.set_ticks(positions, labels=["0", "0.2", "0.4", "0.6", "0.8", "1"])

    # SAVE DATA
    if save:
        save_filename = str(Path(save_folder) / f"{name}field_plot.svg")
        # print(f"\nSaving {type_of_scan}{type_of_data} field scan to "
        # f"{save_filename}...")
        fig1.savefig(
            save_filename,
            bbox_inches="tight",
            format="svg",
            pad_inches=0,
            transparent=True,
        )  # pad_inches = 0 removes need to shrink image in Inkscape

    fig1.set_canvas(canvas)
    return canvas
    # fig1.show()


# line graph svg
# used for both combined_calibration_figures_python.py and
# linear_scan_graph_generator.py
@mpl.rc_context(style_1)
def line_graph(
    horizontal: np.ndarray,
    pressure_or_intensity: np.ndarray,
    left_field_length: float | str,
    right_field_length: float | str,
    name: str,
    type_of_scan: str,
    type_of_data: str,
    save: bool,
    save_folder: str,
    textbox: QTextBrowser,
) -> FigureCanvas:
    """Generate a line graph for a given transducer at a given frequency.

    Args:
        horizontal (np.ndarray): The horizontal positions of the transducer at which
            the data was taken.
        pressure_or_intensity (np.ndarray): The pressure or intensity values at each
            position of the transducer.
        left_field_length (float | str): The length of the field in the negative x
            direction.
        right_field_length (float | str): The length of the field in the positive x
            direction.
        name (str): The name of the transducer.
        type_of_scan (str): The type of scan (lateral or axial).
        type_of_data (str): The type of data (pressure or intensity).
        save (bool): If True, saves the line graph as an SVG file.
        save_folder (str): The folder in which to save the line graph.
        textbox (QTextBrowser): The text box to which to write any errors or warnings.

    Returns:
        FigureCanvas: The canvas object representing the figure.

    """
    _minimum = pressure_or_intensity.min()
    maximum = pressure_or_intensity.max()

    fig2, ax2 = plt.subplots(1, 1)
    canvas = FigureCanvas(fig2)

    ax2.tick_params(axis="both", direction="in", right=False, top=False, pad=7)
    ax2.spines[["right", "top"]].set_visible(False)
    # fig2.canvas.manager.set_window_title(name+"line_plot") # names window
    # ax2.set_aspect(5/3)

    # ax2.set_aspect(abs((-abs(left_field_length)-abs(right_field_length))
    # /(-2))*2) # 2:1 aspect ratio
    # ax2.set_aspect('equal') # makes 1:1 aspect ratio

    """
    x axis
    """
    if left_field_length != "linear" and right_field_length != "linear":
        # Cast to float since we know they're not "linear" strings
        left_float = float(left_field_length)
        right_float = float(right_field_length)
        ax2.set_aspect(
            abs((-abs(left_float) - abs(right_float)) / (-2)) * (3.75 / 4)
        )  # aspect ratio (FOR MANUAL ADJUSTMENT, change 3.75/4 to desired ratio)

        left_field_length = abs(left_float)
        right_field_length = abs(right_float)

        ax2.set_xlim(-left_field_length, right_field_length)
        x_ticks = list(range(-int(left_field_length), int(right_field_length) + 1))
        # x_ticks = map(str, x_ticks)
        ax2.set_xticks(x_ticks)  # adds only the integer x-tick values
    else:
        ax2.set_aspect("auto")  # makes automatic aspect ratio

    ax2.set_xlabel(type_of_scan + "Position, mm")
    ax2.tick_params(axis="x", pad=12)
    # locator=MaxNLocator(nbins=len(x_ticks), integer = True)
    # ax2.xaxis.set_major_locator(locator)

    """
    y axis
    """
    ax2.set_ylim(0, 1)
    y_ticks = [0, 0.2, 0.4, 0.6, 0.8, 1]
    ax2.set_yticks(y_ticks)  # adds only the integer y-tick values
    ax2.set_ylabel("Normalized " + type_of_data)

    norm_pressure = np.divide(
        pressure_or_intensity, maximum
    )  # normalisation of pressure to 1 and below
    maximum_location = np.where(
        norm_pressure == 1.0
    )  # where is the maximum pressure value?
    # which curve (column) does the maximum pressure value belong to in the
    # norm_pressure array?
    max_curve = maximum_location[1][0]

    new_pressure_or_intensity = []  # list for isolating the maximum pressure curve

    # Isolate the maximum pressure curve
    new_pressure_or_intensity = [
        norm_pressure[i][max_curve] for i in range(len(pressure_or_intensity))
    ]  # convert list to numpy array
    new_pressure_or_intensity = np.array(
        new_pressure_or_intensity
    )  # convert list to numpy array

    ax2.axhline(
        y=0.5, color="k", linestyle="dashed", dashes=(15, 10), lw=0.8
    )  # half-max line
    # this causes the glitch where combined_calibration_figures_python
    # can run linear_scan_graph_generator
    if left_field_length != "linear" and right_field_length != "linear":
        ax2.plot(
            horizontal,
            new_pressure_or_intensity,
            color="#74BEA3",
            lw=2.8,
            solid_capstyle="round",
        )  # graph the maximum pressure curve
        # fig2.set_size_inches(7, 5)
    else:
        ax2.plot(
            horizontal,
            new_pressure_or_intensity,
            color="#74BEA3",
            lw=2.8,
            solid_capstyle="round",
            marker="o",
        )  # graph the maximum pressure curve
        peak_location = horizontal[
            np.argwhere(new_pressure_or_intensity == max(new_pressure_or_intensity))
        ]
        ax2.plot(peak_location, max(new_pressure_or_intensity), color="r", marker="o")
        textbox.append("Peak occurs at: " + f"{peak_location[0][0]:.2f}" + "mm")

    ax2.grid()
    # fig2.tight_layout()
    # fig2.set_size_inches(12, 12)

    # manager = fig2.canvas.manager
    # manager.resize(*manager.window.maxsize())

    # SAVE DATA
    if save:
        save_filename = str(Path(save_folder) / f"{name}line_plot.svg")
        # print(f"\nSaving {type_of_scan}{type_of_data} linear scan to "
        # f"{save_filename}...")
        fig2.savefig(
            save_filename,
            bbox_inches="tight",
            format="svg",
            pad_inches=0,
            transparent=True,
        )

    fig2.set_canvas(canvas)
    return canvas
    # fig2.show()
