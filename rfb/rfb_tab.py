from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QPixmap
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
        controls_group = QGroupBox("Selections") 
        # Column 0
        file_label = QLabel("File: ")
        save_label = QLabel("Save graphs?")
        save_folder_label = QLabel("Save folder: ")
        controls_list_col_0 = [file_label, save_label, save_folder_label]
        # Column 1
        self.file_button = QPushButton("Choose Files")
        self.save_box = QCheckBox()
        self.save_folder = QPushButton("Choose Folder")
        controls_list_col_1 = [self.file_button, self.save_box, self.save_folder]
        # layout 
        controls_layout = QGridLayout()
        for i in range(len(controls_list_col_0)):
            controls_layout.addWidget(controls_list_col_0[i], i, 0)
        for i in range(len(controls_list_col_1)):
            controls_layout.addWidget(controls_list_col_1[i], i, 1)
        controls_group.setLayout(controls_layout)

        # Text display 
        self.text_display = QTextBrowser()

        # Graph display 
        self.graph_display = QTabWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(controls_group, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 2, 1)

        self.setLayout(main_layout)