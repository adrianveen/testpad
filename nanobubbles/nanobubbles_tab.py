# from vol2press.vol2press_calcs import Vol2Press
from nanobubbles_graph import NanobubblesGraph

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QHBoxLayout, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QMessageBox, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal

class NanobubblesTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        select_file_btn = QPushButton("SELECT FILE")
        print_graph_btn = QPushButton("PRINT GRAPH")

        text_display = QTextBrowser()

        self.graph_tab = QTabWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(select_file_btn, 0, 0)
        main_layout.addWidget(print_graph_btn, 1, 0)
        main_layout.addWidget(text_display, 2, 0)
        main_layout.addWidget(self.graph_tab, 0, 1, 3, 1)
        self.setLayout(main_layout)

    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "sweep":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Sweep File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Sweep File: ")
                self.sweep_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.sweep_file+"\n")
                self.enable_btn() # enable the new frequency to be added to the YAML 

    def create_graph(self):
        graph = NanobubblesGraph()
        self.graph_tab.addTab(graph.get_graphs(), "Nanobubbles Graph")


    