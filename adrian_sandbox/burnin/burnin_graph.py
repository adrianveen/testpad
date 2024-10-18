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

        self.fig.set_canvas(self.canvas)
        return(self.canvas)
