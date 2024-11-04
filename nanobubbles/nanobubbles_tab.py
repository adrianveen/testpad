# from vol2press.vol2press_calcs import Vol2Press
from nanobubbles.nanobubbles_graph import NanobubblesGraph

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class NanobubblesTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.nanobubbles_files = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox()
        # select file button 
        self.select_file_btn = QPushButton("SELECT FILE")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("txt"))
        # bin width
        self.bin_width_label = QLabel("Bin Width/Bin Count (log scale):")
        self.bin_width_field = QLineEdit()
        self.bin_width_field.setText("30")
        
        # log fields 
        self.log_label = QLabel("Logarithmic Scale:")
        self.log_box = QCheckBox()
        self.log_box.setChecked(False)

        # option to compare multiple datasets. 
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setChecked(False)

        #option to normalize graphs
        self.normal_label = QLabel("Normalize Graphs:")
        self.normal_box = QCheckBox()
        self.normal_box.setChecked(False)

        # save fields 
        self.save_label = QLabel("Save file?")
        self.save_box = QCheckBox()
        self.save_box.setChecked(False)
        self.save_folder_btn = QPushButton("SAVE LOCATION")
        self.save_folder_btn.clicked.connect(lambda: self.openFileDialog("save"))
        
        # print graph button 
        self.print_graph_btn = QPushButton("PRINT GRAPH")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.create_graph())
        
        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_file_btn, 0, 0, 1, 2)
        # add bin width label and field
        selections_layout.addWidget(self.bin_width_label, 1, 0)
        selections_layout.addWidget(self.bin_width_field, 1, 1)
        # add log scale label and checkbox
        selections_layout.addWidget(self.log_label, 2, 0)
        selections_layout.addWidget(self.log_box, 2, 1, Qt.AlignCenter)
        # add compare label and checkbox
        selections_layout.addWidget(self.compare_label, 3, 0)
        selections_layout.addWidget(self.compare_box, 3, 1, Qt.AlignCenter)
        # add normalize label and checkbox
        selections_layout.addWidget(self.normal_label, 4, 0)
        selections_layout.addWidget(self.normal_box, 4, 1, Qt.AlignCenter)
        # add save label and checkbox
        selections_layout.addWidget(self.save_label, 5, 0)
        selections_layout.addWidget(self.save_box, 5, 1, Qt.AlignCenter)
        selections_layout.addWidget(self.save_folder_btn, 6, 0, 1, 2)
        # add print graph button
        selections_layout.addWidget(self.print_graph_btn, 7, 0, 1, 2)
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

    # opens txt file for reading
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "txt": # open nanobubble txt 
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Nanobubble TXT File(s)")
            
            if self.compare_box.isChecked():
                self.dialog1.setFileMode(QFileDialog.ExistingFiles)
            else:
                self.dialog1.setFileMode(QFileDialog.ExistingFile)
            
            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt") # default suffix of yaml
            
            if self.dialog1.exec(): 
                self.text_display.append("Nanobubble File(s): ")
                self.nanobubbles_files = self.dialog1.selectedFiles()
                for file in self.nanobubbles_files:
                    self.text_display.append(file +"\n")
        
        elif d_type == "save": # save graph SVG location 
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            # self.dialog.setDefaultSuffix("*.txt")
            self.dialog.setFileMode(QFileDialog.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location+"\n")

    # add graph + navtoolbar to graph display 
    @Slot()
    def create_graph(self):
        if self.nanobubbles_files is not None:
            self.graph_tab.clear()

            if not self.log_box.isChecked():
                nanobubbles_object = NanobubblesGraph(self.nanobubbles_files)
                graph = nanobubbles_object.get_graphs(float(self.bin_width_field.text()), False, self.normal_box.isChecked(), self.compare_box.isChecked())
            else: #log scale
                nanobubbles_object = NanobubblesGraph(self.nanobubbles_files)
                graph = nanobubbles_object.get_graphs(float(self.bin_width_field.text()), "log", self.normal_box.isChecked(), self.compare_box.isChecked())
                
            nav_tool = NavigationToolbar(graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Nanobubbles Graph")

            # Debugging statements
            print(f"save_box is checked: {self.save_box.isChecked()}")
            print(f"file_save_location: {self.file_save_location}")

            if self.save_box.isChecked():
                save_loc = nanobubbles_object.save_graph(self.file_save_location, self.compare_box.isChecked())
                self.text_display.append(f"Saved to {save_loc}")
        else:
            self.text_display.append("No nanobubble txt found!\n")
