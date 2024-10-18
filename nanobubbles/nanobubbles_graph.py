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
        self.nanobubble_txt = nanobubble_txt
        with open(self.nanobubble_txt, "r") as f:
            self.data = np.array(np.loadtxt(f, skiprows=89, delimiter="\t")) # SKIPS 89 ROWS (assumed to be metadata)

        # create a giant array where every size is represented count number of times 
        # ex. if there are 80 120nm nanobubbles, add 120nm to this array 80 times 
        self.aggregate_representation = np.array([])

        for row in self.data:
            if row[0] != -1:
                for i in range(int(row[1])): # adds the nanobubble size count number of times 
                    self.aggregate_representation = np.append(self.aggregate_representation, row[0])
            
        # self.size = self.data[:, 0]
        # self.count = self.data[:, 1]

    # returns canvas of mpl graph to UI 
    # bin_width determines width of histogram bars 
    def get_graphs(self, bin_width, scale):
        self.fig, self.ax = plt.subplots(1, 1)
        canvas = FigureCanvas(self.fig)
        # if scale = log, set x-axis to log scale from 1-1000
        if scale:
            self.ax.set_xscale('log')
            self.ax.set_xlim(1, 1000)
            bins = np.logspace(np.log10(1), np.log10(1000), num=int(bin_width))
        else:
            # Linear scale: use linear bins
            bins = np.arange(0, 1000 + bin_width, bin_width)
        # ax.plot(self.size, self.count, ls='None', marker='o') # scatter plot
        self.ax.hist(self.aggregate_representation, bins=bins)
        # self.ax.hist(self.aggregate_representation, bins=np.arange(0, 1000+bin_width, bin_width)) # histogram 

        self.ax.set_xlabel("Size/nm")
        self.ax.set_ylabel("Number")

        self.fig.set_canvas(canvas)
        return(canvas)
    
    # save the canvas graph as a SVG 
    def save_graph(self, folder):
        nanobubble_svg_filename = (Path(self.nanobubble_txt).name).split(".")[0]
        full_save_name = os.path.join(folder, str(nanobubble_svg_filename)+".svg")
        self.fig.savefig(full_save_name, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
        return(full_save_name)

if __name__ == "__main__":
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt")
    n.get_graphs()
    plt.show()