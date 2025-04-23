from hydrophone.hydrophone_graph import HydrophoneGraph

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import yaml
import re
from datetime import datetime
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class HydrophoneAnalysisTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.hydrophone_scan_data = None
        self.file_save_location = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # combo box for single CSV or multiple CSV per transducer
        self.combo_label = QLabel("Select CSV Format:")
        self.combo_box = QComboBox()
        self.combo_box.setToolTip("Select the type of hydrophone scan data file.")
        self.combo_box.setPlaceholderText("Select CSV Format")
        self.combo_box.addItem("Multiple CSV files per transducer")
        self.combo_box.addItem("Single CSV file per transducer (legacy CSV format)")
        self.combo_box.setEditable(True)
        le: QLineEdit = self.combo_box.lineEdit()
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setReadOnly(True)

        # 3) Set the placeholder *after* it’s editable
        self.combo_box.setPlaceholderText("Select CSV Format")
        le.setPlaceholderText("Select CSV Format")   # ensure the edit itself knows

        # 4) Finally, reset to “no selection”
        self.combo_box.setCurrentIndex(-1)
        
        # compare checkbox
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setToolTip("Select to compare multiple datasets if legacy data set is being used.")
        self.compare_box.setEnabled(False) # disable for now
        self.compare_box.setChecked(False)
        self.combo_box.currentIndexChanged.connect(self.onFormatChanged)
        # select file button
        self.select_file_btn = QPushButton("SELECT HYDROPHONE CSV FILE(S)")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("csv"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.print_graphs_clicked())
        # save graphs as SVG button
        self.save_as_svg_btn = QPushButton("SAVE GRAPH AS SVG")
        self.save_as_svg_btn.setEnabled(False)
        self.save_as_svg_btn.clicked.connect(lambda: self.openFileDialog("save"))

        # Layout for user interaction area
        selections_layout = QGridLayout()

        rows = [
            (self.combo_label, self.combo_box),  # 2-cell row
            (self.compare_label, self.compare_box),  # 2-cell row
            (self.select_file_btn,),                 # 1-widget, spans 2 columns
            (self.print_graph_btn,),
            (self.save_as_svg_btn,),
        ]

        for r, cells in enumerate(rows):
            if len(cells) == 1:
                selections_layout.addWidget(cells[0], r, 0, 1, 2)
            else:                   # exactly two widgets: left + right
                selections_layout.addWidget(cells[0], r, 0)
                selections_layout.addWidget(cells[1], r, 1)
        selections_layout.setAlignment(self.compare_box, Qt.AlignmentFlag.AlignCenter)
        # selections_layout.addWidget(self.compare_label, 0, 0)
        # selections_layout.addWidget(self.compare_box, 0, 1)
        # selections_layout.addWidget(self.select_file_btn, 1, 0, 1, 2)
        # selections_layout.addWidget(self.print_graph_btn, 2, 0, 1, 2)
        # selections_layout.addWidget(self.save_as_svg_btn, 3, 0, 1, 2)
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
            
            if self.compare_box.isChecked() or self.combo_box.currentText() == "Multiple CSV files per transducer":
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

                        # Scale plot properties to 70% of its original size for saving
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

                    data_array = np.array(data)
                    data_transposed = data_array.T

                    # Convert sensitivity (column 1) from mV/MPa to V/MPa
                    data_transposed[:, 1] = data_transposed[:, 1] / 1000.0

                    # Check if a STD column is present
                    if data_transposed.shape[1] == 3:
                        # If STD values are all NaN, discard the column and use 2 columns only
                        if np.all(np.isnan(data_transposed[:, 2])):
                            data_transposed = data_transposed[:, :2]
                            fmt = ('%s', '%.5f')
                        else:
                            # Convert STD values from mV/MPa to V/MPa
                            data_transposed[:, 2] = data_transposed[:, 2] / 1000.0
                            fmt = ('%s', '%.5f', '%.5f')
                    else:
                        fmt = ('%s', '%.5f')
                    
                    np.savetxt(csv_file_path, data_transposed, delimiter=',', fmt=fmt)
                # finished saving message
                self.text_display.append("The following files were saved:\n")
                self.text_display.append(f"Hydrophone Sensitivity Graph:")
                self.text_display.append(f"{hydrophone_svg_path}\n")
                self.text_display.append(f"Hydrophone Sensitivity Data:")
                self.text_display.append(f"{csv_file_path}\n")

    @Slot()
    def print_graphs_clicked(self):
        self.hydrophone_object = HydrophoneGraph(self.hydrophone_scan_data)
        self.create_graph()

        if isinstance(self.hydrophone_object.transducer_serials, (list, np.ndarray)):
            if len(self.hydrophone_object.transducer_serials) > 1:
                self.text_display.append("Transducer Serial Numbers: ")
                for i, serial in enumerate(self.hydrophone_object.transducer_serials):
                        self.text_display.append(f"{i+1}. {serial}")
                self.text_display.append("")
            else:
                self.text_display.append(f"Transducer Serial Number: {self.hydrophone_object.transducer_serials[0]}\n")
        
        self.print_sensitivities()
   
    @Slot(int)
    def onFormatChanged(self, index: int):
        """Enable compare_box only when the second combo-item is chosen."""
        # index 0 → “Multiple CSV files…”
        # index 1 → “Single CSV file…”
        self.compare_box.setEnabled(index == 1)

    def print_sensitivities(self):
        if self.hydrophone_scan_data is not None and self.hydrophone_object.raw_data:
            converted_data = []  # Store converted datasets here

            for i, dataset in enumerate(self.hydrophone_object.raw_data):
                # Retrieve the transducer serial number for this dataset
                try:
                    serial = self.hydrophone_object.transducer_serials[i]
                except IndexError:
                    serial = "Unknown"

                # Convert dataset to a NumPy array and transpose it so each row is a data point
                data_array = np.array(dataset)
                data_transposed = data_array.T.copy()  # copy to leave raw_data unmodified

                # Convert sensitivity (column 1) from mV/MPa to V/MPa
                data_transposed[:, 1] /= 1000.0

                # Convert STD column if present (column 2)
                if data_transposed.shape[1] >= 3:
                    data_transposed[:, 2] /= 1000.0

                # Store the converted dataset (transpose back to original structure if needed)
                converted_data.append(data_transposed.T.tolist())

                # Extract frequency and sensitivity arrays (assumed to be in MHz and V/MPa now)
                freq = data_transposed[:, 0]
                sensitivity = data_transposed[:, 1]

                # Find the maximum sensitivity and its corresponding frequency
                max_index = np.argmax(sensitivity)
                max_sensitivity = sensitivity[max_index]
                max_freq = freq[max_index]

                # Parse the transducer serial number to extract resonant frequencies.
                # Expected format: "343-T1650H825"
                match = re.search(r'T(\d+)H(\d+)', serial)
                if match:
                    transducer_res_freq_khz = float(match.group(1))
                    hydrophone_res_freq_khz = float(match.group(2))
                    # Convert from kHz to MHz
                    transducer_res_freq_mhz = transducer_res_freq_khz / 1000.0
                    hydrophone_res_freq_mhz = hydrophone_res_freq_khz / 1000.0

                    # Find the sensitivity values at these resonant frequencies by finding the nearest value
                    idx_transducer = np.argmin(np.abs(freq - transducer_res_freq_mhz))
                    sens_at_transducer = sensitivity[idx_transducer]

                    idx_hydrophone = np.argmin(np.abs(freq - hydrophone_res_freq_mhz))
                    sens_at_hydrophone = sensitivity[idx_hydrophone]
                else:
                    # If parsing fails, set these values to None
                    transducer_res_freq_mhz = None
                    hydrophone_res_freq_mhz = None
                    sens_at_transducer = None
                    sens_at_hydrophone = None

                # Build the output string to append to the text display widget
                output_str = f"Transducer Serial: {serial}\n" \
                            f"Max Sensitivity: {max_sensitivity:.3f} V/MPa at {max_freq:.3f} MHz\n"
                if transducer_res_freq_mhz is not None and sens_at_transducer is not None:
                    output_str += f"Sensitivity at transducer resonance ({transducer_res_freq_mhz:.3f} MHz): " \
                                f"{sens_at_transducer:.3f} V/MPa\n"
                if hydrophone_res_freq_mhz is not None and sens_at_hydrophone is not None:
                    output_str += f"Sensitivity at hydrophone resonance ({hydrophone_res_freq_mhz:.3f} MHz): " \
                                f"{sens_at_hydrophone:.3f} V/MPa\n"

                self.text_display.append(output_str)

    def create_graph(self):
        if self.hydrophone_scan_data is not None:
            self.graph_tab.clear()
            self.save_as_svg_btn.setEnabled(True)

            self.graph = self.hydrophone_object.get_graphs(self.compare_box.isChecked())
            
            nav_tool = NavigationToolbar(self.graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(self.graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Hydrophone Scan Data")

        else:
            self.text_display.append("Error: No hydrophone data .csv file found.\n")