import sys
# sys.path.append('../')
# import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
# from mpl_toolkits.mplot3d import axes3d
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QPixmap
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QCheckBox, QFileDialog, QPushButton, QComboBox, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMainWindow, QTabWidget, QTextBrowser, QVBoxLayout,
                               QWidget)
from combined_calibration_figures_python import combined_calibration
from lc_circuit_matching import Calculations
from csv_graphs_hioki import csv_graph
from testpad_tabs import MatchingBoxTab, EboxTab, TransducerCalibrationTab, RFBTab

# application window (inherits QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None): 

        # QMainWindow.__init__(self, parent)

        super().__init__(parent)

        tab_widget = QTabWidget()
        # sp = tab_widget.sizePolicy()
        # sp.Policy = QSizePolicy.Expanding
        
        # tab_widget.setMinimumSize(QMainWindow.sizeHint())
        # tab_widget.showFullScreen()
        tab_widget.addTab(MatchingBoxTab(self), "Matching Box")
        tab_widget.addTab(EboxTab(self), "Siglent/EB-50 Calibration")
        tab_widget.addTab(TransducerCalibrationTab(self), "Transducer Calibration Report")
        tab_widget.addTab(RFBTab(self), "Radiation Force Balance")

        main_layout = QVBoxLayout()

        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

        self.setCentralWidget(tab_widget)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 11pt;}")

    tab_dialog = ApplicationWindow()
    tab_dialog.setWindowTitle("FUS Testpad")
    # tab_dialog.setFixedSize(False)
    # tab_dialog.setMaximumSize()
    # tab_dialog.setFixedSize(700, 500)
    tab_dialog.showMaximized() # full screen 
    
    # tab_dialog.raise_() # look up what this does

    sys.exit(app.exec())
