# from matplotlib.backends.backend_qtagg import FigureCanvas
# from matplotlib.figure import Figure
# from mpl_toolkits.mplot3d import axes3d
from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QWidget)
from transducer.combined_calibration_figures_python import combined_calibration

class TransducerCalibrationTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # need to initialise these so that saving can happen 
        self.selected_data_files, self.selected_save_folder, self.selected_eb50_file = [], "", ""

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
        self.sweep_box = QCheckBox()
        self.ax_field_graphs_box = QCheckBox()
        self.ax_line_graphs_box = QCheckBox()
        self.lat_field_graphs_box = QCheckBox()
        self.lat_line_graphs_box = QCheckBox()
        self.save_box = QCheckBox()
        checkbox_list_col_1 = [self.sweep_box, self.ax_field_graphs_box, self.ax_line_graphs_box, self.lat_field_graphs_box, self.lat_line_graphs_box, self.save_box]

        # layout for checkboxes 
        checkbox_layout = QGridLayout()
        # add labels to group 
        for i in range(len(checkbox_list_col_0)): 
            checkbox_layout.addWidget(checkbox_list_col_0[i], i, 0)
        # add checkboxes to group
        for i in range(len(checkbox_list_col_1)): 
            # checkbox_list_col_1[i].setAlignment()
            checkbox_layout.addWidget(checkbox_list_col_1[i], i, 1, Qt.AlignCenter)

        checkbox_group.setLayout(checkbox_layout)

        # CHANGING THE TEXT BASED ON WHICH CHECKBOX IS CHECKED 
        self.ax_field_graphs_box.checkStateChanged.connect(lambda: self.changeText(self.ax_field_graphs_box, "ax_field"))
        self.ax_line_graphs_box.checkStateChanged.connect(lambda: self.changeText(self.ax_line_graphs_box, "ax_line"))
        self.lat_field_graphs_box.checkStateChanged.connect(lambda: self.changeText(self.lat_field_graphs_box, "lat_field"))
        self.lat_line_graphs_box.checkStateChanged.connect(lambda: self.changeText(self.lat_line_graphs_box, "lat_line"))
        self.save_box.checkStateChanged.connect(lambda: self.changeText(self.save_box, "save"))

        # CHOOSE FILES GROUP
        choose_file_group = QGroupBox("File Selection")
        # Column 0
        self.data_files = QLabel("Data Files*")
        self.save_folder = QLabel("Save Folder")
        self.eb50_file = QLabel("EB-50 File")
        choose_file_col_0 = [self.data_files, self.save_folder, self.eb50_file]
        # Column 1
        self.data_files_button = QPushButton("Choose Files")
        self.save_folder_button = QPushButton("Choose Folder")
        self.eb50_file_button = QPushButton("Choose File")
        choose_file_col_1 = [self.data_files_button, self.save_folder_button, self.eb50_file_button]

        # layout for choose files 
        choose_file_layout = QGridLayout()
        # add labels to group 
        for i in range(len(choose_file_col_0)): 
            choose_file_layout.addWidget(choose_file_col_0[i], i, 0)
        # add buttons to group
        for i in range(len(choose_file_col_1)): 
            choose_file_layout.addWidget(choose_file_col_1[i], i, 1)
        
        choose_file_group.setLayout(choose_file_layout)

        # CONNECTING BUTTONS 
        self.data_files_button.clicked.connect(lambda: self.openFileDialog("data"))
        self.save_folder_button.clicked.connect(lambda: self.openFileDialog("save"))
        self.eb50_file_button.clicked.connect(lambda: self.openFileDialog("eb50"))

        # TEXT DISPLAY GROUP 
        self.text_display_group = QTextBrowser()

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
        print_graph.clicked.connect(lambda: self.printGraph())

        # DISPLAY WINDOW (Change to tabs window, currently a placeholder)
        self.graph_group = QTabWidget()
        self.graph_group.setTabsClosable(True)
        self.graph_group.tabCloseRequested.connect(lambda index: self.graph_group.removeTab(index))
        
        # MAIN LAYOUT 
        main_layout = QGridLayout()
        main_layout.addWidget(checkbox_group, 0, 0, 2, 1)
        main_layout.addWidget(choose_file_group, 0, 1)
        main_layout.addWidget(self.text_display_group, 1, 1)
        main_layout.addWidget(text_fields_group, 2, 0)
        main_layout.addWidget(self.graph_group, 2, 1, 2, 1)
        main_layout.addWidget(print_graph, 3, 0)
        self.setLayout(main_layout)

    @Slot()
    def changeText(self, box: QCheckBox, type: str):
        if type == "ax_field":
            if box.isChecked():
                self.ax_left_field_length.setText("Axial Left Field Length*")
                self.ax_right_field_length.setText("Axial Right Field Length*")
                self.ax_field_height.setText("Axial Field Height*")
                self.interp_step.setText("Interpolation Step*")
            else: 
                self.ax_left_field_length.setText("Axial Left Field Length")
                self.ax_right_field_length.setText("Axial Right Field Length")
                self.ax_field_height.setText("Axial Field Height")
                self.interp_step.setText("Interpolation Step")
        elif type == "ax_line": 
            if box.isChecked():
                self.ax_left_line_length.setText("Axial Left Line Plot Length*")
                self.ax_right_line_length.setText("Axial Right Line Plot Length*")
            else: 
                self.ax_left_line_length.setText("Axial Left Line Plot Length")
                self.ax_right_line_length.setText("Axial Right Line Plot Length")
        elif type == "lat_field":
            if box.isChecked():
                self.lat_field_length.setText("Lateral Field Length*")
                self.interp_step.setText("Interpolation Step*")
            else: 
                self.lat_field_length.setText("Lateral Field Length")
                self.interp_step.setText("Interpolation Step")
        elif type == "lat_line":
            if box.isChecked():
                self.lat_field_length.setText("Lateral Field Length*")
            else: 
                self.lat_field_length.setText("Lateral Field Length")
        elif type == "save":
            if box.isChecked():
                self.save_folder.setText("Save Folder*")
            else: 
                self.save_folder.setText("Save Folder")

    @Slot()
    def openFileDialog(self, type: str):
        if type == "data": 
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Data Files")
            self.dialog1.setFileMode(QFileDialog.ExistingFiles)
            if self.dialog1.exec(): 
                self.text_display_group.append("Data Files: ")
                self.selected_data_files = self.dialog1.selectedFiles()
            for i in self.selected_data_files:
                if i == self.selected_data_files[-1]:
                    self.text_display_group.append(i+"\n")
                else: 
                    self.text_display_group.append(i)
            # print(self.selected_data_files)
        elif type == "save":
            self.dialog2 = QFileDialog(self)
            self.dialog2.setWindowTitle("Save Folder")
            self.dialog2.setFileMode(QFileDialog.Directory)
            if self.dialog2.exec():
                self.selected_save_folder = self.dialog2.selectedFiles()[0]
                self.text_display_group.append("Save Folder: "+str(self.selected_save_folder)+"\n")
            # print(self.selected_save_folder)
        elif type == "eb50":
            self.dialog3 = QFileDialog(self)
            self.dialog3.setWindowTitle("EB-50 File")
            self.dialog3.setFileMode(QFileDialog.ExistingFile)
            if self.dialog3.exec():
                self.selected_eb50_file = self.dialog3.selectedFiles()[0]
                self.text_display_group.append("EB-50 File: "+str(self.selected_eb50_file)+"\n")
            # print(self.selected_eb50_file)

    @Slot()
    # placeholder function 
    def printGraph(self): 
        # clear all tabs
        self.graph_group.clear()

        # sweep_data, axial_field, axial_line, lateral_field, lateral_line
        # axial_left_field_length, axial_right_field_length, axial_field_height, axial_left_line_length, axial_right_line_length, lateral_field_length, interp_step
        var_dict = [self.selected_data_files, self.selected_save_folder, self.selected_eb50_file, 
             self.sweep_box.isChecked(), self.ax_field_graphs_box.isChecked(), self.ax_line_graphs_box.isChecked(), self.lat_field_graphs_box.isChecked(), self.lat_line_graphs_box.isChecked(), self.save_box.isChecked(),
             self.ax_left_field_length_field.text(), self.ax_right_field_length_field.text(), self.ax_field_height_field.text(), 
             self.ax_left_field_length_field.text(), self.ax_right_line_length_field.text(), self.lat_field_length_field.text(), self.interp_step_field.text()]
        graphs = combined_calibration(var_dict, self.text_display_group).getGraphs()
        
        # add graphs to tabs 
        if graphs[0] is not None: 
            self.graph_group.addTab(graphs[0], "Sweep")
        if graphs[1] is not None: 
            self.graph_group.addTab(graphs[1], "Axial Pressure Field Graph")
        if graphs[2] is not None: 
            self.graph_group.addTab(graphs[2], "Axial Intensity Field Graph")
        if graphs[3] is not None: 
            self.graph_group.addTab(graphs[3], "Lateral Pressure Field Graph")
        if graphs[4] is not None: 
            self.graph_group.addTab(graphs[4], "Lateral Intensity Field Graph")
        if graphs[5] is not None: 
            self.graph_group.addTab(graphs[5], "Axial Pressure Line Plot")
        if graphs[6] is not None: 
            self.graph_group.addTab(graphs[6], "Axial Intensity Line Plot")
        if graphs[7] is not None: 
            self.graph_group.addTab(graphs[7], "Lateral Pressure Line Plot")
        if graphs[8] is not None: 
            self.graph_group.addTab(graphs[8], "Lateral Intensity Line Plot")
        # self.graph_group.addT/ab()
        self.graph_group.adjustSize()