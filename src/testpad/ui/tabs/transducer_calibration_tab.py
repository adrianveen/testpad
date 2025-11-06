from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from testpad.core.transducer.combined_calibration_figures_python import (
    CombinedCalibration,
    CombinedCalibrationConfig,
)


class TransducerCalibrationTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # need to initialise these so that saving can happen
        self.selected_data_files, self.selected_save_folder, self.selected_eb50_file = (
            [],
            "",
            "",
        )
        self.dialog1 = None
        self.dialog2 = None
        self.dialog3 = None

        # CHECKBOX GROUP
        checkbox_group = QGroupBox("Selections")
        # Column 0
        sweep_label = QLabel("Write sweep file and graph?")
        ax_field_graphs_label = QLabel("Print axial field graphs?")
        ax_line_graphs_label = QLabel("Print axial line graphs?")
        lat_field_graphs_label = QLabel("Print lateral field graphs?")
        lat_line_graphs_label = QLabel("Print lateral line graphs?")
        save_label = QLabel("Save file?")
        checkbox_list_col_0 = [
            sweep_label,
            ax_field_graphs_label,
            ax_line_graphs_label,
            lat_field_graphs_label,
            lat_line_graphs_label,
            save_label,
        ]
        # Column 1
        self.sweep_box = QCheckBox()
        self.sweep_box.setChecked(True)
        self.ax_field_graphs_box = QCheckBox()
        self.ax_field_graphs_box.setChecked(True)
        self.ax_line_graphs_box = QCheckBox()
        self.ax_line_graphs_box.setChecked(True)
        self.lat_field_graphs_box = QCheckBox()
        self.lat_field_graphs_box.setChecked(True)
        self.lat_line_graphs_box = QCheckBox()
        self.lat_line_graphs_box.setChecked(True)
        self.save_box = QCheckBox()
        checkbox_list_col_1 = [
            self.sweep_box,
            self.ax_field_graphs_box,
            self.ax_line_graphs_box,
            self.lat_field_graphs_box,
            self.lat_line_graphs_box,
            self.save_box,
        ]

        # layout for checkboxes
        checkbox_layout = QGridLayout()
        # add labels to group
        for i in range(len(checkbox_list_col_0)):
            checkbox_layout.addWidget(checkbox_list_col_0[i], i, 0)
        # add checkboxes to group
        for i in range(len(checkbox_list_col_1)):
            # checkbox_list_col_1[i].setAlignment()
            checkbox_layout.addWidget(
                checkbox_list_col_1[i], i, 1, Qt.AlignmentFlag.AlignCenter
            )

        checkbox_group.setLayout(checkbox_layout)

        # CHANGING THE TEXT BASED ON WHICH CHECKBOX IS CHECKED
        self.ax_field_graphs_box.checkStateChanged.connect(
            lambda: self.change_text(self.ax_field_graphs_box, "ax_field")
        )
        self.ax_line_graphs_box.checkStateChanged.connect(
            lambda: self.change_text(self.ax_line_graphs_box, "ax_line")
        )
        self.lat_field_graphs_box.checkStateChanged.connect(
            lambda: self.change_text(self.lat_field_graphs_box, "lat_field")
        )
        self.lat_line_graphs_box.checkStateChanged.connect(
            lambda: self.change_text(self.lat_line_graphs_box, "lat_line")
        )
        self.save_box.checkStateChanged.connect(
            lambda: self.change_text(self.save_box, "save")
        )

        # CHOOSE FILES GROUP
        choose_file_group = QGroupBox("File Selection")
        # Column 0
        self.data_files = QLabel("Data Files*")
        data_files_tooltip = (
            "Select scan data from the transducer's calibration folder.\n"
            "Select the 5 voltage sweep files, and all 8 directional scan files."
        )
        self.data_files.setToolTip(data_files_tooltip)
        self.save_folder = QLabel("Save Folder")
        save_folder_tooltip = (
            "Select the folder where you want to save the output files."
        )
        self.save_folder.setToolTip(save_folder_tooltip)
        self.eb50_file = QLabel("EB-50 File")
        eb50_file_tooltip = "Select the EB-50 calibration .yaml file."
        self.eb50_file.setToolTip(eb50_file_tooltip)

        choose_file_col_0 = [self.data_files, self.save_folder, self.eb50_file]
        # Column 1
        self.data_files_button = QPushButton("Choose Files")
        self.data_files_button.setToolTip(data_files_tooltip)
        self.save_folder_button = QPushButton("Choose Folder")
        self.save_folder_button.setToolTip(save_folder_tooltip)
        self.eb50_file_button = QPushButton("Choose File")
        self.eb50_file_button.setToolTip(eb50_file_tooltip)

        choose_file_col_1 = [
            self.data_files_button,
            self.save_folder_button,
            self.eb50_file_button,
        ]

        # layout for choose files
        choose_file_layout = QGridLayout()
        # add labels to group
        for i in range(len(choose_file_col_0)):
            choose_file_layout.addWidget(choose_file_col_0[i], i, 0)
        # add buttons to group
        for i in range(len(choose_file_col_1)):
            choose_file_layout.addWidget(choose_file_col_1[i], i, 1)

        choose_file_group.setLayout(choose_file_layout)

        # connecting buttons
        self.data_files_button.clicked.connect(lambda: self.open_file_dialog("data"))
        self.save_folder_button.clicked.connect(lambda: self.open_file_dialog("save"))
        self.eb50_file_button.clicked.connect(lambda: self.open_file_dialog("eb50"))

        # TEXT DISPLAY GROUP
        self.text_display_group = QTextBrowser()

        # file selection/text display layout
        file_text_layout = QVBoxLayout()
        file_text_layout.addWidget(choose_file_group)
        file_text_layout.addWidget(self.text_display_group)

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
        text_fields_list_col_0 = [
            self.ax_left_field_length,
            self.ax_right_field_length,
            self.ax_field_height,
            self.ax_left_line_length,
            self.ax_right_line_length,
            self.lat_field_length,
            self.interp_step,
        ]
        # Column 1
        self.ax_left_field_length_field = QLineEdit()
        self.ax_left_field_length_field.setText("7.5")
        self.ax_right_field_length_field = QLineEdit()
        self.ax_right_field_length_field.setText("7.5")
        self.ax_field_height_field = QLineEdit()
        self.ax_field_height_field.setText("3")
        self.ax_left_line_length_field = QLineEdit()
        self.ax_left_line_length_field.setText("7.5")
        self.ax_right_line_length_field = QLineEdit()
        self.ax_right_line_length_field.setText("7.5")
        self.lat_field_length_field = QLineEdit()
        self.lat_field_length_field.setText("3")
        self.interp_step_field = QLineEdit()
        self.interp_step_field.setText("0.1")
        text_fields_list_col_1 = [
            self.ax_left_field_length_field,
            self.ax_right_field_length_field,
            self.ax_field_height_field,
            self.ax_left_line_length_field,
            self.ax_right_line_length_field,
            self.lat_field_length_field,
            self.interp_step_field,
        ]

        # layout for text fields
        text_field_layout = QGridLayout()
        # add labels to group
        for i in range(len(text_fields_list_col_0)):
            text_field_layout.addWidget(text_fields_list_col_0[i], i, 0)
        # add buttons to group
        for i in range(len(text_fields_list_col_1)):
            text_fields_list_col_1[i].setMaximumWidth(200)
            text_field_layout.addWidget(
                text_fields_list_col_1[i], i, 1, Qt.AlignmentFlag.AlignCenter
            )

        text_fields_group.setLayout(text_field_layout)

        # PRINT GRAPH BUTTON
        print_graph = QPushButton("PRINT GRAPHS")
        print_graph.setStyleSheet("background-color: #66A366; color: black;")
        print_graph.clicked.connect(lambda: self.print_graph())

        # text fields/print button layout
        text_print_layout = QVBoxLayout()
        text_print_layout.addWidget(text_fields_group)
        text_print_layout.addWidget(print_graph)

        # DISPLAY WINDOW
        self.graph_group = QTabWidget()
        self.graph_group.setTabsClosable(True)
        self.graph_group.tabCloseRequested.connect(
            lambda index: self.graph_group.removeTab(index)
        )

        # MAIN LAYOUT
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.addWidget(checkbox_group, 0, 0)
        main_layout.addLayout(file_text_layout, 0, 1)
        # main_layout.addWidget(choose_file_group, 0, 1)
        # main_layout.addWidget(self.text_display_group, 1, 1)
        main_layout.addLayout(text_print_layout, 1, 0)
        main_layout.addWidget(self.graph_group, 1, 1)
        # main_layout.addWidget(self.graph_group, 2, 1, 2, 1)
        # main_layout.addWidget(print_graph, 3, 0)
        self.setLayout(main_layout)

    @Slot()
    def change_text(self, box: QCheckBox, box_type: str):
        if box_type == "ax_field":
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
        elif box_type == "ax_line":
            if box.isChecked():
                self.ax_left_line_length.setText("Axial Left Line Plot Length*")
                self.ax_right_line_length.setText("Axial Right Line Plot Length*")
            else:
                self.ax_left_line_length.setText("Axial Left Line Plot Length")
                self.ax_right_line_length.setText("Axial Right Line Plot Length")
        elif box_type == "lat_field":
            if box.isChecked():
                self.lat_field_length.setText("Lateral Field Length*")
                self.interp_step.setText("Interpolation Step*")
            else:
                self.lat_field_length.setText("Lateral Field Length")
                self.interp_step.setText("Interpolation Step")
        elif box_type == "lat_line":
            if box.isChecked():
                self.lat_field_length.setText("Lateral Field Length*")
            else:
                self.lat_field_length.setText("Lateral Field Length")
        elif box_type == "save":
            if box.isChecked():
                self.save_folder.setText("Save Folder*")
            else:
                self.save_folder.setText("Save Folder")

    @Slot()
    def open_file_dialog(self, dialog_type: str):
        if dialog_type == "data":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Data Files")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFiles)
            if self.dialog1.exec():
                self.text_display_group.append("Data Files: ")
                self.selected_data_files = self.dialog1.selectedFiles()
            for i in self.selected_data_files:
                if i == self.selected_data_files[-1]:
                    self.text_display_group.append(i + "\n")
                else:
                    self.text_display_group.append(i)
            # print(self.selected_data_files)
        elif dialog_type == "save":
            self.dialog2 = QFileDialog(self)
            self.dialog2.setWindowTitle("Save Folder")
            self.dialog2.setFileMode(QFileDialog.FileMode.Directory)
            if self.dialog2.exec():
                self.selected_save_folder = self.dialog2.selectedFiles()[0]
                self.text_display_group.append(
                    "Save Folder: " + str(self.selected_save_folder) + "\n"
                )
            # print(self.selected_save_folder)
        elif dialog_type == "eb50":
            self.dialog3 = QFileDialog(self)
            self.dialog3.setWindowTitle("EB-50 File")
            self.dialog3.setFileMode(QFileDialog.FileMode.ExistingFile)
            if self.dialog3.exec():
                self.selected_eb50_file = self.dialog3.selectedFiles()[0]
                self.text_display_group.append(
                    "EB-50 File: " + str(self.selected_eb50_file) + "\n"
                )
            # print(self.selected_eb50_file)

    # placeholder function
    @Slot()
    def print_graph(self):
        # clear all tabs
        self.graph_group.clear()
        # print(self.ax_left)

        # sweep_data, axial_field, axial_line, lateral_field, lateral_line
        # axial_left_field_length, axial_right_field_length, axial_field_height, axial_left_line_length, axial_right_line_length, lateral_field_length, interp_step
        cfg = CombinedCalibrationConfig(
            files=[Path(p) for p in self.selected_data_files],
            save_folder=Path(self.selected_save_folder)
            if self.selected_save_folder
            else None,
            eb50_file=Path(self.selected_eb50_file)
            if self.selected_eb50_file
            else None,
            sweep_data=self.sweep_box.isChecked(),
            axial_field=self.ax_field_graphs_box.isChecked(),
            axial_line=self.ax_line_graphs_box.isChecked(),
            lateral_field=self.lat_field_graphs_box.isChecked(),
            lateral_line=self.lat_line_graphs_box.isChecked(),
            save=self.save_box.isChecked(),
            ax_left_field_length=float(self.ax_left_field_length_field.text() or 0),
            ax_right_field_length=float(self.ax_right_field_length_field.text() or 0),
            ax_field_height=float(self.ax_field_height_field.text() or 0),
            ax_left_line_length=float(self.ax_left_line_length_field.text() or 0),
            ax_right_line_length=float(self.ax_right_line_length_field.text() or 0),
            lat_field_length=float(self.lat_field_length_field.text() or 0),
            interp_step=float(self.interp_step_field.text() or 0),
        )
        graphs = CombinedCalibration(cfg, self.text_display_group).get_graphs()

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
