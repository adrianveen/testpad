from vol2press.vol2press_calcs import Vol2Press

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal

class Vol2PressTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.sweep_file = None
        self.cal_eb50_file = None
        self.sys_eb50_file = None
        self.save_location = None
        self.values_dict = {}

        # BUTTONS 
        selections_group = QGroupBox("File Selections")
        cal_eb50_file_btn = QPushButton("SELECT CALIBRATION EB-50 YAML")
        cal_eb50_file_btn.clicked.connect(lambda: self.openFileDialog("eb-50_cal"))
        sys_eb50_file_btn = QPushButton("SELECT CUSTOMER EB-50 YAML")
        sys_eb50_file_btn.clicked.connect(lambda: self.openFileDialog("eb-50_sys"))
        save_btn = QPushButton("SAVE AS")
        save_btn.clicked.connect(lambda: self.openFileDialog("save"))

        selections_layout = QGridLayout()
        selections_layout.addWidget(cal_eb50_file_btn, 0, 0)
        selections_layout.addWidget(sys_eb50_file_btn, 1, 0)
        # selections_layout.addWidget(sweep_btn, 2, 0)
        selections_layout.addWidget(save_btn, 2, 0)
        selections_group.setLayout(selections_layout)

        # USER FIELDS 
        # ONE TIME FIELDS 
        # available frequencies should be deduced 
        single_fields_group = QGroupBox("Transducer Fields")
        impedance_label = QLabel("impedance_fund")
        self.impedance_field = QLineEdit()
        phase_label = QLabel("phase_fund")
        self.phase_field = QLineEdit()
        pcd_label = QLabel("PCD_freq")
        self.pcd_field = QLineEdit()
        diameter_label = QLabel("txDiameter")
        self.diameter_field = QLineEdit()
        focal_point_label = QLabel("txFocalPointFactor")
        self.focal_point_field = QLineEdit()

        single_fields_layout = QGridLayout()
        single_fields_layout.setColumnStretch(0, 1)
        single_fields_layout.setColumnStretch(1, 1)
        single_fields_layout.addWidget(impedance_label, 0, 0)
        single_fields_layout.addWidget(self.impedance_field, 0, 1)
        single_fields_layout.addWidget(phase_label, 1, 0)
        single_fields_layout.addWidget(self.phase_field, 1, 1)
        single_fields_layout.addWidget(pcd_label, 2, 0)
        single_fields_layout.addWidget(self.pcd_field, 2, 1)
        single_fields_layout.addWidget(diameter_label, 3, 0)
        single_fields_layout.addWidget(self.diameter_field, 3, 1)
        single_fields_layout.addWidget(focal_point_label, 4, 0)
        single_fields_layout.addWidget(self.focal_point_field, 4, 1)
        single_fields_group.setLayout(single_fields_layout)

        # FIELDS PER FREQUENCY 
        freq_fields_group = QGroupBox("Info Per Frequency")
        sweep_btn = QPushButton("SELECT SWEEP TXT")
        sweep_btn.clicked.connect(lambda: self.openFileDialog("sweep"))
        axial_len_label = QLabel("TxAxialFocalDiameter")
        self.axial_field = QLineEdit()
        lateral_len_label = QLabel("TxLateralFocalDiameter")
        self.lateral_field = QLineEdit()
        offset_label = QLabel("offset")
        self.offset_field = QLineEdit()

        self.fields_list = [self.axial_field, self.lateral_field, self.offset_field]

        for field in self.fields_list:
            field.textChanged.connect(lambda: self.enable_btn())

        # self.fields_dict = {"TxAxialFocalDiameter": axial_field, "TxLateralFocalDiameter": lateral_field}

        fields_layout = QGridLayout()
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)
        fields_layout.addWidget(sweep_btn, 0, 0, 1, 2)
        fields_layout.addWidget(axial_len_label, 1, 0)
        fields_layout.addWidget(self.axial_field, 1, 1)
        fields_layout.addWidget(lateral_len_label, 2, 0)
        fields_layout.addWidget(self.lateral_field, 2, 1)
        fields_layout.addWidget(offset_label, 3, 0)
        fields_layout.addWidget(self.offset_field, 3, 1)
        freq_fields_group.setLayout(fields_layout)

        # RESULTS BUTTONS
        self.add_to_yaml_btn = QPushButton("ADD FREQUENCY INFORMATION")
        self.add_to_yaml_btn.setStyleSheet("QPushButton:disabled {color: gray}")
        self.add_to_yaml_btn.clicked.connect(lambda: self.disable_btn())
        self.add_to_yaml_btn.clicked.connect(lambda: self.get_calcs())
        results_btn = QPushButton("PRINT TO YAML")
        results_btn.setStyleSheet("background-color: #74BEA3")
        results_btn.clicked.connect(lambda: self.create_yaml())
        # results_btn.clicked.connect(lambda: self.get_calcs())

        # TEXT CONSOLE 
        console_box = QGroupBox("Console Output")
        self.text_display = QTextBrowser()
        console_layout = QGridLayout()
        console_layout.addWidget(self.text_display)
        console_box.setLayout(console_layout)
        
        # GRAPH
        self.graph_display = QTabWidget()

        # MAIN LAYOUT 
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.addWidget(selections_group, 0, 0)
        main_layout.addWidget(single_fields_group, 1, 0)
        main_layout.addWidget(freq_fields_group, 2, 0)
        main_layout.addWidget(self.add_to_yaml_btn, 3, 0)
        main_layout.addWidget(results_btn, 4, 0)
        main_layout.addWidget(console_box, 5, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 5, 1)

        self.setLayout(main_layout)

    @Slot()
    # file dialog boxes to select sweep/calibration eb-50/customer eb-50 files 
    def openFileDialog(self, d_type):
        if d_type == "sweep":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Sweep File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Sweep File: ")
                self.sweep_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sweep_file+"\n")
                self.enable_btn() # enable the new frequency to be added to the YAML 

        elif d_type == "eb-50_cal":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Calibration EB-50 File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.yaml")
            self.dialog1.setDefaultSuffix("yaml") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Calibration EB-50 File: ")
                self.cal_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.cal_eb50_file+"\n")

        elif d_type == "eb-50_sys":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Customer EB-50 File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.yaml")
            self.dialog1.setDefaultSuffix("yaml") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Customer EB-50 File: ")
                self.sys_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sys_eb50_file+"\n")

        elif d_type == "save":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setNameFilter("*.yaml")
            self.dialog1.setDefaultSuffix("yaml") # default suffix of yaml
            self.dialog1.setWindowTitle("YAML Save Location")
            self.dialog1.setFileMode(QFileDialog.AnyFile)
            if self.dialog1.exec():
                self.text_display.append("Save Location: ")
                self.save_location = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.save_location+"\n")

    def disable_btn(self):
        self.add_to_yaml_btn.setEnabled(False)
    
    def enable_btn(self):
        self.add_to_yaml_btn.setEnabled(True)

    @Slot()
    # return calc values 
    def get_calcs(self):
        if self.sweep_file is not None and self.cal_eb50_file is not None and self.sys_eb50_file is not None:
            self.calcs = Vol2Press(self.cal_eb50_file, self.sys_eb50_file, self.sweep_file)
            self.r_value = float(f"{self.calcs.return_B_value():.4f}")
            self.text_display.append(f"Regression value: {self.r_value} MPa/Vpp\n")
            self.printGraphs()
            self.add_to_frequency()
        else:
            if self.sweep_file is None:
                self.text_display.append(f"Missing file: sweep file")
            if self.cal_eb50_file is None:
                self.text_display.append(f"Missing file: calibration EB-50 file")
            if self.sys_eb50_file is None:
                self.text_display.append(f"Missing file: customer EB-50 file")

    @Slot()
    def printGraphs(self):
        self.graph_display.clear()
        comparison_graph = self.calcs.getGraphs()
        self.graph_display.addTab(comparison_graph, "Comparison Graph")

    @Slot()
    def add_to_frequency(self):
        freq = self.calcs.get_freq()
        self.text_display.append(f"Adding {freq} Hz values to dictionary...\n")
        freq_dict = {}
        freq_dict["vol2press"] = [0, self.r_value, 0]
        freq_dict["TxAxialFocalDiameter"] = float(self.axial_field.text())
        freq_dict["TxLateralFocalDiameter"] = float(self.lateral_field.text())
        freq_dict["offset"] = self.offset_field.text()
        self.values_dict[freq] = freq_dict

    @Slot()
    def create_yaml(self):
        available_frequencies = [key for key in self.values_dict if type(key) is float] # gets a list of the existing frequencies in the field 
        self.values_dict["txAvailableFrequencies"] = available_frequencies
        self.values_dict["impedance_fund"] = float(self.impedance_field.text())
        self.values_dict["phase_fund"] = float(self.phase_field.text())
        self.values_dict["PCD_freq"] = float(self.diameter_field.text())
        self.values_dict["txDiameter"] = float(self.focal_point_field.text())

        with open(self.save_location, 'wt', encoding='utf8') as f:
            self.text_display.append(f"Writing dictionary to {self.save_location}...\n")
            yaml.dump(self.values_dict, f, default_flow_style=None)

