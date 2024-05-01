import sys

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import axes3d
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialogButtonBox, QPushButton, QComboBox, QDialog, QGridLayout, QGroupBox, 
                               QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QSlider,
                               QTableWidget, QTableWidgetItem, QTabWidget, QTextBrowser, QVBoxLayout,
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
        freq_textbox.setMaximumWidth(100)

        z_textbox = QLineEdit()
        z_textbox.setMaximumWidth(100)

        phase_textbox = QLineEdit()
        phase_textbox.setMaximumWidth(100)

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
        # SIGLENT GROUPBOX 
        siglent_group = QGroupBox("Siglent")
        
        # EB-50 GROUPBOX 
        eb50_group = QGroupBox("EB-50")
        serial_num_label = QLabel("EB-50 serial number")
        amp_num_label = QLabel("Amplifier number")
        siglent_file_label = QLabel("Siglent file")
        eb50_atten_label = QLabel("EB-50 Attenuation (dB)")
        amp_start_val_label = QLabel("Amplitude start value (Vpp)")
        amp_stop_val_label = QLabel("Amplitude stop value (Vpp)")
        amp_step_val_label = QLabel("Amplitude step value (Vpp)")
        coupler_atten_label = QLabel("Coupler attenuation (dB)")

        # MAIN LAYOUT 
        main_layout = QGridLayout()
        main_layout.addWidget(siglent_group)
        main_layout.addWidget(eb50_group)

        self.setLayout(main_layout)

class TransducerCalibrationTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # CHECKBOX GROUP
        checkbox_group = QGroupBox("Selections")
        # Column 0
        sweep_label = QLabel("Write sweep file and graph?")
        ax_field_graphs_label = QLabel("Print axial field graphs?")
        ax_line_graphs_label = QLabel("Print axial line graphs?")
        lat_field_graphs_label = QLabel("Print lateral field graphs?")
        lat_line_graphs_label = QLabel("Print lateral line graphs?")
        save_label = QLabel("Save file?")
        checkbox_list_col_0 = [sweep_label, ax_field_graphs_label, ax_line_graphs_label, lat_field_graphs_label, lat_line_graphs_label, save_label]
        # Column 1
        sweep_box = QCheckBox()
        ax_field_graphs_box = QCheckBox()
        ax_line_graphs_box = QCheckBox()
        lat_field_graphs_box = QCheckBox()
        lat_line_graphs_box = QCheckBox()
        save_box = QCheckBox()
        checkbox_list_col_1 = [sweep_box, ax_field_graphs_box, ax_line_graphs_box, lat_field_graphs_box, lat_line_graphs_box, save_box]

        # layout for checkboxes 
        checkbox_layout = QGridLayout()
        # add labels to group 
        for i in range(len(checkbox_list_col_0)): 
            checkbox_layout.addWidget(checkbox_list_col_0[i], i, 0)
        # add checkboxes to group
        for i in range(len(checkbox_list_col_1)): 
            # checkbox_list_col_1[i].setAlignment()
            checkbox_layout.addWidget(checkbox_list_col_1[i], i, 1)

        checkbox_group.setLayout(checkbox_layout)

        # CHOOSE FILES GROUP
        choose_file_group = QGroupBox("File Selection")
        # Column 0
        self.data_files = QLabel("Data Files")
        self.save_folder = QLabel("Save Folder")
        self.eb50_file_button = QLabel("EB-50 File")
        choose_file_col_0 = [self.data_files, self.save_folder, self.eb50_file_button]
        # Column 1
        self.data_files_button = QPushButton("Choose Files")
        self.save_folder_button = QPushButton("Choose Folder")
        self.eb50_file_button_button = QPushButton("Choose File")
        choose_file_col_1 = [self.data_files_button, self.save_folder_button, self.eb50_file_button_button]

        # layout for choose files 
        choose_file_layout = QGridLayout()
        # add labels to group 
        for i in range(len(choose_file_col_0)): 
            choose_file_layout.addWidget(choose_file_col_0[i], i, 0)
        # add buttons to group
        for i in range(len(choose_file_col_1)): 
            choose_file_layout.addWidget(choose_file_col_1[i], i, 1)
        
        choose_file_group.setLayout(choose_file_layout)

        # TEXT DISPLAY GROUP 
        text_display_group = QTextBrowser()

        # TEXT FIELDS GROUP 
        text_fields_group = QGroupBox("Specifications")
        # Column 0
        self.ax_left_field_length = QLabel("Axial Left Field Length")
        self.ax_right_field_length = QLabel("Axial Right Field Length")
        self.ax_field_height = QLabel("Axial Field Height")
        self.ax_left_line_length = QLabel("Axial Left Line Plot Length")
        self.ax_right_line_length = QLabel("Axial Right Line Plot Length")
        self.lat_field_length = QLabel("Lateral Field Length")
        self.interp_step = QLabel("Interpolation Step")
        text_fields_list_col_0 = [self.ax_left_field_length, self.ax_right_field_length, self.ax_field_height, self.ax_left_line_length, self.ax_right_line_length, self.lat_field_length, self.interp_step]
        # Column 1
        self.ax_left_field_length_field = QLineEdit()
        self.ax_right_field_length_field = QLineEdit()
        self.ax_field_height_field = QLineEdit()
        self.ax_left_line_length_field = QLineEdit()
        self.ax_right_line_length_field = QLineEdit()
        self.lat_field_length_field = QLineEdit()
        self.interp_step_field = QLineEdit()
        text_fields_list_col_1 = [self.ax_left_field_length_field, self.ax_right_field_length_field, self.ax_field_height_field, self.ax_left_line_length_field, self.ax_right_line_length_field, self.lat_field_length_field, self.interp_step_field]

        # layout for text fields
        text_field_layout = QGridLayout()
        # add labels to group 
        for i in range(len(text_fields_list_col_0)): 
            text_field_layout.addWidget(text_fields_list_col_0[i], i, 0)
        # add buttons to group
        for i in range(len(text_fields_list_col_1)): 
            text_fields_list_col_1[i].setMaximumWidth(200)
            text_field_layout.addWidget(text_fields_list_col_1[i], i, 1)
        
        text_fields_group.setLayout(text_field_layout)

        # PRINT GRAPH BUTTON 
        print_graph = QPushButton("PRINT GRAPHS")
        print_graph.setStyleSheet("background-color: #74BEA3")

        # DISPLAY WINDOW (Change to tabs window, currently a placeholder)
        graph_group = QTabWidget()
        graph_group.addTab(GraphTab(self), "Sweep")
        graph_group.addTab(GraphTab(self), "Axial Field")
        graph_group.addTab(GraphTab(self), "Lateral Field")
        graph_group.addTab(GraphTab(self), "Axial Line")
        graph_group.addTab(GraphTab(self), "Lateral Line")

        # # CHANGING THE TEXT BASED ON WHICH CHECKBOX IS CHECKED 
        # if ax_field_graphs_box.isChecked():
        #     self.ax_left_field_length.setText("Axial Left Field Length*")
        #     self.ax_right_field_length.setText("Axial Right Field Length*")
        #     self.ax_field_height.setText("Axial Field Height*")
        #     self.interp_step.setText("Interpolation Step*") 
        #     self.update()
        # sweep_box.connect(self.changeText("sweep"))
        ax_field_graphs_box.checkStateChanged.connect(lambda: self.changeText(ax_field_graphs_box, "ax_field"))

        
        # MAIN LAYOUT 
        main_layout = QGridLayout()
        main_layout.addWidget(checkbox_group, 0, 0, 2, 1)
        main_layout.addWidget(choose_file_group, 0, 1)
        main_layout.addWidget(text_display_group, 1, 1)
        main_layout.addWidget(text_fields_group, 2, 0)
        main_layout.addWidget(graph_group, 2, 1, 2, 1)
        main_layout.addWidget(print_graph, 3, 0)
        self.setLayout(main_layout)

    def changeText(self, box: QCheckBox, type: str):
        if type == "ax_field":
            if box.isChecked():
                self.ax_left_field_length.setText("Axial Left Field Length*")
            else: 
                self.ax_left_field_length.setText("Axial Left Field Length")
                # print("Hi")
            self.ax_left_field_length.update()


# change to accept parameter of graph type + other graph info 
class GraphTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        main_layout = QGridLayout()

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