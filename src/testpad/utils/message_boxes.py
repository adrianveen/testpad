"""QMessageBox utility module for use across all testpad tabs.

Collection of pure functions for each type of QMessageBox to
be called directly.
"""

from PySide6.QtWidgets import QMessageBox


# TODO: Refine this module
# Use the following structure:
# def type_dialog(title: str, text: str) -> bool:
#     """Show a dialog with the given title and text."""
#     reply = QMessageBox.type(
#         self,
#         title,
#         text,
#         QMessageBox.StandardButton.Ok,
#     )
#     return reply == QMessageBox.StandardButton.Ok
# Confirm this is the best way to handle QMessageBoxes
def show_question(message: str) -> bool:
    """Open a question dialog with the given message and return the result."""
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Question)
    message_box.setWindowTitle("Question")
    message_box.setText(message)
    message_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    return message_box.exec() == QMessageBox.StandardButton.Yes


def show_info(message: str) -> None:
    """Open an info message dialog with the given message."""
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Information)
    message_box.setWindowTitle("Information")
    message_box.setText(message)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    message_box.exec()


def show_warning(message: str) -> None:
    """Open a warning message dialog with the given message."""
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setWindowTitle("Warning")
    message_box.setText(message)
    message_box.setStandardButtons(
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    )

    message_box.exec()


def show_critical(message: str) -> None:
    """Open a critical error message dialog with the given message."""
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Critical)
    message_box.setWindowTitle("Critical Error")
    message_box.setText(message)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    message_box.exec()
