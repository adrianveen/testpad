import sys

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import axes3d
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialogButtonBox, QPushButton, QComboBox, QDialog, QGridLayout, QGroupBox, 
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QSlider,
                               QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout,
                               QWidget, QSizePolicy)


class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None): 

        # QMainWindow.__init__(self, parent)

        super().__init__(parent)

        # Central widget
        # self._main = QWidget()
        # self.setCentralWidget(self._main)

        tab_widget = QTabWidget()
        # sp = tab_widget.sizePolicy()
        # sp.Policy = QSizePolicy.Expanding
        
        # tab_widget.setMinimumSize(QMainWindow.sizeHint())
        # tab_widget.showFullScreen()
        tab_widget.addTab(MatchingBoxTab(self), "Matching Box")
        tab_widget.addTab(EboxTab(self), "EB-50 Calibration")
        tab_widget.addTab(TransducerCalibrationTab(self), "Transducer Calibration")
        tab_widget.addTab(RFBTab(self), "Radiation Force Balance")
        # tab_widget.addTab(ApplicationsTab(file_info, self), "Applications")
        # self.adjustSize()
        # self.addDockWidget(tab_widget)

        # tab_layout = QVBoxLayout() 
        # tab_layout.addWidget(tab_widget)

        main_layout = QVBoxLayout()

        # main_layout.addLayout(tab_layout)
        # main_layout.addWidget(QPushButton())
        # main_layout.addStretch()

        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

        self.setCentralWidget(tab_widget)

        # self.adjustSize()



class MatchingBoxTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Column 0
        freq_label = QLabel("Frequency: ")
        z_label = QLabel("Impedance: ")
        phase_label = QLabel("Phase: ")
        toroid_label = QLabel("Toroid: ")

        widgets_list_col_0 = [freq_label, z_label, phase_label, toroid_label]

        # column 1 
        freq_textbox = QLineEdit()
        # freq_textbox.setMaximumWidth(100)

        z_textbox = QLineEdit()
        # z_textbox.setMaximumWidth(100)

        phase_textbox = QLineEdit()
        # phase_textbox.setMaximumWidth(100)

        toroid_box = QComboBox()
        toroid_box.addItems(["200", "280", "160"])

        get_val = QPushButton("Get Values") 

        widgets_list_col_1 = [freq_textbox, z_textbox, phase_textbox, toroid_box, get_val]

        # column 2 
        affix_box = QComboBox()
        affix_box.addItems(["MHz", "kHz"])

        widgets_list_col_2 = [affix_box]

        # main layout of matching box section 
        main_layout = QGridLayout()

        # add all widgets to grid layout 
        for i in range(len(widgets_list_col_0)): 
            main_layout.addWidget(widgets_list_col_0[i], i, 0)

        for i in range(len(widgets_list_col_1)): 
            main_layout.addWidget(widgets_list_col_1[i], i, 1)

        for i in range(len(widgets_list_col_2)): 
            main_layout.addWidget(widgets_list_col_2[i], i, 2)

        self.setLayout(main_layout)

class EboxTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        siglent_group = QGroupBox("Siglent")
        eb50_group = QGroupBox("EB-50")
        main_layout = QGridLayout()
        main_layout.addWidget(siglent_group)
        main_layout.addWidget(eb50_group)

        self.setLayout(main_layout)

class TransducerCalibrationTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Column 0
        sweep_label = QLabel("Write sweep file and graph?")
        ax_field_graphs_label = QLabel("Print axial field graphs?")
        ax_line_graphs_label = QLabel("Print axial line graphs?")
        lat_field_graphs_label = QLabel("Print lateral field graphs?")
        lat_line_graphs_label = QLabel("Print lateral line graphs?")
        save_label = QLabel("Save file?")
        data_files = QLabel("Data Files")
        save_folder = QLabel("Save Folder")
        eb50_file = QLabel("EB-50 File")
        ax_left_field_length = QLabel("Axial Left Field Length")
        ax_right_field_length = QLabel("Axial Right Field Length")
        ax_field_height = QLabel("Axial Field Height")
        ax_left_line_length = QLabel("Axial Left Line Plot Length")
        ax_right_line_length = QLabel("Axial Right Line Plot Length")
        lat_field_length = QLabel("Lateral Field Length")
        interp_step = QLabel("Interpolation Step")

        widgets_list_col_0 = [sweep_label, ax_field_graphs_label, ax_line_graphs_label, lat_field_graphs_label, lat_line_graphs_label, save_label, \
                              data_files, save_folder, eb50_file, \
                                ax_left_field_length, ax_right_field_length, ax_field_height, ax_left_line_length, ax_right_line_length, lat_field_length, interp_step]
        
        # Column 1, EDIT
        sweep_box = QCheckBox()
        ax_field_graphs_box = QCheckBox()
        ax_line_graphs_box = QCheckBox()
        lat_field_graphs_box = QCheckBox()
        lat_line_graphs_box = QCheckBox()
        save_box = QCheckBox()
        data_files_button = QPushButton("Choose Files")
        save_folder_button = QPushButton("Choose Folder")
        eb50_file_button = QPushButton("Choose File")
        ax_left_field_length_field = QLineEdit()
        ax_right_field_length_field = QLineEdit()
        ax_field_height_field = QLineEdit()
        ax_left_line_length_field = QLineEdit()
        ax_right_line_length_field = QLineEdit()
        lat_field_length_field = QLineEdit()
        interp_step_field = QLineEdit()

        # EDIT 
        widgets_list_col_1 = [sweep_box, ax_field_graphs_box, ax_line_graphs_box, lat_field_graphs_box, lat_line_graphs_box, save_box, \
                              data_files_button, save_folder_button, eb50_file_button, \
                                ax_left_field_length_field, ax_right_field_length_field, ax_field_height_field, ax_left_field_length_field, ax_left_line_length_field, ax_right_line_length_field, lat_field_length_field, interp_step_field]
        

        main_layout = QGridLayout()

        # add all widgets to grid layout 
        for i in range(len(widgets_list_col_0)): 
            main_layout.addWidget(widgets_list_col_0[i], i, 0)

        for i in range(len(widgets_list_col_1)): 
            main_layout.addWidget(widgets_list_col_1[i], i, 1)

        self.setLayout(main_layout)

class RFBTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        main_layout = QGridLayout()

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setFixedSize

    # if len(sys.argv) >= 2:
    #     file_name = sys.argv[1]
    # else:
    #     file_name = "."

    tab_dialog = ApplicationWindow()
    # tab_dialog.setFixedSize(700, 500)
    tab_dialog.show()
    tab_dialog.raise_()

    sys.exit(app.exec())