from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QPixmap
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QComboBox, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser, QVBoxLayout,
                               QWidget)
# from calibration_reports.combined_calibration_figures_python import combined_calibration
# from matching_box.lc_circuit_matching import Calculations
# from matching_box.csv_graphs_hioki import csv_graph

class RFBTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Controls group 
        controls_group = QGroupBox() 
        # Column 0
        file_label = QLabel("File: ")
        save_label = QLabel("Save graphs?")
        save_folder_label = QLabel("Save folder: ")
        controls_list_col_0 = [file_label, save_label, save_folder_label]
        # Column 1
        

        main_layout = QGridLayout()


        self.setLayout(main_layout)