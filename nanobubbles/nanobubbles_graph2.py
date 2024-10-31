from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qtagg import FigureCanvas
from pathlib import Path
import os

class NanobubblesGraph():
    def __init__(self, nanobubble_txt) -> None:
        self.aggregate_representation = np.array([])

        # Check if nanobubble_txt is a list or a single file
        if isinstance(nanobubble_txt, list):
            for file in nanobubble_txt:
                self._process_file(file)
        else:
            self._process_file(nanobubble_txt)

    def _process_file(self, file):
        with open(file, "r") as f:
            data = np.array(np.loadtxt(f, skiprows=89, delimiter="\t"))  # SKIPS 89 ROWS (assumed to be metadata)

        # Append data to aggregate_representation
        for row in data:
            if row[0] != -1:
                for i in range(int(row[1])):  # adds the nanobubble size count number of times
                    self.aggregate_representation = np.append(self.aggregate_representation, row[0])

    # returns canvas of mpl graph to UI 
    # bin_width determines width of histogram bars 
    def get_graphs(self, bin_width, scale):
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)
        
        # if scale = log, set x-axis to log scale from 1-1000
        if scale:
            self.ax.set_xscale('log')
            self.ax.set_xlim(1, 1000)
            bins = np.logspace(np.log10(1), np.log10(1000), num=int(bin_width))
        else:
            # Linear scale: use linear bins
            bins = np.arange(0, 1000 + bin_width, bin_width)
        
        self.ax.hist(self.aggregate_representation, bins=bins, color='#73A89E', rwidth=0.95)
         

        self.ax.set_xlabel("Diameter [nm]", fontsize=16)
        self.ax.set_ylabel("Number Absolute", fontsize=16)
        # set title of graph
        self.ax.set_title("Nanobubble Size Distribution", fontsize=18)

        # Increase font size of axes values
        self.ax.tick_params(axis='both', which='major', labelsize=14)
        self.ax.tick_params(axis='both', which='minor', labelsize=12)

        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.11, right=0.97, top=0.95, bottom=0.08)

        self.fig.set_canvas(self.canvas)
        return(self.canvas)
    
    # create overlaid histograms based on 3 datasets passed through
    def overlaid_histograms(self, bin_width, scale):
        # Overlaid Histograms
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)

                # if scale = log, set x-axis to log scale from 1-1000
        if scale:
            self.ax.set_xscale('log')
            self.ax.set_xlim(1, 1000)
            bins = np.logspace(np.log10(1), np.log10(1000), num=int(bin_width))
        else:
            # Linear scale: use linear bins
            bins = np.arange(0, 1000 + bin_width, bin_width)
            
        for i, data_batch in enumerate(self.nanobubble_txt):
            plt.hist(data_batch, bins=bins, alpha=0.5, label=f'Batch {i+1}', log=True)

        self.ax.set_xlabel("Diameter [nm]", fontsize=16)
        self.ax.set_ylabel("Number Absolute", fontsize=16)
        # set title of graph
        self.ax.set_title("Nanobubble Size Distribution", fontsize=18)

        # Increase font size of axes values
        self.ax.tick_params(axis='both', which='major', labelsize=14)
        self.ax.tick_params(axis='both', which='minor', labelsize=12)

        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.11, right=0.97, top=0.95, bottom=0.08)

        self.fig.set_canvas(self.canvas)
        return(self.canvas)

    # save the canvas graph as a SVG 
    def save_graph(self, folder):
        nanobubble_svg_filename = (Path(self.nanobubble_txt).name).split(".")[0]
        full_save_name = os.path.join(folder, str(nanobubble_svg_filename)+".svg")
        self.fig.savefig(full_save_name, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
        return(full_save_name)

    def got_resize_event(self):
        self.fig.tight_layout(pad=.5)

if __name__ == "__main__":
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt")
    n.get_graphs()
    plt.show()
