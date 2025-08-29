import sys
import os
from importlib import import_module
from typing import Callable, List, Tuple
# from PySide6.QtGui import QResizeEvent, QPalette
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication, QTimer

from testpad.resources.palette.custom_palette import load_custom_palette
from testpad.ui.splash import SplashScreen
from testpad.version import __version__ 

# application window (subclass of QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None, *,
                 progress_cb: Callable[[str], None] | None = None,
                 tabs_spec: List[Tuple[str, str, str]] | None = None): 

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

        self._tab_widget = QTabWidget()

        # Build tabs dynamically to allow progress reporting
        self._build_tabs(progress_cb, tabs_spec)

        # Set as central widget
        self.setCentralWidget(self._tab_widget)

    def _build_tabs(self, progress_cb: Callable[[str], None] | None,
                    tabs_spec: List[Tuple[str, str, str]] | None) -> None:
        # tabs_spec: list of (module_path, class_name, label)
        if tabs_spec is None:
            tabs_spec = [
                ("testpad.ui.tabs.matching_box_tab", "MatchingBoxTab", "Matching Box"),
                ("testpad.ui.tabs.transducer_calibration_tab", "TransducerCalibrationTab", "Transducer Calibration Report"),
                ("testpad.ui.tabs.transducer_linear_tab", "TransducerLinearTab", "Transducer Linear Graphs"),
                ("testpad.ui.tabs.rfb_tab", "RFBTab", "Radiation Force Balance"),
                ("testpad.ui.tabs.vol2press_tab", "Vol2PressTab", "Sweep Analysis"),
                ("testpad.ui.tabs.burnin_tab", "BurninTab", "Burn-in Graph Viewer"),
                ("testpad.ui.tabs.nanobubbles_tab", "NanobubblesTab", "Nanobubbles Tab"),
                ("testpad.ui.tabs.temp_analysis_tab", "TempAnalysisTab", "Temperature Analysis"),
                ("testpad.ui.tabs.hydrophone_tab", "HydrophoneAnalysisTab", "Hydrophone Analysis"),
                ("testpad.ui.tabs.sweep_plot_tab", "SweepGraphTab", "Sweep Graphs"),
            ]

        for module_path, class_name, label in tabs_spec:
            try:
                mod = import_module(module_path)
                cls = getattr(mod, class_name)
                module_file = getattr(mod, "__file__", module_path)
                if progress_cb:
                    progress_cb(f"Loading tab: {label} ({module_file})")
                if label == "Sweep Graphs":
                    # original ctor took no parent
                    widget = cls()
                else:
                    widget = cls(self)
                self._tab_widget.addTab(widget, label)
            except Exception as e:  # keep app loading if one tab fails
                if progress_cb:
                    progress_cb(f"Failed to load: {label} — {e}")
                # Add a placeholder error tab
                from PySide6.QtWidgets import QLabel
                err = QLabel(f"Failed to load '{label}': {e}")
                self._tab_widget.addTab(err, label)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)

    QCoreApplication.setOrganizationName("FUS Instruments")
    QCoreApplication.setOrganizationDomain("fusinstruments.com")
    QCoreApplication.setApplicationName("Testpad")

    app.setStyleSheet("QLabel{font-size: 11pt;}")  # increase font size slightly of QLabels
    app.setStyle("Fusion")
    dark_palette, palette_tooltip = load_custom_palette(palette_name="dark_palette")
    app.setPalette(dark_palette)
    app.setStyleSheet(palette_tooltip)

    # Splash screen setup
    splash = SplashScreen(version_text=f"v{__version__}")
    splash.show_centered()
    splash.update_progress(2, "Starting Testpad…")

    # Define tabs spec here so we can compute progress based on real work
    tabs_spec = [
        ("testpad.ui.tabs.matching_box_tab", "MatchingBoxTab", "Matching Box"),
        ("testpad.ui.tabs.transducer_calibration_tab", "TransducerCalibrationTab", "Transducer Calibration Report"),
        ("testpad.ui.tabs.transducer_linear_tab", "TransducerLinearTab", "Transducer Linear Graphs"),
        ("testpad.ui.tabs.rfb_tab", "RFBTab", "Radiation Force Balance"),
        ("testpad.ui.tabs.vol2press_tab", "Vol2PressTab", "Sweep Analysis"),
        ("testpad.ui.tabs.burnin_tab", "BurninTab", "Burn-in Graph Viewer"),
        ("testpad.ui.tabs.nanobubbles_tab", "NanobubblesTab", "Nanobubbles Tab"),
        ("testpad.ui.tabs.temp_analysis_tab", "TempAnalysisTab", "Temperature Analysis"),
        ("testpad.ui.tabs.hydrophone_tab", "HydrophoneAnalysisTab", "Hydrophone Analysis"),
        ("testpad.ui.tabs.sweep_plot_tab", "SweepGraphTab", "Sweep Graphs"),
    ]

    total_steps = len(tabs_spec) + 2  # init + finalize
    progress_state = {"step": 0}

    def progress_step(message: str) -> None:
        progress_state["step"] += 1
        percent = int(progress_state["step"] / total_steps * 100)
        splash.update_progress(percent, message)

    progress_step("Initializing main window…")
    tab_dialog = ApplicationWindow(progress_cb=progress_step, tabs_spec=tabs_spec)
    tab_dialog.resize(1200, 800)

    progress_step("Finalizing UI…")
    # Show main window immediately, keep splash for ~1s at 100%
    tab_dialog.show()
    QTimer.singleShot(750, splash.close)
    sys.exit(app.exec())
