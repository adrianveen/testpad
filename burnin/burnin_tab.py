from burnin.burnin_graph import BurninGraph
from burnin.burnin_stats import BurninStats

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import os

class myQwidget(QWidget):
    def __init__(self, burnin_graph: BurninGraph):
        super().__init__()
        self.graph = burnin_graph

    def resizeEvent(self, event):
        self.graph.got_resize_event()

class BurninTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        # user interaction area 
        selections_group = QGroupBox()
        self.select_burnin_file_btn = QPushButton("SELECT BURN-IN FILE")        # checkbox for selecting burn-in file
        self.select_burnin_file_btn.clicked.connect(lambda: self.openFileDialog("burn"))
        # check box for summary statistics
        self.print_statistics_lbl = QLabel("Print Summary Statistics:")       # checkbox for printing statistics
        self.print_statistics_box = QCheckBox()
        self.print_statistics_box.setChecked(False)      # default for printing statistics is unchecked
        # check box to show separated error values by direction
        self.separate_errors_lbl = QLabel("Show error values separated by direction:")       # checkbox for separated error values
        self.separate_errors_box = QCheckBox()
        self.separate_errors_box.setChecked(False)      # default for separated error values is unchecked
        # check box to show moving avg with separate graphs
        self.moving_avg_lbl = QLabel("Add moving average:")       # checkbox for adding a moving average
        self.moving_avg_box = QCheckBox()
        self.moving_avg_box.setChecked(False)      # default for adding moving avg is unchecked
        # button to print graphs (this prints all selected graphs)
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #73A89E")
        self.print_graph_btn.clicked.connect(self.printGraphs)

        #layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_burnin_file_btn, 0, 0, 1, 2)
        # add print statistics label and checkbox
        selections_layout.addWidget(self.print_statistics_lbl, 1, 0)
        selections_layout.addWidget(self.print_statistics_box, 1, 1)
        # box to show separated error values by direction
        selections_layout.addWidget(self.separate_errors_lbl, 2, 0)
        selections_layout.addWidget(self.separate_errors_box, 2, 1)
        # add moving avg label and checkbox
        selections_layout.addWidget(self.moving_avg_lbl, 3, 0)
        selections_layout.addWidget(self.moving_avg_box, 3, 1)
        #print graph button - all figures produced with this button
        selections_layout.addWidget(self.print_graph_btn, 4, 0, 1, 2)
        selections_group.setLayout(selections_layout)

        self.text_display = QTextBrowser()

        self.graph_display = QTabWidget()

        # organizes layout in grid
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

        self.burnin = BurninGraph(self.burnin_file, [self.moving_avg_box.isChecked(),self.separate_errors_box.isChecked()])
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

        # Update text display with axis-specific and test number message. Call printStats() as well
        if self.print_statistics_box.isChecked():
            self.text_display.append(f"Summary Statistics for: {axis_name}; test no. {test_number}:\n")
            self.stats.printStats()
            
        burn_graph = self.burnin.getGraph()
        nav_tool = NavigationToolbar(burn_graph)

        burn_widget = myQwidget(burnin_graph=self.burnin)
        burn_widget.setContentsMargins(5, 5, 5, 5)
        burn_layout = QVBoxLayout()
        burn_layout.setContentsMargins(5, 5, 5, 5)
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)
        
        self.graph_display.addTab(burn_widget, "Burn-in Graph")

        # Create Tab for separated error values
        if self.separate_errors_box.isChecked():
            seperate_graph = self.burnin.getGraphs_separated()
            nav_tool_sep = NavigationToolbar(seperate_graph)
            separated_widget = myQwidget(burnin_graph=self.burnin)
            separated_widget.setContentsMargins(5, 5, 5, 5)
            separated_layout = QVBoxLayout()
            separated_layout.setContentsMargins(5, 5, 5, 5)
            separated_layout.addWidget(nav_tool_sep)
            separated_layout.addWidget(seperate_graph)
            separated_widget.setLayout(separated_layout)

            self.graph_display.addTab(separated_widget, "Error vs Time with directions separated")
        else:
            pass

        # add tab for positive error and negative error if moving average is checked
        if self.moving_avg_box.isChecked():
            # call movingAvg() function from BurninGraph class
            pos_avg, neg_avg = self.burnin.movingAvg()

            # create tab for positive error values
            nav_tool_pos = NavigationToolbar(pos_avg)
            
            pos_error_widget = myQwidget(burnin_graph=self.burnin)
            pos_error_widget.setContentsMargins(5, 5, 5, 5)
            pos_error_layout = QVBoxLayout()
            pos_error_layout.setContentsMargins(5, 5, 5, 5)
            pos_error_layout.addWidget(nav_tool_pos)
            pos_error_layout.addWidget(pos_avg)
            pos_error_widget.setLayout(pos_error_layout)

            self.graph_display.addTab(pos_error_widget, "Positive Error w/ Moving Avg")

            # create tab for negative error values
            nav_tool_neg = NavigationToolbar(neg_avg)

            neg_error_widget = myQwidget(burnin_graph=self.burnin)
            neg_error_widget.setContentsMargins(5, 5, 5, 5)
            neg_error_layout = QVBoxLayout()
            neg_error_layout.setContentsMargins(5, 5, 5, 5)
            neg_error_layout.addWidget(nav_tool_neg)
            neg_error_layout.addWidget(neg_avg)
            neg_error_widget.setLayout(neg_error_layout)

            self.graph_display.addTab(neg_error_widget, "Negative Error w/ Moving Avg")
        else:
            pass
