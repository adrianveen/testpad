import PySide6.QtWidgets as QtWidgets
from PySide6.QtCore import Qt


class DissolvedOxygenTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = ..., f: Qt.WindowType = ...) -> None:
        super().__init__(parent, f)

        # Main layout
        main_layout = QtWidgets.QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)

        # Add widgets
