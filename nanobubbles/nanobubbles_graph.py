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
            self.data = np.array(np.loadtxt(f, skiprows=89, delimiter="\t"))

        # self.data = self.data[self.data[:, 0].argsort()] # sort numpy data by the size column 

        # counter = 0
        # while counter <= len(self.data):
        #     if self.data[counter][0] > 1000:
        #         break
        #     counter += 1

        # self.data = self.data[:counter]

        self.aggregate_representation = np.array([])

        for row in self.data:
            if row[0] != -1:
                for i in range(int(row[1])):    
                    self.aggregate_representation = np.append(self.aggregate_representation, row[0])
            
        self.size = self.data[:, 0]
        self.count = self.data[:, 1]

        # self.all_data = self.data[:, :2]
        # print(self.all_data)

    def get_graphs(self):
        fig, ax = plt.subplots(1, 1)
        canvas = FigureCanvas(fig)

        # ax.plot(self.size, self.count, ls='None', marker='o')
        ax.hist(self.aggregate_representation, bins='auto')

        # ax.set_xlim([0, 1000])
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