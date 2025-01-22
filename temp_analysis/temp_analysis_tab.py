# from vol2press.vol2press_calcs import Vol2Press
from temp_analysis.temperature_graph import TemperatureGraph

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import yaml
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class TempAnalysisTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.temperature_data_files = None
        self.file_save_location = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # compare checkbox
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setChecked(False)
        # select file button
        self.select_file_btn = QPushButton("SELECT TEMPERATURE .CSV FILE")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("csv"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.create_graph())

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.compare_label, 0, 0)
        selections_layout.addWidget(self.compare_box, 0, 1)
        selections_layout.addWidget(self.select_file_btn, 1, 0, 1, 2)
        selections_layout.addWidget(self.print_graph_btn, 2, 0, 1, 2)
        buttons_groupbox.setLayout(selections_layout)

        # TEXT CONSOLE
        self.text_display = QTextBrowser()

        # GRAPH DISPLAY 
        self.graph_tab = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_tab, 0, 1, 2, 1)
        self.setLayout(main_layout)
    
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "csv": # open nanobubble txt 
            self.dialog1 = QFileDialog(self)
            
            if self.compare_box.isChecked():
                self.dialog1.setFileMode(QFileDialog.ExistingFiles)
                self.dialog1.setWindowTitle("Temperature Data CSV Files")
            else:
                self.dialog1.setFileMode(QFileDialog.ExistingFile)
                self.dialog1.setWindowTitle("Temperature Data CSV File")

            self.dialog1.setNameFilter("*.csv")
            self.dialog1.setDefaultSuffix("csv") # default suffix of yaml
            
            if self.dialog1.exec(): 
                self.text_display.append("Temperature Data File(s): ")
                self.temperature_data_files = self.dialog1.selectedFiles()
                for file in self.temperature_data_files:
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
    
    @Slot()
    def create_graph(self):
        if self.temperature_data_files is not None:
            self.graph_tab.clear()

            temperature_object = TemperatureGraph(self.temperature_data_files)
            graph = temperature_object.get_graphs(self.compare_box.isChecked())
            
            nav_tool = NavigationToolbar(graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Temperature Graph")

            # Debugging statements
            # print(f"save_box is checked: {self.save_box.isChecked()}")
            # if self.file_save_location is not None:
            #   print(f"file_save_location: {self.file_save_location}")

        else:
            self.text_display.append("Error: No temperature .csv file found.\n")