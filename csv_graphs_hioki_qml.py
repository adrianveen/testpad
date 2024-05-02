from pathlib import Path, PurePath, PureWindowsPath
import sys
import numpy as np
import math
import os
import matplotlib.pyplot as plt
# import numpy as np
import pandas as pd 
# from pathlib import Path

# from PySide6.QtCore import QObject, Slot
# from PySide6.QtWidgets import QApplication
# from PySide6.QtGui import QGuiApplication
# from PySide6.QtQml import QQmlApplicationEngine, QmlElement

# QML_IMPORT_NAME = "matching_graphs"
# QML_IMPORT_MAJOR_VERSION = 1

class csv_graph():
    def __init__(self, frequency, unit, filename, save, save_folder: str = None):
        self.selected_freq = frequency
        if unit == "kHz":
            self.selected_freq *= 1e3
        elif unit == "MHz":
            self.selected_freq *= 1e6
        
        self.filename = filename
        # print(self.filename)
        self.save = save
        # print(self.save)
        self.save_folder = save_folder[7:]

        # fetch data from csv file 
        try: 
            lines = np.array(pd.read_csv(self.filename, header=0, sep=',', usecols=[1, 7, 9], skiprows=20))
        except Exception as e: 
            print(str(e) + "\nWARNING: Unable to open file. Did you select a CSV file?\n")
            return()
            # sys.exit(1)
        # print(lines)

        self.frequencies = lines[:, 0]
        self.impedances = lines[:, 1]
        self.phases = lines[:, 2]

        # graph impedance
        self.impedance_graph = self.graph(self.frequencies, self.impedances, xlabel="Frequencies (Hz)", ylabel="Impedance (Ohms)", title="Impedance Magnitude |Z|", type='Z')

        # graph phase 
        self.phase_graph = self.graph(self.frequencies, self.phases, xlabel="Frequencies (Hz)", ylabel="Phase Shift (degrees)", title="Phase", type='THETAZ')

        # plt.draw()


    def graph(self, x, y, xlabel:str=None, ylabel:str=None, title:str=None, type:str=None):
        fig, ax = plt.subplots(1, 1)

        ax.plot(x, y, "o-", alpha = 0.3)

        intersection = np.interp(self.selected_freq, x, y)
        ax.plot(self.selected_freq, intersection, "ro")
        ax.annotate(f"[{self.selected_freq/1e6:0.3f}, {intersection:0.3f}]", (self.selected_freq, intersection))

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        if self.save:
            graph_type = (self.filename.split("/")[-1]).split(".")[0]
            # save_filename = PurePath(self.save_folder, graph_type+'_'+type+'.svg')
            # save_filename = str(save_filename).replace('\\\\', '\\')
            # save_filename = os.path.normpath(str(save_filename))
            if sys.platform.startswith('win'):
                save_filename = (self.save_folder[1:]+'/'+graph_type+'_'+type+'.svg')
            else: 
                save_filename = (self.save_folder+'/'+graph_type+'_'+type+'.svg')
            print(f"Saving {title} graph to {save_filename}...")
            try:
                fig.savefig(save_filename, bbox_inches='tight', format='svg', pad_inches = 0, transparent=True) # pad_inches = 0 removes need to shrink image in Inkscape
            except Exception as e: 
                print(str(e)+"\nWARNING: Unable to save. Did you select a save location?\n")
            

        fig.show()

# @QmlElement
# class TextBox(QObject): 
#     # function for the button
#     # frequency, filename, save, save_folder
#     @Slot(float, str, str, bool, str, result=None)
#     def printGraph(self, frequency, unit, filename, save, save_folder):
#         csv_graph(frequency, unit, filename, save, save_folder)
#     @Slot(None, result=None)
#     def closeAll(self): 
#         plt.close('all')

# if __name__ == '__main__':
#     #Set up the application window
#     app = QApplication(sys.argv)
#     engine = QQmlApplicationEngine()
#     engine.quit.connect(app.quit)

#     #Load the QML file
#     qml_file = Path(__file__).parent / "widget_hioki.qml"
#     engine.load(qml_file)

#     # #Show the window
#     if not engine.rootObjects():
#         sys.exit(-1)

#     sys.exit(app.exec())
    