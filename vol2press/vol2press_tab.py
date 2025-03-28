from vol2press.vol2press_calcs import Vol2Press

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget, QSizePolicy)
import numpy as np
import yaml
import os
import decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from transducer.add_ncycle_sweep_data_to_config_file import add_ncycle_sweep_to_transducer_file

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
        self.transducer_field.setText("600")
        impedance_label = QLabel("impedance_fund [\u03A9]")
        self.impedance_field = QLineEdit()
        self.impedance_field.setPlaceholderText("50")
        self.impedance_field.setText("50")
        phase_label = QLabel("phase_fund [\u00B0]")
        self.phase_field = QLineEdit()
        self.phase_field.setPlaceholderText("0")
        self.phase_field.setText("0")
        pcd_label = QLabel("PCD_freq [Hz]")
        self.pcd_field = QLineEdit()
        diameter_label = QLabel("txDiameter [mm]")
        self.diameter_field = QLineEdit()
        self.diameter_field.setText("35")
        focal_point_label = QLabel("txFocalPointFactor")
        self.focal_point_field = QLineEdit()
        self.focal_point_field.setText("0.7")

        self.one_time_fields_list = [self.transducer_field, self.impedance_field, self.phase_field, self.pcd_field, self.diameter_field, self.focal_point_field]

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
        freq_label = QLabel("Frequency [MHz]")
        self.freq_field = QLineEdit()
        self.freq_field.setText("0.550")
        freq_affix = QComboBox()
        freq_affix.addItems(["MHz, kHz"])
        freq_affix.setCurrentText("MHz")
        axial_len_label = QLabel("TxAxialFocalDiameter [mm]")
        self.axial_field = QLineEdit()
        self.axial_field.setText("16.5")
        lateral_len_label = QLabel("TxLateralFocalDiameter [mm]")
        self.lateral_field = QLineEdit()
        self.lateral_field.setText("2.5")
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
        uni_cali_label = QLabel("unified_vol2press [MPa/Vpp]")
        self.uni_cali_field = QLineEdit()
        self.uni_cali_field.setPlaceholderText("0.08")

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

        cycles_checkbox = QCheckBox("INCLUDE N CYCLES DATA:")
        cycles_checkbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.browse_ncycles_data = QPushButton("SELECT N CYCLES FOLDER")
        self.browse_ncycles_data.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.browse_ncycles_data.clicked.connect(lambda: self.openFileDialog("n_cycles"))
        self.browse_ncycles_data.setEnabled(False)
        cycles_checkbox.toggled.connect(self.browse_ncycles_data.setEnabled)
        # Add each widget to its own cell in the grid layout, centered in its cell.
        self.results_btn = QPushButton("PRINT TO YAML")
        self.results_btn.setStyleSheet("background-color: #74BEA3")
        self.results_btn.clicked.connect(lambda: self.create_yaml())
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
        main_layout.setColumnStretch(1, 1)
        main_layout.setColumnStretch(2, 2)
        main_layout.addWidget(selections_group, 0, 0, 1, 2)
        main_layout.addWidget(single_fields_group, 1, 0, 1, 2)
        main_layout.addWidget(freq_fields_group, 2, 0, 1, 2)
        main_layout.addWidget(self.add_to_yaml_btn, 3, 0, 1, 2)
        main_layout.addWidget(cycles_checkbox, 4, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.browse_ncycles_data, 4, 1, 1, 1)
        main_layout.addWidget(self.results_btn, 5, 0, 1, 2)
        main_layout.addWidget(clear_btn, 6, 0, 1, 2)
        main_layout.addWidget(console_box, 7, 0, 1, 2)
        main_layout.addWidget(self.graph_display, 0, 2, 8, 2)

        self.setLayout(main_layout)

    @Slot()
    # file dialog boxes to select sweep/calibration eb-50/customer eb-50 files/a save location
    def openFileDialog(self, d_type):
        if d_type == "sweep":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Sweep File")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
            self.dialog1.setNameFilter("Text Files (*.txt)")
            self.dialog1.setDefaultSuffix("txt")  # default suffix

            # Set the default directory if it exists
            default_dir = r"G:\Shared drives\FUS_Team\Transducers Calibration and RFB"
            if os.path.isdir(default_dir):
                self.dialog1.setDirectory(default_dir)
            
            if self.dialog1.exec():
                self.text_display.append("Sweep File: ")
                self.sweep_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sweep_file + "\n")
                self.enable_btn()  # enable the new frequency to be added to the YAML

        elif d_type == "eb-50_cal":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Calibration EB-50 File")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
            self.dialog1.setNameFilter("YAML Files (*.yaml)")
            self.dialog1.setDefaultSuffix("yaml")  # default suffix of yaml

            # Specify the desired initial directory.
            specified_path = r"G:\Shared drives\FUS_Team\Siglent.And.EB-50-Calibration\eb-50_yaml\2183-eb50"
            if os.path.isdir(specified_path):
                self.dialog1.setDirectory(specified_path)
            # Otherwise, QFileDialog will use its default directory.

            if self.dialog1.exec():
                self.text_display.append("Calibration EB-50 File: ")
                self.cal_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.cal_eb50_file + "\n")


        elif d_type == "eb-50_sys":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Customer EB-50 File")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
            self.dialog1.setNameFilter("YAML Files (*.yaml)")
            self.dialog1.setDefaultSuffix("yaml")  # default suffix of yaml

            # Specify the desired default directory
            specified_path = r"G:\Shared drives\FUS_Team\Siglent.And.EB-50-Calibration\eb-50_yaml"
            if os.path.isdir(specified_path):
                self.dialog1.setDirectory(specified_path)
            
            if self.dialog1.exec():
                self.text_display.append("Customer EB-50 File: ")
                self.sys_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sys_eb50_file + "\n")

        elif d_type == "n_cycles":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("N Cycles Data")
            # Set the file mode to Directory so only folders can be selected
            self.dialog1.setFileMode(QFileDialog.Directory)
            # Ensure that only directories are shown
            self.dialog1.setOption(QFileDialog.ShowDirsOnly, True)
            
            if self.dialog1.exec():
                selected_dir = self.dialog1.selectedFiles()[0]
                # Now store the selected directory and its parent directory
                self.n_cycles_dir = selected_dir
                self.n_cycles_parent_dir = os.path.dirname(selected_dir)
                self.text_display.append("N Cycles Data: " + selected_dir + "\n")

        elif d_type == "save":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setNameFilter("YAML Files (*.yaml)")
            self.dialog1.setDefaultSuffix("yaml")  # default suffix of yaml
            self.dialog1.setWindowTitle("YAML Save Location")
            self.dialog1.setFileMode(QFileDialog.FileMode.AnyFile)
            if self.dialog1.exec():
                selected_file = self.dialog1.selectedFiles()[0]
                # If a directory is selected, append a default file name.
                if os.path.isdir(selected_file):
                    selected_file = os.path.join(selected_file, "default_config.yaml")
                self.save_file_path = selected_file          # Full file path (directory + file name)
                self.save_location = os.path.dirname(selected_file)  # Just the directory
                self.config_filename = os.path.basename(selected_file)  # Just the file name
                self.text_display.append("Save Location: " + self.save_location + "\n")
                self.text_display.append("Config File Name: " + self.config_filename + "\n")

    # disable the add frequency button 
    def disable_btn(self):
        self.add_to_yaml_btn.setEnabled(False)
    
    # enable the add frequency button 
    def enable_btn(self):
        self.add_to_yaml_btn.setEnabled(True)

    # clear previous frequency data (useful for creating data for new transducer)
    def clear_dicts(self):
        qReply = QMessageBox.question(
            self,
            'Confirm Clear',
            'Are you sure you want to clear all previously stored frequency data?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if qReply == QMessageBox.StandardButton.Yes:  # if user says yes, clear previous dicts
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
            self.printGraphs(dataset=self.calcs)
            self.add_to_frequency()
        else:
            if self.sweep_file is None:
                self.text_display.append(f"Missing file: sweep file")
            if self.cal_eb50_file is None:
                self.text_display.append(f"Missing file: calibration EB-50 file")
            if self.sys_eb50_file is None:
                self.text_display.append(f"Missing file: customer EB-50 file")

    # print the graphs
    @Slot()
    def printGraphs(self, dataset):
        self.graph_display.clear()
        comparison_graph = self.calcs.getGraphs()
        self.graph_display.addTab(comparison_graph, "Comparison Graph")

    # add data to a dictionary 
    def add_to_dict(self, key, value, dictionary):
        if value != '':
            if key == "offset":
                dictionary[key] = np.array([float(value[0]), float(value[1]), float(value[2])]).tolist()
            elif key == "vol2press":
                dictionary[key] = [0, value, 0]
            else:
                dictionary[key] = float(value)

    # add frequency data to frequency dictionary 
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

    # create a yaml file with all dictionaries 
    @Slot()
    def create_yaml(self):
        available_frequencies = np.array([key for key in self.freq_dict if type(key) is float]).tolist() # gets a list of the existing frequencies in the field 
        self.values_dict["txAvailableFrequencies"] = available_frequencies

        self.add_to_dict("impedance_fund", self.impedance_field.text(), self.values_dict)
        self.add_to_dict("phase_fund", self.phase_field.text(), self.values_dict)
        self.add_to_dict("PCD_freq", self.pcd_field.text(), self.values_dict)
        self.add_to_dict("txDiameter", self.diameter_field.text(), self.values_dict)
        self.add_to_dict("txFocalPointFactor", self.focal_point_field.text(), self.values_dict)

        self.values_dict = self.values_dict | self.freq_dict # ensure that all frequency dictionary values are placed at the end 
        self.summary_dict = {}
        self.summary_dict[self.transducer_field.text()] = self.values_dict

        with open(self.save_file_path, 'wt', encoding='utf8') as f:
            full_path = os.path.join(self.save_location, self.config_filename)
            self.text_display.append(f"Writing dictionary to {full_path}...\n")
            yaml.dump(self.summary_dict, f, default_flow_style=None, sort_keys=False)
            self.text_display.append("Writing to dictionary complete.")

        self.n_cycles_plot_data = add_ncycle_sweep_to_transducer_file(self.n_cycles_dir, self.save_file_path)
        
        self.plot_ncycle_data(self.n_cycles_plot_data)

    def plot_ncycle_data(self, plot_data = list):
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)
        # store frequencies in a list
        frequencies = []
        for freq, cycles, pressure in plot_data:
            self.ax.plot(cycles, pressure, label=f"{freq} MHz")

        self.ax.set_xlabel("Cycle Number")
        self.ax.set_ylabel("Normalized Pressure (MPA)")
        self.ax.legend(title="Frequency")
        self.ax.grid(True)
        self.ax.set_title("N Cycles Data")
        self.fig.set_canvas(self.canvas)
        self.graph_display.addTab(self.canvas, "N Cycles Data")
        self.graph_display.setCurrentWidget(self.canvas)


    
    # def resizeEvent(self, event):
    #     """
    #     Override resizeEvent to force the 'SELECT N CYCLES DATA' button
    #     to be half the width of the 'PRINT TO YAML' button.
    #     """
    #     super().resizeEvent(event)
    #     # Measure the PRINT TO YAML button’s current width
    #     full_width = self.results_btn.width()
    #     # Set the N cycles button to half that width
    #     self.browse_ncycles_data.setFixedWidth(full_width // 2)