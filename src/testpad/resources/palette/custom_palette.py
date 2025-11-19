from PySide6 import QtCore, QtGui, QtWidgets


def load_custom_palette(palette_name: str) -> tuple[QtGui.QPalette, str]:
    """Return a Qt palette and optional tooltip style for a given theme name.

    Uses fully-qualified enum references for clarity (QtGui.QPalette.ColorRole,
        QtGui.QPalette.ColorGroup, QtCore.Qt.GlobalColor).
    """
    if palette_name == "dark_palette":
        palette = QtGui.QPalette()

        # Window + basic roles
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(
            QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white
        )
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(35, 35, 35))
        palette.setColor(
            QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53)
        )

        # Tooltips
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(25, 25, 25))
        palette.setColor(
            QtGui.QPalette.ColorRole.ToolTipText, QtCore.Qt.GlobalColor.white
        )

        # Text + buttons
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtCore.Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(
            QtGui.QPalette.ColorRole.ButtonText, QtCore.Qt.GlobalColor.white
        )
        palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtCore.Qt.GlobalColor.red)

        # Links & selections
        palette.setColor(
            QtGui.QPalette.ColorRole.Link, QtGui.QColor(49, 84, 72)
        )  # green-ish
        palette.setColor(
            QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(49, 84, 72)
        )  # green-ish
        palette.setColor(
            QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(230, 230, 230)
        )

        # Disabled state tweaks
        palette.setColor(
            QtGui.QPalette.ColorGroup.Active,
            QtGui.QPalette.ColorRole.Button,
            QtGui.QColor(53, 53, 53),
        )
        palette.setColor(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.ButtonText,
            QtCore.Qt.GlobalColor.darkGray,
        )
        palette.setColor(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.WindowText,
            QtCore.Qt.GlobalColor.darkGray,
        )
        palette.setColor(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.Text,
            QtCore.Qt.GlobalColor.darkGray,
        )
        palette.setColor(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.Light,
            QtGui.QColor(53, 53, 53),
        )

        # Optional tooltip style to match dark palette
        palette_style = (
            "QToolTip { "
            "color: rgb(230, 230, 230); "
            "background-color: rgb(53, 53, 53); "
            "border: 1px solid rgb(230, 230, 230); "
            "}"
        )
    else:
        # Ensure fallback uses Fusion style's standard palette
        style = QtWidgets.QStyleFactory.create("Fusion")
        if style is not None:
            palette = style.standardPalette()
        else:
            palette = QtWidgets.QApplication.style().standardPalette()
        palette_style = ""

    return palette, palette_style
