import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
import sys 
import matplotlib.pyplot as plt
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from calibration_resources import create_sweep_file, fetch_data, field_graph, line_graph, fwhmx
import os
from pathlib import Path

# from PySide6.QtCore import QObject, Slot
# from PySide6.QtWidgets import QApplication
# # from PySide6.QtGui import QGuiApplication DO NOT USE BECAUSE CLOSING THE GRAPH WILL CLOSE THE PROGRAM
# from PySide6.QtQml import QQmlApplicationEngine, QmlElement

from PySide6.QtWidgets import QTextBrowser


# QML_IMPORT_NAME = "calibration_reports"
# QML_IMPORT_MAJOR_VERSION = 1

"""
A script to write voltage sweep txts and to generate axial and lateral field/line plots as svgs. 
"""

# main class, runs all the relevant methods from calibration_resources and prints to the terminal 
class combined_calibration:
    def __init__(self, variables_dict: list, textbox: QTextBrowser, graph_tabs_list: list):
        plt.close("all") # closes previous graphs 

        plt.ion()
        # print(variables_dict)
        
        textbox.append("\n*******************GENERATING GRAPHS***********************\n") # divider 

        # assigns dictionary values to variables (probably wildly inefficient, might need reworking)
        # files, save_folder, eb50_file, sweep_data, axial_field, axial_line, lateral_field, lateral_line, axial_left_field_length, axial_right_field_length, axial_field_height, axial_left_line_length, axial_right_line_length, lateral_field_length, interp_step, save = map(variables_dict.get, ('Data Files*', 'Save Folder', 'EB-50 File', 'Write sweep file and graph?', 'Print axial field graphs?', 'Print axial line graphs?', 'Print lateral field graphs?', 'Print lateral line graphs?', 'Axial Left Field Length', 'Axial Right Field Length', 'Axial Field Height', 'Axial Left Line Plot Length', 'Axial Right Line Plot Length','Lateral Field Length', 'Interpolation Step', 'Save file?'))
        files, save_folder, eb50_file = [i for i in variables_dict[:3]]
        sweep_data, axial_field, axial_line, lateral_field, lateral_line, save = [bool(i) for i in variables_dict[3:9]]
        axial_left_field_length, axial_right_field_length, axial_field_height, axial_left_line_length, axial_right_line_length, lateral_field_length, interp_step = [float(i) if i != '' else 0 for i in variables_dict[9:]]

        """
        MANUAL PARAMETER OVERRIDE (THE MANUAL FILE OVERRIDE IS BELOW)
        """
        # folder = r"C:\Users\RKPC\Documents\transducer_calibrations\103-T479.5H750\1432kHz\scan_data" # data folder
        # save_folder = r"C:\Users\RKPC\Documents\transducer_calibrations\103-T479.5H750\1432kHz\report" # save folder 
        # eb50_file = r"C:\Users\RKPC\Documents\summer_2022\fn_generator\eb50_data\2244-eb50\2244-eb50.txt" # eb50 txt file

        # # below parameters are for graph appearances 
        # axial_left_field_length = -8 # yz field & line graph left x-axis limit 
        # axial_right_field_length = 8 # yz field & line graph right x-axis limit 
        # axial_field_height = 3 # yz field & line plot height (from -axial_field_height to +axial_field_height)
        # lateral_field_length = 3 # xz field & line plot width and height (from -lateral_field_length to +lateral_field_length)
        # interp_step = 0.1 # interpolation step, affects all field plots

        # # Toggle which graphs you'd like to print below (if True, the graph is printed and potentially saved, if False, it is not)
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
        # files_list = [f for f in os.listdir(folder) if f.endswith('.hdf5')] # include only hdf5 files
        # files_list = sorted(files_list, key=lambda x: int((x.split('.')[0]).split('_')[-1])) # sort so that the latest scan is used 
        files_list = sorted(files, key=lambda x: int((x[x.rfind('.')-1]))) # sort so that the latest scan is used 
        
        sweep_list = []

        """
        AUTOMATIC FILE DETECTION FOR LOOP 
        """
        for i in range(len(files_list)):
            f = files_list[i]
            if "_sweep_" in f:
                sweep_filename = f
                sweep_list.append(sweep_filename)
            elif "_yz_" in f:
                axial_filename = f
            elif "_xz_" in f:
                lateral_filename = f
            elif "_x_" in f:
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

        # Do the files exist? If not, exit (could probably be reworked into more specific error messages)
        try:
            if sweep_data or axial_field or axial_line or lateral_field or lateral_line:
                if sweep_data:
                    textbox.append("Sweeps: "+ str(sweep_list))
                    trans_freq_filename = sweep_filename # trans_freq_filename is only so the name of the transducer can be grabbed
                if axial_field:
                    textbox.append("Axial: "+ axial_filename)
                    trans_freq_filename = axial_filename
                if axial_line:
                    textbox.append("y linear: " + y_line_scan)
                    trans_freq_filename = y_line_scan
                if lateral_field:
                    textbox.append("Lateral: " + lateral_filename)
                    trans_freq_filename = lateral_filename
                if lateral_line:
                    textbox.append("x linear: " + x_line_scan)
                    textbox.append("z linear: " + z_line_scan) 
                    trans_freq_filename = x_line_scan
            else: 
                raise NameError
        except NameError as e:
            textbox.append("\nNameError: "+str(e)+"\nOops! One or more of the scan files does not exist. \
                  \nDid you input the right folder?\nAre there scans missing?\nDid you select the correct checkboxes?\n")
            return

        # TXT FILE OF FILES USED
        if save:
            counter = 1

            while True:
                try:
                    full_filename1 = os.path.join(save_folder, "files_used_" + str(counter) +".txt") 
                    with open(full_filename1, "x") as f:
                        textbox.append(f"\nSaving files used to {full_filename1}...")
                        for file in files_list:
                            f.write(file+"\n")
                    break
                except FileExistsError:
                    counter += 1


        """
        TRANSDUCER AND FREQUENCY DETAILS 
        """
        details = (trans_freq_filename.split("/")[-1]).split("_")
        for word in details:
            if "Hz" in word:
                freq = word # frequency 
            elif "T" in word and "H" in word:
                transducer = word
        if details[0] != transducer: # for dealing with files like '320_T1500H750' instead of '320-T1500H750'
            transducer = details[0]+"-"+transducer
        textbox.append("\nTransducer: "+ transducer)
        textbox.append("Frequency: "+ freq+"\n")

        """
        VOLTAGE SWEEP 
        """
        if sweep_data: 
            create_sweep_file(sweep_list, save_folder, transducer, freq, save, eb50_file, textbox)

        """
        FIELD GRAPHS
        """
        if axial_field:

            x_data, y_data, z_data, pressure, intensity = fetch_data(axial_filename, "axial")
            # Pressure field 
            field_graph(y_data, z_data, pressure, axial_left_field_length, axial_right_field_length, axial_field_height, transducer+"_"+freq+"_pressure_axial_", 'Axial ', 'Pressure', interp_step, save, save_folder, textbox)
            # Intensity field 
            field_graph(y_data, z_data, intensity, axial_left_field_length, axial_right_field_length, axial_field_height, transducer+"_"+freq+"_intensity_axial_", 'Axial ', 'Intensity', interp_step, save, save_folder, textbox)

        if lateral_field:
            x_data, y_data, z_data, pressure, intensity = fetch_data(lateral_filename, "lateral")
            # Pressure field 
            field_graph(x_data, z_data, pressure, lateral_field_length, lateral_field_length, lateral_field_length, transducer+"_"+freq+"_pressure_lateral_", 'Lateral ', 'Pressure', interp_step, save, save_folder, textbox)
            # Intensity field 
            field_graph(x_data, z_data, intensity, lateral_field_length, lateral_field_length, lateral_field_length, transducer+"_"+freq+"_intensity_lateral_", 'Lateral ', 'Intensity', interp_step, save, save_folder, textbox)
        
        """
        LINEAR GRAPHS 
        """

        # Y LINE SCAN LINE GRAPH
        if axial_line:

            x_data, y_data, z_data, pressure, intensity = fetch_data(y_line_scan, "axial")

            line_graph(y_data, pressure, axial_left_line_length, axial_right_line_length, transducer+"_"+freq+"_pressure_axial_", 'Axial ', 'Pressure', save, save_folder, textbox)
            y_pressure_fwhmx = fwhmx(y_data, pressure, axial_left_line_length, axial_right_line_length, 'Y', 'Axial ', 'Pressure')
            line_graph(y_data, intensity, axial_left_line_length, axial_right_line_length, transducer+"_"+freq+"_intensity_axial_", 'Axial ', 'Intensity', save, save_folder, textbox)
            y_intensity_fwhmx = fwhmx(y_data, intensity, axial_left_line_length, axial_right_line_length, 'Y', 'Axial ', 'Intensity')

            # AXIAL FWHMX
            textbox.append(f"Axial Pressure FWHMX: {y_pressure_fwhmx:0.1f} mm")
            textbox.append(f"Axial Intensity FWHMX: {y_intensity_fwhmx:0.1f} mm")

        if lateral_line:
            # X LINE SCAN 
            x_data, y_data, z_data, pressure, intensity = fetch_data(x_line_scan, "lateral")
            # Pressure line plot 
            line_graph(x_data, pressure, lateral_field_length, lateral_field_length, transducer+"_"+freq+"_pressure_lateral_", 'Lateral ', 'Pressure', save, save_folder, textbox)
            x_pressure_fwhmx = fwhmx(x_data, pressure, lateral_field_length, lateral_field_length, 'X', 'Lateral ', 'Pressure')
            # Intensity line plot 
            line_graph(x_data, intensity, lateral_field_length, lateral_field_length, transducer+"_"+freq+"_intensity_lateral_", 'Lateral ', 'Intensity', save, save_folder, textbox)
            x_intensity_fwhmx = fwhmx(x_data, intensity, lateral_field_length, lateral_field_length, 'X', 'Lateral ', 'Intensity')

            # # Z LINE SCAN 
            x_data, y_data, z_data, pressure, intensity = fetch_data(z_line_scan, "lateral")
            z_pressure_fwhmx = fwhmx(z_data, np.transpose(pressure), lateral_field_length, lateral_field_length, 'Z', 'Lateral ', 'Pressure')
            z_intensity_fwhmx = fwhmx(z_data, np.transpose(intensity), lateral_field_length, lateral_field_length, 'Z', 'Lateral ', 'Intensity')

            # LATERAL FWHMX (AVERAGE OF X AND Z)
            averaged_pressure_fwhmx = (x_pressure_fwhmx+z_pressure_fwhmx)/2.0
            averaged_intensity_fwhmx = (x_intensity_fwhmx+z_intensity_fwhmx)/2.0
            textbox.append(f"Averaged Lateral Pressure FWHMX: {averaged_pressure_fwhmx:0.1f} mm")
            textbox.append(f"Averaged Lateral Intensity FWHMX: {averaged_intensity_fwhmx:0.1f} mm")

        # plt.show()

# """
# QML Connection Section 
# """
# @QmlElement
# class TextBox(QObject): 
#     # function for the button
#     # files, save_folder, eb50_file, sweep_data, axial_field, axial_line, lateral_field, lateral_line, axial_left_field_length, axial_right_field_length, axial_field_height, axial_left_line_length, axial_right_line_length, lateral_field_length, interp_step, save
#     @Slot(list, result=None)
#     def printGraph(self, param_list):
#         # plt.ion()
#         # map values to dictionary? 
#         main(param_list)
#         # plt.show()
#     # close all open graphs upon termination of program 
#     @Slot(None, result=None)
#     def closeAll(self): 
#         plt.close('all')
#     @Slot(str, str, result=None)
#     def showFile(self, type, file):
#         file = file.split(",")
#         print(type)
#         for i in file: 
#             print(i)
#         print("")

# """
# Init section 
# """
# if __name__ == '__main__':

#     plt.ion()

#     app = QApplication(sys.argv)
#     engine = QQmlApplicationEngine()
#     engine.quit.connect(app.quit)

#     #Load the QML file
#     qml_file = Path(__file__).parent / "widget_reports.qml"
#     engine.load(qml_file)

#     # #Show the window
#     if not engine.rootObjects():
#         sys.exit(-1)

#     sys.exit(app.exec())


