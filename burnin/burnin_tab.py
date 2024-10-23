from burnin.burnin_graph import BurninGraph
from burnin.burnin_stats import BurninStats

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import os

class BurninTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        # user interaction area 
        selections_group = QGroupBox()
        self.select_burnin_file_btn = QPushButton("SELECT BURN-IN FILE")        # checkbox for selecting burn-in file
        self.select_burnin_file_btn.clicked.connect(lambda: self.openFileDialog("burn"))
        
        self.print_statistics_lbl = QLabel("Print Summary Statistics?")       # checkbox for printing statistics
        self.print_statistics_box = QCheckBox()
        self.print_statistics_box.setChecked(False)      # default for printing statistics is unchecked
        
        self.moving_avg_lbl = QLabel("Add moving average?")       # checkbox for adding a moving average
        self.moving_avg_box = QCheckBox()
        self.moving_avg_box.setChecked(False)      # default for adding moving avg is unchecked

        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(self.printGraphs)

        #layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_burnin_file_btn, 0, 0, 1, 2)
        
        selections_layout.addWidget(self.print_statistics_lbl, 1, 0)
        selections_layout.addWidget(self.print_statistics_box, 1, 1)
        
        selections_layout.addWidget(self.moving_avg_lbl, 2, 0)
        selections_layout.addWidget(self.moving_avg_box, 2, 1)

        selections_layout.addWidget(self.print_graph_btn, 3, 0, 1, 2)
        selections_group.setLayout(selections_layout)

        self.text_display = QTextBrowser()

        self.graph_display = QTabWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(selections_group, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 2, 1)
        self.setLayout(main_layout)

    @Slot()
    # file dialog boxes 
    def openFileDialog(self, d_type):
        default_path = r"G:\Shared drives\FUS_Team\RK300 Software Testing\Software Releases\rk300_program_v2.9.1"    

        #check if default path exists, otherwise set to home directory
        if not os.path.exists(default_path):
            default_path = os.path.expanduser("~")

        if d_type == "burn":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Burn-in File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.hdf5")

            #set default directory
            self.dialog1.setDirectory(default_path)

            if self.dialog1.exec(): 
                self.text_display.append("Burn-in File: ")
                self.burnin_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.burnin_file+ "\n")

        elif d_type == "save": # not including save anymore because graph of burn-in is already saved as SVG 
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Save Folder")
            self.dialog1.setFileMode(QFileDialog.Directory)

            #set default directory
            self.dialog1.setDirectory(default_path)

            if self.dialog1.exec(): 
                self.text_display.append("Save Folder: ")
                self.save_folder = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.save_folder+"\n")

    # prints burn-in graph with navigation tool bar to pan/zoom
    def printGraphs(self):
        self.graph_display.clear()

        self.burnin = BurninGraph(self.burnin_file)
        self.stats = BurninStats(self.burnin_file, self.text_display)

        # Determine the axis name based on the filename
        if "_axis_A_" in self.burnin_file:
            axis_name = "Axis A"
        elif "_axis_B_" in self.burnin_file:
            axis_name = "Axis B"
        else:
            axis_name = "Unknown Axis"

        # Extract the test number after the last underscore
        try:
            test_number = self.burnin_file.split('_')[-1].split('.')[0]  # Split by underscore and get the last part, then remove file extension
        except IndexError:
            test_number = "Unknown"

        # Update text display with axis-specific and test number message
        self.text_display.append(f"Summary Statistics for: {axis_name}; test no. {test_number}:\n")

        # check if print statistics is checked and call printStats() if it is
        if self.print_statistics_box.isChecked():
            self.stats.printStats()

        # check if moving average is checked and call movingAvg() if it is
        # if self.moving_avg_box.isChecked():
        #     self.burnin.movingAvg()

        burn_graph = self.burnin.getGraph()
        seperate_graph = self.burnin.getGraphs_separated()
        nav_tool = NavigationToolbar(burn_graph)
        # nav_tool_A = NavigationToolbar(burn_graph_A)
        nav_tool_2 = NavigationToolbar(seperate_graph)

        burn_widget = QWidget()
        burn_layout = QVBoxLayout()
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)

        self.graph_display.addTab(burn_widget, "Burn-in Graph")

        # Create Tab for separated error values
        separated_widget = QWidget()
        separated_layout = QVBoxLayout()
        separated_layout.addWidget(nav_tool_2)
        separated_layout.addWidget(seperate_graph)
        separated_widget.setLayout(separated_layout)

        self.graph_display.addTab(separated_widget, "Error vs Time with directions separated")

        # add tab for positive error and negative error if moving average is checked
        if self.moving_avg_box.isChecked():
            # call movingAvg() function from BurninGraph class
            

            # create tab for positive error values
            nav_tool_pos = NavigationToolbar()
            
            pos_error_widget = QWidget()
            pos_error_layout = QVBoxLayout()
            pos_error_layout.addWidget(nav_tool_pos)
        # # Create Motor B Tab
        # motor_b_widget = QWidget()
        # motor_b_layout = QVBoxLayout()
        # #motor_b_layout.addWidget(nav_tool)
        # motor_b_widget.setLayout(motor_b_layout)

        # self.graph_display.addTab(motor_b_widget, "Motor B")
        

