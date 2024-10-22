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
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import h5py

class BurninGraph():
    def __init__(self, burnin_file) -> None:
        self.burnin_file = burnin_file

        # open burn-in file and extract error/time 
        with h5py.File(self.burnin_file) as file:
            self.error = list(file['Error (counts)'])
            self.time = list(file['Time (s)'])

    # graphs error vs time 
    def getGraph(self):
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)

        self.ax.plot(self.time, self.error)

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Error (counts)")

        # Determine title based on filename
        if "_axis_A_" in self.burnin_file:
            self.ax.set_title("Axis A Error")
        elif "_axis_B_" in self.burnin_file:
            self.ax.set_title("Axis B Error")
        else:
            self.ax.set_title("Unknown Axis")  # Fallback title in case of unexpected filename

        self.fig.set_canvas(self.canvas)
        return(self.canvas)
    
    #graph error vs time with 0 values remove
    def getGraphs_separated(self):
        # Separate positive and negative errors
        positive_errors = [e if e > 0 else np.nan for e in self.error]
        negative_errors = [e if e < 0 else np.nan for e in self.error]

        # linear regression line for both positive and negative error values
        # positive regression line
        self.fig, self.ax = plt.subplots(1, 1)

        # Plotting
        plt.plot(self.time, positive_errors, label='Positive Error (counts)')
        plt.plot(self.time, negative_errors, label='Negative Error (counts)')

        # Labels and title
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Error (counts)")
        
        # Determine title based on filename
        if "_axis_A_" in self.burnin_file:
            title = "Axis A Error"
        elif "_axis_B_" in self.burnin_file:
            title = "Axis B Error"
        else:
            title = "Unknown Axis"  # Fallback title in case of unexpected filename
        self.ax.set_title(title)
        # add the legend in the best location around the center of the graph
        self.ax.legend(loc='best', bbox_to_anchor=(0.5, 0.5, 0, 0))

        self.canvas = FigureCanvas(self.fig)

        return self.canvas

        

