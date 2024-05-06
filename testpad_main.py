import sys
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from matching_box.matching_box_tab import MatchingBoxTab
from rfb.rfb_tab import RFBTab
from transducer.transducer_calibration_tab import TransducerCalibrationTab
from transducer.transducer_linear_tab import TransducerLinearTab
from eb50.eb50_tab import EboxTab

# application window (inherits QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None): 

        # QMainWindow.__init__(self, parent)

        super().__init__(parent)

        tab_widget = QTabWidget()
        # sp = tab_widget.sizePolicy()
        # sp.Policy = QSizePolicy.Expanding
        
        # tab_widget.setMinimumSize(QMainWindow.sizeHint())
        # tab_widget.showFullScreen()
        # self.matching_tab = MatchingBoxTab(self) # declare as separate object to resize image 
        tab_widget.addTab(MatchingBoxTab(self), "Matching Box") # matching calculations & CSV graphs 
        tab_widget.addTab(EboxTab(self), "Siglent/EB-50 Calibration") # calibrating siglent & EB-50 
        tab_widget.addTab(TransducerCalibrationTab(self), "Transducer Calibration Report") # calibration report graphs 
        tab_widget.addTab(TransducerLinearTab(self), "Transducer Linear Graphs") # linear graphs made during calibration 
        tab_widget.addTab(RFBTab(self), "Radiation Force Balance") # rfb graphs 

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        self.setCentralWidget(tab_widget)
    
    # def resizeEvent(self, event: QResizeEvent) -> None:
    #     # super().resizeEvent(event)
    #     self.matching_tab.resizeImage()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 11pt;}") # increase font size slightly of QLabels

    tab_dialog = ApplicationWindow()
    tab_dialog.setWindowTitle("FUS Testpad")
    # tab_dialog.setFixedSize(False)
    # tab_dialog.setMaximumSize()
    # tab_dialog.setFixedSize(700, 500)
    tab_dialog.showMaximized() # full screen 
    
    # tab_dialog.raise_() # look up what this does

    sys.exit(app.exec())
