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

        # BUTTONS 
        selections_group = QGroupBox("File Selections")
        cal_eb50_file_btn = QPushButton("SELECT CALIBRATION EB-50 YAML")
        cal_eb50_file_btn.clicked.connect(lambda: self.openFileDialog("eb-50_cal"))
        sys_eb50_file_btn = QPushButton("SELECT CUSTOMER EB-50 YAML")
        sys_eb50_file_btn.clicked.connect(lambda: self.openFileDialog("eb-50_sys"))
        sweep_btn = QPushButton("SELECT SWEEP TXT")
        sweep_btn.clicked.connect(lambda: self.openFileDialog("sweep"))
        results_btn = QPushButton("GET RESULTS")
        results_btn.setStyleSheet("background-color: #74BEA3")
        results_btn.clicked.connect(lambda: self.get_calcs())

        selections_layout = QGridLayout()
        selections_layout.addWidget(cal_eb50_file_btn, 0, 0)
        selections_layout.addWidget(sys_eb50_file_btn, 1, 0)
        selections_layout.addWidget(sweep_btn, 2, 0)
        selections_layout.addWidget(results_btn, 3, 0)
        selections_group.setLayout(selections_layout)

        # TEXT CONSOLE 
        console_box = QGroupBox("Console Output")
        self.text_display = QTextBrowser()
        console_layout = QGridLayout()
        console_layout.addWidget(self.text_display)
        console_box.setLayout(console_layout)
        
        # GRAPH
        self.graph_display = QTabWidget()

        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.addWidget(selections_group, 0, 0)
        main_layout.addWidget(console_box, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 2, 1)

        self.setLayout(main_layout)

    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "sweep":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Sweep File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            if self.dialog1.exec(): 
                self.text_display.append("Sweep File: ")
                self.sweep_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sweep_file+"\n")
        elif d_type == "eb-50_cal":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Calibration EB-50 File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            if self.dialog1.exec(): 
                self.text_display.append("Calibration EB-50 File: ")
                self.cal_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.cal_eb50_file+"\n")
        elif d_type == "eb-50_sys":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Customer EB-50 File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            if self.dialog1.exec(): 
                self.text_display.append("Customer EB-50 File: ")
                self.sys_eb50_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sys_eb50_file+"\n")

    @Slot()
    def get_calcs(self):
        if self.sweep_file is not None and self.cal_eb50_file is not None and self.sys_eb50_file is not None:
            self.calcs = Vol2Press(self.cal_eb50_file, self.sys_eb50_file, self.sweep_file)
            self.text_display.append(f"Regression value: {self.calcs.return_B_value():.4f} MPa/Vpp\n")
            self.printGraphs()
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
        # print(self.selected_data_files, self.selected_save_folder)
        # variables_dict = [self.selected_data_files, self.save_graph.isChecked(), self.selected_save_folder, self.x_graph_box.isChecked(), self.y_graph_box.isChecked(), self.z_graph_box.isChecked()]
        comparison_graph = self.calcs.getGraphs()
        self.graph_display.addTab(comparison_graph, "Comparison Graph")


