from PySide6.QtWidgets import QVBoxLayout, QLabel
from testpad.ui.tabs.base_tab import BaseTab
from .model import DissolvedO2Model
from .presenter import DissolvedO2Presenter

class DissolvedO2Tab(BaseTab):
    """UI stub for Dissolved O2 (feature-flagged)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DissolvedO2Model()
        self._presenter = DissolvedO2Presenter(self._model)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dissolved O₂ (stub tab)"))
        layout.addStretch(1)

        self._presenter.initialize()

    def on_close(self) -> None:
        self._presenter.shutdown()