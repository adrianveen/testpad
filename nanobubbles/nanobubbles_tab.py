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

        # BUTTONS 
        buttons_groupbox = QGroupBox()
        select_file_btn = QPushButton("SELECT FILE")
        select_file_btn.clicked.connect(lambda: self.openFileDialog("txt"))
        print_graph_btn = QPushButton("PRINT GRAPH")
        print_graph_btn.setStyleSheet("background-color: #74BEA3")
        print_graph_btn.clicked.connect(lambda: self.create_graph())
        
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(select_file_btn)
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

    # 
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "txt":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Nanobubble TXT File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt") # default suffix of yaml
            if self.dialog1.exec(): 
                self.text_display.append("Nanobubble File: ")
                self.nanobubbles_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.nanobubbles_file+"\n")

    # add graph + navtoolbar to graph display 
    @Slot()
    def create_graph(self):
        self.graph_tab.clear()

        graph = NanobubblesGraph(self.nanobubbles_file).get_graphs()
        nav_tool = NavigationToolbar(graph)

        graph_widget = QWidget()
        burn_layout = QVBoxLayout()
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(graph)
        graph_widget.setLayout(burn_layout)

        self.graph_tab.addTab(graph_widget, "Nanobubbles Graph")


    