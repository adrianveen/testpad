from vol2press.vol2press_calcs import Vol2Press

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
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
        self.freq_dict = {}

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
        transducer_label = QLabel("Transducer Serial No.")
        self.transducer_field = QLineEdit()
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

        self.one_time_fields_list = [self.transducer_field, self.impedance_field, self.phase_field, self.pcd_field, self.focal_point_field]

        single_fields_layout = QGridLayout()
        single_fields_layout.setColumnStretch(0, 1)
        single_fields_layout.setColumnStretch(1, 1)
        single_fields_layout.addWidget(transducer_label, 0, 0)
        single_fields_layout.addWidget(self.transducer_field, 0, 1)
        single_fields_layout.addWidget(impedance_label, 1, 0)
        single_fields_layout.addWidget(self.impedance_field, 1, 1)
        single_fields_layout.addWidget(phase_label, 2, 0)
        single_fields_layout.addWidget(self.phase_field, 2, 1)
        single_fields_layout.addWidget(pcd_label, 3, 0)
        single_fields_layout.addWidget(self.pcd_field, 3, 1)
        single_fields_layout.addWidget(diameter_label, 4, 0)
        single_fields_layout.addWidget(self.diameter_field, 4, 1)
        single_fields_layout.addWidget(focal_point_label, 5, 0)
        single_fields_layout.addWidget(self.focal_point_field, 5, 1)
        single_fields_group.setLayout(single_fields_layout)

        # FIELDS PER FREQUENCY 
        freq_fields_group = QGroupBox("Info Per Frequency")
        sweep_btn = QPushButton("SELECT SWEEP TXT")
        sweep_btn.clicked.connect(lambda: self.openFileDialog("sweep"))
        freq_label = QLabel("Frequency (MHz)")
        self.freq_field = QLineEdit()
        freq_affix = QComboBox()
        freq_affix.addItems(["MHz, kHz"])
        freq_affix.setCurrentText("MHz")
        axial_len_label = QLabel("TxAxialFocalDiameter")
        self.axial_field = QLineEdit()
        lateral_len_label = QLabel("TxLateralFocalDiameter")
        self.lateral_field = QLineEdit()
        offset_label = QLabel("offset")
        offset_widget = QWidget()
        offset_widget.setContentsMargins(0, 0, 0, 0)
        offset_layout = QHBoxLayout()
        offset_layout.setContentsMargins(0, 0, 0, 0)
        self.offset_field_1 = QLineEdit()
        self.offset_field_1.setText("0")
        self.offset_field_1.setPlaceholderText("0")
        self.offset_field_2 = QLineEdit()
        self.offset_field_2.setText("0")
        self.offset_field_2.setPlaceholderText("0")
        self.offset_field_3 = QLineEdit()
        self.offset_field_3.setText("0")
        self.offset_field_3.setPlaceholderText("0")
        offset_layout.addWidget(self.offset_field_1)
        offset_layout.addWidget(self.offset_field_2)
        offset_layout.addWidget(self.offset_field_3)
        offset_widget.setLayout(offset_layout)
        uni_cali_label = QLabel("unified_vol2press")
        self.uni_cali_field = QLineEdit()

        self.fields_list = [self.freq_field, self.axial_field, self.lateral_field, self.offset_field_1, \
                            self.offset_field_2, self.offset_field_3, self.uni_cali_field]

        for field in self.fields_list:
            field.textChanged.connect(lambda: self.enable_btn())

        fields_layout = QGridLayout()
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)
        fields_layout.addWidget(sweep_btn, 0, 0, 1, 2)
        fields_layout.addWidget(freq_label, 1, 0)
        fields_layout.addWidget(self.freq_field, 1, 1)
        fields_layout.addWidget(axial_len_label, 2, 0)
        fields_layout.addWidget(self.axial_field, 2, 1)
        fields_layout.addWidget(lateral_len_label, 3, 0)
        fields_layout.addWidget(self.lateral_field, 3, 1)
        fields_layout.addWidget(offset_label, 4, 0)
        fields_layout.addWidget(offset_widget, 4, 1)
        fields_layout.addWidget(uni_cali_label, 5, 0)
        fields_layout.addWidget(self.uni_cali_field, 5, 1)
        freq_fields_group.setLayout(fields_layout)

        # RESULTS BUTTONS
        self.add_to_yaml_btn = QPushButton("ADD FREQUENCY INFORMATION")
        self.add_to_yaml_btn.setStyleSheet("QPushButton:disabled {color: gray}")
        self.add_to_yaml_btn.clicked.connect(lambda: self.disable_btn())
        self.add_to_yaml_btn.clicked.connect(lambda: self.get_calcs())
        results_btn = QPushButton("PRINT TO YAML")
        results_btn.setStyleSheet("background-color: #74BEA3")
        results_btn.clicked.connect(lambda: self.create_yaml())
        clear_btn = QPushButton("CLEAR DATA")
        clear_btn.clicked.connect(lambda: self.clear_dicts())
        clear_btn.clicked.connect(lambda: self.enable_btn())

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
        main_layout.addWidget(clear_btn, 5, 0)
        main_layout.addWidget(console_box, 6, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 7, 1)

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

    def clear_dicts(self):
        qReply = QMessageBox.question(
            self,
            'Confirm Clear',
            'Are you sure you want to clear all previously stored frequency data?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if qReply == QMessageBox.Yes:  # if user says yes, clear previous dicts
            self.freq_dict = {}
            self.values_dict = {}
            self.summary_dict = {}
            self.text_display.append("Previous frequency data cleared.\n")
        

    @Slot()
    # return calc values 
    def get_calcs(self):
        if self.sweep_file is not None and self.cal_eb50_file is not None and self.sys_eb50_file is not None:
            self.calcs = Vol2Press(self.cal_eb50_file, self.sys_eb50_file, self.sweep_file, float(self.freq_field.text()))
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

    def add_to_dict(self, key, value, dictionary):
        if value != '':
            if key == "offset":
                dictionary[key] = np.array([float(value[0]), float(value[1]), float(value[2])]).tolist()
            elif key == "vol2press":
                dictionary[key] = value
            else:
                dictionary[key] = float(value)

    @Slot()
    def add_to_frequency(self):
        freq = float(self.freq_field.text())*1000000 # MHz to Hz
        self.text_display.append(f"Adding {freq} Hz information to dictionary...\n")
        spec_freq_dict = {}
        self.add_to_dict("vol2press", self.r_value, spec_freq_dict)
        self.add_to_dict("TxAxialFocalDiameter", self.axial_field.text(), spec_freq_dict)
        self.add_to_dict("TxLateralFocalDiameter", self.lateral_field.text(), spec_freq_dict)
        self.add_to_dict("offset", [self.offset_field_1.text(), self.offset_field_2.text(), self.offset_field_3.text()], spec_freq_dict)
        self.add_to_dict("unified_vol2press", self.uni_cali_field.text(), spec_freq_dict)

        self.freq_dict[freq] = spec_freq_dict

    @Slot()
    def create_yaml(self):
        available_frequencies = np.array([key for key in self.freq_dict if type(key) is float]).tolist() # gets a list of the existing frequencies in the field 
        self.values_dict["txAvailableFrequencies"] = available_frequencies

        self.add_to_dict("impedance_fund", self.impedance_field.text(), self.values_dict)
        self.add_to_dict("phase_fund", self.phase_field.text(), self.values_dict)
        self.add_to_dict("PCD_freq", self.pcd_field.text(), self.values_dict)
        self.add_to_dict("txDiameter", self.focal_point_field.text(), self.values_dict)

        self.values_dict = self.values_dict | self.freq_dict # ensure that all frequency dictionary values are placed at the end 
        self.summary_dict = {}
        self.summary_dict[self.transducer_field.text()] = self.values_dict

        with open(self.save_location, 'wt', encoding='utf8') as f:
            self.text_display.append(f"Writing dictionary to {self.save_location}...\n")
            yaml.dump(self.summary_dict, f, default_flow_style=None, sort_keys=False)

