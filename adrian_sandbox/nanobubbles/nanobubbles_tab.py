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

        self.nanobubbles_file = None

        # USER INTERACTION AREA
        # select file button 
        buttons_groupbox = QGroupBox()
        select_file_btn = QPushButton("SELECT FILE")
        select_file_btn.clicked.connect(lambda: self.openFileDialog("txt"))
        # bin width 
        bin_widget = QWidget()
        bin_widget.setContentsMargins(0, 0, 0, 0)
        bin_width_label = QLabel("Bin width")
        self.bin_width_field = QLineEdit()
        self.bin_width_field.setText("25")
        bin_layout = QGridLayout()
        bin_layout.setColumnStretch(0, 1)
        bin_layout.setColumnStretch(1, 1)
        bin_layout.setContentsMargins(0, 0, 0, 0)
        bin_layout.addWidget(bin_width_label, 0, 0)
        bin_layout.addWidget(self.bin_width_field, 0, 1)
        bin_widget.setLayout(bin_layout)
        
        # log fields 
        log_widget = QWidget()
        log_widget.setContentsMargins(0, 0, 0, 0)
        log_label = QLabel("Logarithmic Scale?")
        self.log_box = QCheckBox()
        log_layout = QGridLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.addWidget(log_label, 0, 0)
        log_layout.addWidget(self.log_box, 0, 1, Qt.AlignCenter)
        # save_layout.addWidget(save_folder_btn, 1, 0, 1, 2)
        log_widget.setLayout(log_layout)
        
        # save fields 
        save_widget = QWidget()
        save_widget.setContentsMargins(0, 0, 0, 0)
        save_label = QLabel("Save file?")
        self.save_box = QCheckBox()
        save_folder_btn = QPushButton("SAVE LOCATION")
        save_folder_btn.clicked.connect(lambda: self.openFileDialog("save"))
        save_layout = QGridLayout()
        save_layout.setContentsMargins(0, 0, 0, 0)
        save_layout.addWidget(save_label, 0, 0)
        save_layout.addWidget(self.save_box, 0, 1, Qt.AlignCenter)
        save_layout.addWidget(save_folder_btn, 1, 0, 1, 2)
        save_widget.setLayout(save_layout)

        # print graph button 
        print_graph_btn = QPushButton("PRINT GRAPH")
        print_graph_btn.setStyleSheet("background-color: #74BEA3")
        print_graph_btn.clicked.connect(lambda: self.create_graph())
        
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(select_file_btn)
        buttons_layout.addWidget(bin_widget)
        buttons_layout.addWidget(log_widget)
        buttons_layout.addWidget(save_widget)
        buttons_layout.addWidget(print_graph_btn)
        buttons_groupbox.setLayout(buttons_layout)

        # TEXT CONSOLE
        self.text_display = QTextBrowser()

        # GRAPH DISPLAY 
        self.graph_tab = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()
        # main_layout.addWidget(select_file_btn, 0, 0)
        # main_layout.addWidget(print_graph_btn, 1, 0)
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_tab, 0, 1, 3, 1)
        self.setLayout(main_layout)

    # opens txt file for reading
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "txt": # open nanobubble txt 
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Nanobubble TXT File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Nanobubble File: ")
                self.nanobubbles_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.nanobubbles_file+"\n")
        
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
        if self.nanobubbles_file is not None:
            self.graph_tab.clear()

            if not self.log_box.isChecked():
                nanobubbles_object = NanobubblesGraph(self.nanobubbles_file)
                graph = nanobubbles_object.get_graphs(float(self.bin_width_field.text()))
                nav_tool = NavigationToolbar(graph)

                graph_widget = QWidget()
                burn_layout = QVBoxLayout()
                burn_layout.addWidget(nav_tool)
                burn_layout.addWidget(graph)
                graph_widget.setLayout(burn_layout)

                self.graph_tab.addTab(graph_widget, "Nanobubbles Graph")
            else: #log scale
                nanobubbles_object = NanobubblesGraph(self.nanobubbles_file)
                graph = nanobubbles_object.get_graphs(float(self.bin_width_field.text()), "log")
                nav_tool = NavigationToolbar(graph)

                graph_widget = QWidget()
                burn_layout = QVBoxLayout()
                burn_layout.addWidget(nav_tool)
                burn_layout.addWidget(graph)
                graph_widget.setLayout(burn_layout)

                self.graph_tab.addTab(graph_widget, "Nanobubbles Graph")

            if self.save_box.isChecked():
                save_loc = nanobubbles_object.save_graph(self.file_save_location)
                self.text_display.append(f"Saved to {save_loc}")
        else:
            self.text_display.append("No nanobubble txt found!\n")


    