"""A script to create linear graphs for analysis during transducer calibration."""

from PySide6.QtWidgets import QTextBrowser

from testpad.core.transducer.calibration_resources import (
    fetch_data,
    line_graph,
    np,
    plt,
)


class LinearScan:
    def __init__(self, variables_dict: list, textbox: QTextBrowser) -> None:
        plt.close("all")  # closes previous graphs

        self.graphs_list: list[object | None] = [None] * 3

        # assigns dictionary values to variables
        # (probably wildly inefficient, might need reworking)
        files, save, save_folder = variables_dict[:3]
        x_line, y_line, z_line = variables_dict[3:]

        """
        MANUAL PARAMETER OVERRIDE (THE MANUAL FILE OVERRIDE IS BELOW)
        """
        # folder = r"C:\Users\RKPC\Documents\transducer_calibrations\103-T479.5H750\1432kHz\scan_data" # data folder
        # save_folder = r"C:\Users\RKPC\Documents\transducer_calibrations\103-T479.5H750\1432kHz\report" # save folder
        # eb50_file = r"C:\Users\RKPC\Documents\summer_2022\fn_generator\eb50_data\2244-eb50\2244-eb50.txt" # eb50 txt file

        # # below parameters are for graph appearances
        # axial_left_field_length = -8 # yz field & line graph left x-axis limit
        # axial_right_field_length = 8 # yz field & line graph right x-axis limit
        # axial_field_height = 3
        # yz field & line plot height (from -axial_field_height to +axial_field_height)
        # lateral_field_length = 3
        # xz field & line plot width and height
        #  (from -lateral_field_length to +lateral_field_length)
        # interp_step = 0.1 # interpolation step, affects all field plots

        # # Toggle which graphs you'd like to print below (if True, the graph is printed
        # and potentially saved, if False, it is not)
        # sweep_data = True
        # axial_field = True
        # axial_line = False
        # lateral_field = False
        # lateral_line = False

        # # Toggle the save (if True, graphs are saved, if False, graphs aren't saved)
        # save = False

        """
        FILE STUFF
        """
        # print(variables_dict)
        # files_list = [f for f in os.listdir(folder) if f.endswith('.hdf5')] # include only hdf5 files
        # files_list = sorted(files_list, key=lambda x: int((x.split('.')[0]).split('_')[-1])) # sort so that the latest scan is used
        files_list = sorted(
            files, key=lambda x: int(x[x.rfind(".") - 1])
        )  # sort so that the latest scan is used
        # print(files_list)

        """
        AUTOMATIC FILE DETECTION FOR LOOP
        """
        x_line_scan = ""
        y_line_scan = ""
        z_line_scan = ""
        for i in range(len(files_list)):
            f = files_list[i]
            if "_x_" in f:
                x_line_scan = f
            elif "_y_" in f:
                y_line_scan = f
            elif "_z_" in f:
                z_line_scan = f

        """
        MANUAL FILE OVERRIDE
        """
        # sweep_filename = r"518_T1000H550_sweep_1000kHz_01.hdf5" # voltage sweep filename
        # axial_filename = r"532_T500H750_yz_500kHz_2000mVpp_08.hdf5" # yz field & line plot
        # lateral_filename = r"526_T1570H750_xz_1570kHz_1000mVpp_04.hdf5" # xz field & line plot
        # x_line_scan = r"317_T1150H550_x_3450kHz_1500mVpp_01.hdf5" # x linear scan
        # y_line_scan = r"C:\Users\RKPC\Documents\transducer_calibrations\532-T500H750\500kHz\scan_data\532_T500H750_y_500kHz_2000mVpp_02.hdf5" # y linear scan
        # z_line_scan = r"317_T1150H550_z_3450kHz_1500mVpp_01.hdf5" # z linear scan
        # save_folder = r"C:\Users\RKPC\Documents\transducer_calibrations\532-T500H750\500kHz\report_PYTHON"

        # Do the files exist? If not, exit

        # Do the files exist? If not, exit
        trans_freq_filename = None
        try:
            if x_line:
                textbox.append("x linear: " + x_line_scan)
                trans_freq_filename = x_line_scan
            if y_line:
                textbox.append("y linear: " + y_line_scan)
                trans_freq_filename = y_line_scan
            if z_line:
                textbox.append("z linear: " + z_line_scan)
                trans_freq_filename = z_line_scan
        except NameError:
            textbox.append(
                "\nOops! One or more of the scan files does not exist. "
                "Did you input the right folder? Are there scans missing? "
                "Have you toggled the graphs correctly?\n"
            )
            return

        if not trans_freq_filename:
            textbox.append(
                "\nNo scan file was selected. "
                "Please choose a folder and toggle at least one linear scan.\n"
            )
            return

            # print("Missing file:", e)
            # sys.exit(1)

        textbox.append(
            "\n*******************GENERATING GRAPHS***********************\n"
        )  # divider

        """
        TRANSDUCER AND FREQUENCY DETAILS
        """

        details = (trans_freq_filename.split("/")[-1]).split("_")
        # print(details)
        # transducer = details[0]+ '-' + details[1] # Transducer name
        freq = ""
        transducer = ""
        for word in details:
            if "Hz" in word:
                freq = word  # frequency
            elif "T" in word and "H" in word:
                transducer = word
        if (
            details[0] != transducer
        ):  # for dealing with files like '320_T1500H750' instead of '320-T1500H750'
            transducer = details[0] + "-" + transducer
        textbox.append("\nTransducer: " + transducer)
        textbox.append("Frequency: " + freq + "\n")

        """
        GRAPHING
        """
        if x_line:
            # X LINE SCAN
            textbox.append("Outputting x line scan linear graph...")
            x_data, y_data, z_data, pressure, _intensity, _ = fetch_data(
                x_line_scan, "lateral"
            )

            # Pressure line plot
            x_graph = line_graph(
                horizontal=x_data,
                pressure_or_intensity=pressure,
                left_field_length="linear",
                right_field_length="linear",
                name=transducer + "_" + freq + "_x_linear_",
                type_of_scan="Lateral ",
                type_of_data="Pressure",
                save=save,
                save_folder=save_folder,
                textbox=textbox,
            )
            self.graphs_list[0] = x_graph

        if y_line:
            textbox.append("Outputting y line scan linear graph...")
            x_data, y_data, z_data, pressure, _intensity, _ = fetch_data(
                y_line_scan, "axial"
            )

            y_graph = line_graph(
                horizontal=y_data,
                pressure_or_intensity=pressure,
                left_field_length="linear",
                right_field_length="linear",
                name=transducer + "_" + freq + "_y_linear_",
                type_of_scan="Axial ",
                type_of_data="Pressure",
                save=save,
                save_folder=save_folder,
                textbox=textbox,
            )
            self.graphs_list[1] = y_graph

        if z_line:
            # # Z LINE SCAN
            textbox.append("Outputting z line scan linear graph...")
            x_data, y_data, z_data, pressure, _intensity, _ = fetch_data(
                z_line_scan, "lateral"
            )
            z_graph = line_graph(
                horizontal=z_data,
                pressure_or_intensity=np.transpose(pressure),
                left_field_length="linear",
                right_field_length="linear",
                name=transducer + "_" + freq + "_z_linear_",
                type_of_scan="Lateral ",
                type_of_data="Pressure",
                save=save,
                save_folder=save_folder,
                textbox=textbox,
            )
            self.graphs_list[2] = z_graph

        textbox.append(
            "\n***********************FINISHED****************************\n"
        )

    def getGraphs(self) -> list[object | None]:
        return self.graphs_list
