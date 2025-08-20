import sys
import os
# from PySide6.QtGui import QResizeEvent, QPalette
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon

from matching_box.matching_box_tab import MatchingBoxTab
from rfb.rfb_tab import RFBTab
from transducer.transducer_calibration_tab import TransducerCalibrationTab
from transducer.transducer_linear_tab import TransducerLinearTab
from vol2press.vol2press_tab import Vol2PressTab
from burnin.burnin_tab import BurninTab
from nanobubbles.nanobubbles_tab import NanobubblesTab
from temp_analysis.temp_analysis_tab import TempAnalysisTab
from hydrophone.hydrophone_tab import HydrophoneAnalysisTab
from sweep_plotter.sweep_plot_tab import SweepGraphTab

# application window (subclass of QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None): 

        # QMainWindow.__init__(self, parent)

        super().__init__(parent)
        base_path = getattr(sys, '_MEIPASS', os.getcwd())
        icon_path = os.path.join(base_path, 'images', 'fus_icon_transparent.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("FUS Testpad v1.9.5")
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
    app.setStyleSheet("QLabel{font-size: 11pt;}") # increase font size slightly of QLabels

    tab_dialog = ApplicationWindow()
    # tab_dialog.setFixedSize(False)
    # tab_dialog.setMaximumSize()
    # tab_dialog.setFixedSize(700, 500)
    tab_dialog.showMaximized() # full screen 
    
    # tab_dialog.raise_() # look up what this does

    sys.exit(app.exec())
