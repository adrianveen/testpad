from hydrophone.hydrophone_graph import HydrophoneGraph

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import yaml
from datetime import datetime
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class HydrophoneAnalysisTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.hydrophone_scan_data = None
        self.file_save_location = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # compare checkbox
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setChecked(False)
        # select file button
        self.select_file_btn = QPushButton("SELECT HYDROPHONE CSV FILE(S)")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("csv"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.create_graph())
        # save graphs as SVG button
        self.save_as_svg_btn = QPushButton("SAVE GRAPH AS SVG")
        self.save_as_svg_btn.setEnabled(False)
        self.save_as_svg_btn.clicked.connect(lambda: self.openFileDialog("save"))

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.compare_label, 0, 0)
        selections_layout.addWidget(self.compare_box, 0, 1)
        selections_layout.addWidget(self.select_file_btn, 1, 0, 1, 2)
        selections_layout.addWidget(self.print_graph_btn, 2, 0, 1, 2)
        selections_layout.addWidget(self.save_as_svg_btn, 3, 0, 1, 2)
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
        if d_type == "csv": # open hydrophone csv 
            self.dialog1 = QFileDialog(self)
            
            if self.compare_box.isChecked():
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFiles)
                self.dialog1.setWindowTitle("Hydrophone Scan CSV Files")
            else:
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
                self.dialog1.setWindowTitle("Hydrophone Scan CSV File")

            self.dialog1.setNameFilter("*.csv")
            self.dialog1.setDefaultSuffix("csv") # default suffix of csv
            
            if self.dialog1.exec(): 
                self.text_display.append("Hydrophone Scan Data Files: ")
                self.hydrophone_scan_data = self.dialog1.selectedFiles()
                for file in self.hydrophone_scan_data:
                    self.text_display.append(file +"\n")
        
        # file saving
        elif d_type == "save": # save graph SVG location 
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location+"\n")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self.hydrophone_object.tx_serial_no}_sensitivity_vs_frequency_{timestamp}.svg"
                hydrophone_svg_path = os.path.join(self.file_save_location, file_name)

                dpi = 96
                fig_width = 6.5
                fig_height = 3.5

                self.graph.figure.set_size_inches(fig_width, fig_height)
                
                # Create dictionaries to hold the original properties
                original_marker_sizes = {}
                original_marker_edge_widths = {}
                original_line_widths = {}

                # Temporarily reduce marker size, marker edge width, and line width to 70% for saving
                for ax in self.graph.figure.get_axes():
                    for line in ax.get_lines():
                        # Save original values
                        original_marker_sizes[line] = line.get_markersize()
                        original_marker_edge_widths[line] = line.get_markeredgewidth()
                        original_line_widths[line] = line.get_linewidth()

                        # Scale plot properties to 70% of its original size
                        line.set_markersize(original_marker_sizes[line] * 0.7)
                        line.set_markeredgewidth(original_marker_edge_widths[line] * 0.7)
                        line.set_linewidth(original_line_widths[line] * 0.7)

                self.graph.figure.savefig(hydrophone_svg_path, format="svg", dpi=dpi, bbox_inches="tight", pad_inches=0)

                for ax in self.graph.figure.get_axes():
                    for line in ax.get_lines():
                        line.set_markersize(original_marker_sizes[line])
                        
                for i, data in enumerate(self.hydrophone_object.raw_data):
                    txt_file_name = f"{self.hydrophone_object.transducer_serials[i]}_sensitivity_vs_frequency_{timestamp}.txt"
                    csv_file_path = os.path.join(self.file_save_location, txt_file_name)
                    
                    # Check if data tuple has 2 or 3 elements
                    if len(data) == 2:
                        # Only frequency and sensitivity
                        data_array = np.array(data)
                        data_transposed = data_array.T
                    else:
                        # Tuple contains STD as well
                        data_array = np.array(data)
                        data_transposed = data_array.T
                        # Optionally, if STD values are all NaN, discard the column:
                        if np.all(np.isnan(data_transposed[:, 2])):
                            data_transposed = data_transposed[:, :2]
                    
                    np.savetxt(csv_file_path, data_transposed, delimiter=',', fmt='%s')
                # finished saving message
                self.text_display.append("The following files were saved:\n")
                self.text_display.append(f"Hydrophone Sensitivity Graph:")
                self.text_display.append(f"{hydrophone_svg_path}\n")
                self.text_display.append(f"Hydrophone Sensitivity Data:")
                self.text_display.append(f"{csv_file_path}\n")

    @Slot()
    def create_graph(self):
        if self.hydrophone_scan_data is not None:
            self.graph_tab.clear()
            self.save_as_svg_btn.setEnabled(True)

            self.hydrophone_object = HydrophoneGraph(self.hydrophone_scan_data)
            self.graph = self.hydrophone_object.get_graphs(self.compare_box.isChecked())
            
            nav_tool = NavigationToolbar(self.graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(self.graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Hydrophone Scan Data")

            self.text_display.append("Transducer Serial Number: " + self.hydrophone_object.tx_serial_no + "\n")
            # Debugging statements
            # print(f"save_box is checked: {self.save_box.isChecked()}")
            # if self.file_save_location is not None:
            #   print(f"file_save_location: {self.file_save_location}")

        else:
            self.text_display.append("Error: No hydrophone data .csv file found.\n")