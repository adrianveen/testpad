import sys
import os
import importlib
from contextlib import contextmanager
from importlib.abc import MetaPathFinder as _MetaPathFinder
from importlib.machinery import PathFinder as _PathFinder
from typing import Callable, List, Tuple, Set, Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication, QTimer, QSignalBlocker

from testpad.resources.palette.custom_palette import load_custom_palette
from testpad.ui.splash import SplashScreen
from testpad.ui.tabs.registry import TABS_SPEC, enabled_tabs, TabSpec
from testpad.version import __version__ 

# application window (subclass of QMainWindow)
class ApplicationWindow(QMainWindow): 
    def __init__(self, parent: QWidget=None, *,
                 progress_cb: Optional[Callable[[str], None]] = None,
                 tabs_spec: Optional[List[TabSpec]] = None,
                 on_first_show: Optional[Callable[[], None]] = None,
                 per_file_cb: Optional[Callable[[int], None]] = None) -> None: 

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
        self._lazy_specs: List[TabSpec] = []
        self._loaded: dict[int, bool] = {}
        self._on_first_show: Optional[Callable[[], None]] = on_first_show
        self._shown_once: bool = False
        self._per_file_cb: Optional[Callable[[int], None]] = per_file_cb

        # Build lightweight placeholders; load tabs on demand
        self._setup_lazy_tabs(progress_cb, tabs_spec)

        # Set as central widget
        self.setCentralWidget(self._tab_widget)

        # Ensure the initially visible tab is loaded before showing the window
        # so the main window appears with UI ready.
        self._ensure_loaded(self._tab_widget.currentIndex(), progress_cb)

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        if not self._shown_once:
            self._shown_once = True
            if self._on_first_show:
                # Defer to next loop turn to ensure the window is really shown
                QTimer.singleShot(0, self._on_first_show)

    def _setup_lazy_tabs(self, progress_cb: Callable[[str], None] | None,
                         tabs_spec: List[Tuple[str, str, str]] | None) -> None:

        if tabs_spec is None:
            tabs_spec = list(TABS_SPEC)
        self._lazy_specs = list(tabs_spec)

        # Add lightweight placeholders (so the UI can show immediately)
        from PySide6.QtWidgets import QLabel
        
        for spec in self._lazy_specs:
            label = spec.label
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.addWidget(QLabel("Tab loads on first open…"))
            layout.addStretch(1)
            self._tab_widget.addTab(placeholder, label)

        # Hook tab change to lazy-loader
        self._tab_widget.currentChanged.connect(self._ensure_loaded)

        # Initial tab is loaded synchronously in __init__ to avoid blank window

    @staticmethod
    @contextmanager
    def _progress_imports(callback: Optional[Callable[[str], None]], targets: Set[str], per_file_cb: Optional[Callable[[int], None]] = None):
        if callback is None:
            yield
            return
        class _Tracer(_MetaPathFinder):
            def __init__(self):
                self.seen_mods: Set[str] = set()
                self.seen_files: Set[str] = set()
            def find_spec(self, fullname, path, target=None):  # noqa: D401
                top = fullname.split('.', 1)[0]
                if top not in targets:
                    return None
                try:
                    spec = _PathFinder.find_spec(fullname, path)
                except Exception:
                    spec = None
                # Emit top-level import name once
                if top not in self.seen_mods:
                    self.seen_mods.add(top)
                    try:
                        callback(f"Importing {top}…")
                    except Exception:
                        pass
                # Emit file origin for more granular feedback
                if spec and isinstance(getattr(spec, 'origin', None), str):
                    origin = spec.origin
                    if origin and origin not in ('built-in', 'frozen') and origin not in self.seen_files:
                        self.seen_files.add(origin)
                        try:
                            callback(f"Loading: {origin}")
                        except Exception:
                            pass
                        if per_file_cb is not None:
                            try:
                                per_file_cb(len(self.seen_files))
                            except Exception:
                                pass
                return None
        import sys as _sys
        tracer = _Tracer()
        _sys.meta_path.insert(0, tracer)
        try:
            yield
        finally:
            try:
                _sys.meta_path.remove(tracer)
            except ValueError:
                pass

    def _ensure_loaded(self, index: int, progress_cb: Optional[Callable[[str], None]] = None) -> None:
        # Skip work if the tab is already loaded or the index falls outside the spec list.
        if index in self._loaded or index < 0 or index >= len(self._lazy_specs):
            return
        spec = self._lazy_specs[index]
        label = spec.label
        module_path = spec.module
        class_name = spec.cls

        try:
            # Provide immediate feedback that this tab is the one being resolved.
            if progress_cb:
                progress_cb(f"Loading: {label} ({module_path})")
            # Highlight module families that tend to dominate import time so the progress UI can
            # surface meaningful messages while the interpreter walks their files.
            heavy = {"testpad", "PySide6", "numpy", "pandas", "matplotlib", "h5py", "scipy", "PIL", "yaml"}
            # Temporarily install our import tracer to stream progress callbacks as dependencies load.
            with self._progress_imports(progress_cb, heavy, self._per_file_cb):
                mod = importlib.import_module(module_path)
            # Late-bind the widget class so we do not pay import costs until the tab is needed.
            cls = getattr(mod, class_name)
            # `SweepGraphTab` predates the parent-aware tabs, so we keep its legacy construction path.
            widget = cls() if label == "Sweep Graphs" else cls(self)
            if progress_cb:
                progress_cb(f"Loaded: {label}")
        except Exception as e:
            from PySide6.QtWidgets import QLabel
            # Substitute a failure indicator so the user sees the problem instead of a blank tab.
            widget = QLabel(f"Failed to load '{label}': {e}")

        # Replace placeholder while preserving index
        blocker = QSignalBlocker(self._tab_widget)
        try:
            # Swap the placeholder for the real widget without triggering `currentChanged`.
            self._tab_widget.removeTab(index)
            self._tab_widget.insertTab(index, widget, label)
            # Keep current index without re-triggering currentChanged
            self._tab_widget.setCurrentIndex(index)
        finally:
            del blocker
        # Remember that this tab has been resolved so future activations are no-ops.
        self._loaded[index] = True
    
def main() -> None:
    """Main entry point for the Testpad application."""
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
    splash.update_progress(5, "Starting Testpad…")
    
    flags = {
        "degasser_data": True  # Enable for testing
    }
    tabs_spec: List[TabSpec] = list(enabled_tabs(TABS_SPEC, flags))

    # Staged progress with granular updates during first tab import
    prog = {"p": 5}
    def setp(pct: int, msg: str):
        if pct > prog["p"]:
            prog["p"] = pct
        splash.update_progress(prog["p"], msg)

    setp(25, "Loading theme…")
    setp(60, "Initializing main window…")

    # Per-file proportional progress: advance a small, fixed amount per file discovered
    files_per_percent = 5  # tweak to taste
    def per_file_cb(count: int):
        # Map file count to percent in [60,95)
        start, end = 60, 95
        pct = start + min((end - start - 1), count // files_per_percent)
        if pct > prog["p"]:
            prog["p"] = pct
        splash.update_progress(prog["p"], None)

    # Message-only callback (does not change percent directly)
    def tab_cb(msg: str):
        splash.update_progress(prog["p"], msg)

    # Define finalize callback before creating the window, pass to on_first_show
    def finalize_ready():
        splash.update_progress(100, "Ready")
        QTimer.singleShot(200, splash.close)

    # Mention a few remaining tabs without loading them
    remaining = [spec.label for spec in tabs_spec][1:]
    for name in remaining[:3]:
        tab_cb(f"Ready: {name}")

    tab_dialog = ApplicationWindow(progress_cb=tab_cb, tabs_spec=tabs_spec, on_first_show=finalize_ready, per_file_cb=per_file_cb)
    tab_dialog.resize(1200, 800)

    # Show the window, then mark 100% when it is actually exposed (interactable)
    setp(95, "Finalizing UI…")
    tab_dialog.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
