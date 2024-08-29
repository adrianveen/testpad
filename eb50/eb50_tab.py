from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QPixmap
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QComboBox, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser, QVBoxLayout,
                               QWidget)

# CURRENTLY A PLACEHOLDER

class EboxTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # SIGLENT GROUPBOX 
        siglent_group = QGroupBox("Siglent")
        
        # EB-50 GROUPBOX 
        eb50_group = QGroupBox("EB-50")
        serial_num_label = QLabel("EB-50 serial number")
        amp_num_label = QLabel("Amplifier number")
        siglent_file_label = QLabel("Siglent file")
        eb50_atten_label = QLabel("EB-50 Attenuation (dB)")
        amp_start_val_label = QLabel("Amplitude start value (Vpp)")
        amp_stop_val_label = QLabel("Amplitude stop value (Vpp)")
        amp_step_val_label = QLabel("Amplitude step value (Vpp)")
        coupler_atten_label = QLabel("Coupler attenuation (dB)")

        # MAIN LAYOUT 
        main_layout = QGridLayout()
        main_layout.addWidget(siglent_group)
        main_layout.addWidget(eb50_group)

        self.setLayout(main_layout)

