from burnin.burnin_graph import BurninGraph

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class BurninTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        selections_group = QGroupBox()
        self.select_burnin_file_btn = QPushButton("SELECT BURN-IN FILE")
        self.select_burnin_file_btn.clicked.connect(lambda: self.openFileDialog("burn"))
        # self.select_save_folder_btn = QPushButton("SELECT SAVE FOLDER")
        # self.select_save_folder_btn.clicked.connect(lambda: self.openFileDialog("save"))
        # save_graph_label = QLabel("Save graph?")
        # self.save_graph_box = QCheckBox()
        self.print_graph_btn = QPushButton("PRINT GRAPH")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(self.printGraphs)

        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_burnin_file_btn, 0, 0, 1, 2)
        # selections_layout.addWidget(self.select_save_folder_btn, 1, 0, 1, 2)
        # selections_layout.addWidget(save_graph_label, 2, 0)
        # selections_layout.addWidget(self.save_graph_box, 2, 1)
        selections_layout.addWidget(self.print_graph_btn, 1, 0, 1, 2)
        selections_group.setLayout(selections_layout)

        self.text_display = QTextBrowser()

        self.graph_display = QTabWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(selections_group, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 2, 1)
        self.setLayout(main_layout)

    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "burn":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Burn-in File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.hdf5")

            if self.dialog1.exec(): 
                self.text_display.append("Burn-in File: ")
                self.burnin_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.burnin_file+"\n")
        elif d_type == "save":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Save Folder")
            self.dialog1.setFileMode(QFileDialog.Directory)

            if self.dialog1.exec(): 
                self.text_display.append("Save Folder: ")
                self.save_folder = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.save_folder+"\n")

    def printGraphs(self):
        self.graph_display.clear()

        self.burnin = BurninGraph(self.burnin_file)

        burn_graph = self.burnin.getGraph()
        nav_tool = NavigationToolbar(burn_graph)

        burn_widget = QWidget()
        burn_layout = QVBoxLayout()
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)

        self.graph_display.addTab(burn_widget, "Burn-in Graph")

