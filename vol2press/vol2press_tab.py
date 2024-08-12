from vol2press_calcs import Vol2Press

from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal


class Vol2Press(QWidget):
    def __init__(self) -> None:
        super().__init__()

        selections_group = QGroupBox("File Selections")
        cal_eb50_file_btn = QPushButton("SELECT CALIBRATION EB-50 FILE")
        sys_eb50_file_btn = QPushButton("SELECT CUSTOMER EB-50 FILE")
        sweep_btn = QPushButton("SELECT SWEEP FILE")

        selections_layout = QGridLayout()
        selections_layout.addWidget(cal_eb50_file_btn, 0, 0)
        selections_layout.addWidget(sys_eb50_file_btn, 1, 0)
        selections_layout.addWidget(sweep_btn, 2, 0)
        selections_group.setLayout(selections_layout)

        console = QTextBrowser()

        graph_widget = QWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(selections_group, 0, 0)

        self.setLayout(main_layout)