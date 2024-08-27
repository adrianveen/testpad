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

class NanobubblesGraph():
    def __init__(self, nanobubble_txt) -> None:
        with open(nanobubble_txt, "r") as f:
            self.data = np.loadtxt(f, skiprows=89, delimiter="\t")

        self.data = self.data[self.data[:, 0].argsort()] # sort numpy data by the size column 
            
        self.size = self.data[:, 0]
        self.count = self.data[:, 1]

    def get_graphs(self):
        fig, ax = plt.subplots(1, 1)
        canvas = FigureCanvas(fig)

        ax.plot(self.size, self.count)

        ax.set_xlim([0, 1000])
        ax.set_xlabel("Size/nm")
        ax.set_ylabel("Number")

        fig.set_canvas(canvas)
        return(canvas)


if __name__ == "__main__":
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt")
    n.get_graphs()
    plt.show()