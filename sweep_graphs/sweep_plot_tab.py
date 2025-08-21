import os
import numpy as np
import h5py

from datetime import datetime
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)

from sweep_graphs.sweep_graph import SweepGraph

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
        # spin box for trace number
        self.trace_no_menu = QComboBox()
        self.trace_no_menu.setEnabled(False)
        self.trace_no_label = QLabel("Select Trace Number:")
        # Save file as SVG button
        self.save_as_svg_btn = QPushButton("SAVE GRAPH AS SVG")
        self.save_as_svg_btn.setEnabled(False)
        self.save_as_svg_btn.clicked.connect(lambda: self.openFileDialog("save"))

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_file_btn, 0, 0, 1, 2)
        selections_layout.addWidget(self.trace_no_label, 1, 0)
        selections_layout.addWidget(self.trace_no_menu, 1, 1)
        selections_layout.addWidget(self.print_graph_btn, 2, 0, 1, 2)
        selections_layout.addWidget(self.save_as_svg_btn, 3, 0, 1, 2)
        buttons_groupbox.setLayout(selections_layout)
        buttons_groupbox.setFixedWidth(buttons_groupbox.minimumSizeHint().width())

        # TEXT CONSOLE
        self.text_display = QTextBrowser()
        self.text_display.setFixedWidth(buttons_groupbox.minimumSizeHint().width())

        # GRAPH DISPLAY 
        self.graph_tabs = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_tabs, 0, 1, 2, 1)
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
        
        # file saving location and save graph as SVG
        elif d_type == "save": # save graph SVG location 
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            # self.dialog.setDefaultSuffix("*.txt")
            self.dialog.setFileMode(QFileDialog.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location+"\n")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                time_svg_path = os.path.join(self.file_save_location, f"{self.scan_data_object.serial_no}_time_graph_{timestamp}.svg")
                fft_svg_path = os.path.join(self.file_save_location, f"{self.scan_data_object.serial_no}_fft_graph_{timestamp}.svg")

                # Define DPI and compute dimensions for a 1080p display (1920x1080 pixels)
                dpi = 100
                fig_width = 1920 / dpi   # 19.2 inches
                fig_height = 1080 / dpi  # 10.8 inches

                # Access the figure from the canvas for the time graph:
                self.time_graph.figure.set_size_inches(fig_width, fig_height)
                self.time_graph.figure.savefig(time_svg_path, format="svg", dpi=dpi)

                self.fft_graph.figure.set_size_inches(fig_width, fig_height)
                self.fft_graph.figure.savefig(fft_svg_path, format="svg", dpi=dpi)

                # finished saving message
                self.text_display.append("The following files were saved as SVG files:\n")
                self.text_display.append(f"Time Domain Graph: {self.scan_data_object.serial_no}_time_graph_{timestamp}.svg\n")
                self.text_display.append(f"FFT Graph: {self.scan_data_object.serial_no}_fft_graph_{timestamp}.svg\n")

                #print(f"serial no test: {self.scan_data_object.serial_no}")

        if self.scan_data_hdf5 and len(self.scan_data_hdf5) > 0:
            self.trace_no_menu.setEnabled(True)
            self.trace_no_menu.clear()
            with h5py.File(self.scan_data_hdf5[0], 'r') as f:
                # extract the number of rows to set the drop down
                scan_group = f['Scan']
                raw_pressu_waveforms = scan_group['Raw pressure waveforms (Pa)'][:]
                self.trace_no_menu.addItems([str(i+1) for i in range(raw_pressu_waveforms.shape[0])])
                # set the max index
                self.trace_no_menu.setCurrentIndex(raw_pressu_waveforms.shape[0]-1)
    
    @Slot()
    def create_graph(self):
        if self.scan_data_hdf5 is not None:
            self.graph_tabs.clear()
            self.save_as_svg_btn.setEnabled(True)

            self.scan_data_object = SweepGraph(self.scan_data_hdf5)
            self.time_graph, self.fft_graph = self.scan_data_object.get_graphs(self.trace_no_menu.currentIndex(), graph_type='time')
            
            # if time_graph is None or fft_graph is None:
            #     print("Error: One of the graph canvases is None")
            #     return

            nav_tool_time = NavigationToolbar(self.time_graph)
            nav_tool_fft = NavigationToolbar(self.fft_graph)

            time_widget = QWidget()
            time_layout = QVBoxLayout()
            time_layout.addWidget(nav_tool_time)
            time_layout.addWidget(self.time_graph)
            time_widget.setLayout(time_layout)
            self.graph_tabs.addTab(time_widget, "Time Domain")

            fft_widget = QWidget()
            fft_layout = QVBoxLayout()
            fft_layout.addWidget(nav_tool_fft)
            fft_layout.addWidget(self.fft_graph)
            fft_widget.setLayout(fft_layout)
            self.graph_tabs.addTab(fft_widget, "FFT Graph")

            # parts = self.scan_data_hdf5.split('_')
            # tx_serial_no = "-".join(parts[:2])
            # self.text_display.append("Transducer Serial Number: " + tx_serial_no + "\n")
            # Debugging statements
            # print(f"save_box is checked: {self.save_box.isChecked()}")
            # if self.file_save_location is not None:
            #   print(f"file_save_location: {self.file_save_location}")

        else:
            self.text_display.append("Error: No scan data hdf5 file found.\n")