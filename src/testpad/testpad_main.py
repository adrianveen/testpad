import sys
import os
# from PySide6.QtGui import QResizeEvent, QPalette
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication

from testpad.ui.tabs.matching_box_tab import MatchingBoxTab
from testpad.ui.tabs.transducer_calibration_tab import TransducerCalibrationTab
from testpad.ui.tabs.transducer_linear_tab import TransducerLinearTab
from testpad.ui.tabs.rfb_tab import RFBTab
from testpad.ui.tabs.vol2press_tab import Vol2PressTab
from testpad.ui.tabs.burnin_tab import BurninTab
from testpad.ui.tabs.nanobubbles_tab import NanobubblesTab
from testpad.ui.tabs.temp_analysis_tab import TempAnalysisTab
from testpad.ui.tabs.hydrophone_tab import HydrophoneAnalysisTab
from testpad.ui.tabs.sweep_plot_tab import SweepGraphTab
from testpad.resources.palette.custom_palette import load_custom_palette
from testpad.version import __version__ 

# application window (subclass of QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None): 

        # QMainWindow.__init__(self, parent)

        super().__init__(parent)
        pkg_dir = os.path.dirname(__file__)
        icon_path_pkg = os.path.join(pkg_dir, 'resources', 'fus_icon_transparent.ico')
        meipass = getattr(sys, '_MEIPASS', '')
        if os.path.exists(icon_path_pkg):
            icon_path = icon_path_pkg
        elif meipass:
            icon_path = os.path.join(meipass, 'resources', 'fus_icon_transparent.ico')
        else:
            icon_path = os.path.join(os.getcwd(), 'src', 'testpad', 'resources', 'fus_icon_transparent.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(f"FUS Testpad v{__version__}")
        self.resize(800, 600)        
        
        tab_widget = QTabWidget()

        tab_widget.addTab(MatchingBoxTab(self), "Matching Box") # matching calculations & CSV graphs
        tab_widget.addTab(TransducerCalibrationTab(self), "Transducer Calibration Report") # calibration report graphs 
        tab_widget.addTab(TransducerLinearTab(self), "Transducer Linear Graphs") # linear graphs made during calibration 
        tab_widget.addTab(RFBTab(self), "Radiation Force Balance") # rfb graphs 
        tab_widget.addTab(Vol2PressTab(self), "Sweep Analysis") # linear regression of sweep line using two different gains
        tab_widget.addTab(BurninTab(self), "Burn-in Graph Viewer") # graphs HDF5 files from burn-in for user manipulation 
        tab_widget.addTab(NanobubblesTab(self), "Nanobubbles Tab") # graphs nanobubbles size vs. count
        tab_widget.addTab(TempAnalysisTab(self), "Temperature Analysis") # graphs temperature vs. time
        tab_widget.addTab(HydrophoneAnalysisTab(self), "Hydrophone Analysis") # graphs hydrophone data
        tab_widget.addTab(SweepGraphTab(), "Sweep Graphs") # placeholder tab for future use

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        self.setCentralWidget(tab_widget)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    QCoreApplication.setOrganizationName("FUS Instruments")
    QCoreApplication.setOrganizationDomain("fusinstruments.com")
    QCoreApplication.setApplicationName("Testpad")
    
    app.setStyleSheet("QLabel{font-size: 11pt;}") # increase font size slightly of QLabels
    app.setStyle("Fusion")
    dark_palette, palette_tooltip = load_custom_palette(palette_name="dark_palette")

    app.setPalette(dark_palette)
    app.setStyleSheet(palette_tooltip)

    tab_dialog = ApplicationWindow()
    # tab_dialog.setFixedSize(False)
    # tab_dialog.setMaximumSize()
    # tab_dialog.setFixedSize(700, 500)
    tab_dialog.resize(1200, 800)
    tab_dialog.show() 
    
    # tab_dialog.raise_() # look up what this does

    sys.exit(app.exec())
