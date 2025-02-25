from hydrophone.hydrophone_graph import HydrophoneGraph

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import yaml
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class SweepGraphTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.scan_data_hdf5 = None
        self.file_save_location = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # select file button
        self.select_file_btn = QPushButton("SELECT HYDROPHONE HDF5 FILE")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("hdf5"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.create_graph())

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_file_btn, 0, 0, 1, 2)
        selections_layout.addWidget(self.print_graph_btn, 1, 0, 1, 2)
        buttons_groupbox.setLayout(selections_layout)

        # TEXT CONSOLE
        self.text_display = QTextBrowser()

        # GRAPH DISPLAY 
        self.time_domain_tab = QTabWidget()
        self.fft_tab = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.time_domain_tab, 0, 1, 2, 1)
        main_layout.addWidget(self.fft_tab, 0, 2, 2, 1)
        self.setLayout(main_layout)
    
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "hdf5": # open scan data hdf5 
            self.dialog1 = QFileDialog(self)

            self.dialog1.setFileMode(QFileDialog.ExistingFiles)
            self.dialog1.setWindowTitle("Scan Data HDF5 Files")

            self.dialog1.setNameFilter("*.hdf5")
            self.dialog1.setDefaultSuffix("hdf5") # default suffix of hdf5
            
            if self.dialog1.exec(): 
                self.text_display.append("Scan Data HDF5 File: ")
                self.scan_data_hdf5 = self.dialog1.selectedFiles()
                for file in self.scan_data_hdf5:
                    self.text_display.append(file +"\n")
        
        # NOT IMPLEMENTED YET
        elif d_type == "save": # save graph SVG location 
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            # self.dialog.setDefaultSuffix("*.txt")
            self.dialog.setFileMode(QFileDialog.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location+"\n")
    
    # @Slot()
    # def create_graph(self):
    #     if self.scan_data_hdf5 is not None:
    #         self.time_domain_tab.clear()

    #         scan_data_object = HydrophoneGraph(self.scan_data_hdf5)
    #         graph = scan_data_object.get_graphs(self.trace_no.value()) 
            
    #         nav_tool = NavigationToolbar(graph)

    #         graph_widget = QWidget()
    #         burn_layout = QVBoxLayout()
    #         burn_layout.addWidget(nav_tool)
    #         burn_layout.addWidget(graph)
    #         graph_widget.setLayout(burn_layout)

    #         self.time_domain_tab.addTab(graph_widget, "Scan Data Time Domain")

    #         #self.text_display.append("Transducer Serial Number: " + scan_data_object.tx_serial_no + "\n")
    #         # Debugging statements
    #         # print(f"save_box is checked: {self.save_box.isChecked()}")
    #         # if self.file_save_location is not None:
    #         #   print(f"file_save_location: {self.file_save_location}")

    #     else:
    #         self.text_display.append("Error: No hydrophone data .csv file found.\n")