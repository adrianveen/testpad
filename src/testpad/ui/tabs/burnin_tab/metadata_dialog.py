import sys

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from testpad.config.defaults import ISO_8601_DATE_FORMAT
from testpad.core.burnin.model import BurninModel, Metadata


class MetadataDialog(QDialog):
    def __init__(self, parent=None) -> None:
        """Capture metadata for report title block.

        Custom dialog window to collect metadata from the user before generating
        a PDF report.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.

        """
        super().__init__(parent)
        self._model = BurninModel()
        self.setWindowTitle("Generate Report")
        self.setModal(True)
        # Set fixed window size
        self.setFixedSize(250, 200)

        self.main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.setLayout(self.main_layout)
        table_title_label = QLabel(
            self,
            text="Enter the following information\nbefore generating a report:\n",
        )
        self.main_layout.addWidget(table_title_label)
        self.main_layout.addLayout(self.form_layout)
        self._build_form()
        self._add_buttons()

    def set_initial_values(self, metadata: Metadata) -> None:
        """Set the initial values of the form fields from the given metadata.

        Args:
            metadata (Metadata): The metadata to use for setting the initial values.

        """
        self._tested_by_edit.setText(metadata.tested_by)
        self._test_name_edit.setText(metadata.test_name)
        self._date_edit.setDate(QDate.toPython(metadata.test_date))
        self._serial_number_edit.setText(metadata.rk300_serial)

    def _build_form(self) -> None:
        """Build the form layout for the dialog.

        Adds rows to the form layout for entering metadata.
        """
        self._tested_by_edit = QLineEdit(self)
        self.form_layout.addRow("Tested By: ", self._tested_by_edit)
        self._test_name_edit = QLineEdit(self)
        self.form_layout.addRow("Test Name: ", self._test_name_edit)
        self._date_edit = QDateEdit(self)
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat(ISO_8601_DATE_FORMAT)
        self.form_layout.addRow("Date: ", self._date_edit)
        self._serial_number_edit = QLineEdit(self)
        self.form_layout.addRow("RK-300 Serial #: ", self._serial_number_edit)

    def _add_buttons(self) -> None:
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText("Generate Report")
        ok_btn.setDefault(True)
        ok_btn.setAutoDefault(True)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.main_layout.addWidget(buttons)

    def _accept(self) -> None:
        super().accept()
        # Save metadata to model
        self.close()

    def get_metadata(self) -> dict:
        """Return the metadata collected by the dialog as a dictionary.

        This method is called after the dialog is accepted and returns the
        metadata collected by the dialog as a dictionary.

        Returns:
            dict: A dictionary containing the metadata collected by the dialog.

        """
        tested_by = self._tested_by_edit.text().strip()
        test_name = self._test_name_edit.text().strip()
        test_date = self._date_edit.date()
        rk300_serial = self._serial_number_edit.text().strip()
        return {
            "tested_by": tested_by,
            "test_name": test_name,
            "test_date": test_date,
            "rk300_serial": rk300_serial,
        }


def _main() -> None:
    app = QApplication(sys.argv)
    dialog = MetadataDialog()
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
