from Pyside6 import QtCore, QtWidgets

from testpad.ui.tabs.burnin_tab.view import BurninView as _view

# Collect report metadata via a quick popup dialog
dialog = QtWidgets.QDialog(_view)
dialog.setWindowTitle("Report Details")
form = QtWidgets.QFormLayout(dialog)

name_edit = QtWidgets.QLineEdit(dialog)
name_edit.setPlaceholderText("Your name")
date_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate(), dialog)
date_edit.setCalendarPopup(True)
serial_edit = QtWidgets.QLineEdit(dialog)
serial_edit.setPlaceholderText("Device serial number")

form.addRow("Tested By", name_edit)
form.addRow("Date", date_edit)
form.addRow("Device Serial #", serial_edit)

buttons = QtWidgets.QDialogButtonBox(
    QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
    parent=dialog,
)
buttons.accepted.connect(dialog.accept)
buttons.rejected.connect(dialog.reject)
form.addRow(buttons)

if dialog.exec() != QtWidgets.QDialog.Accepted:
    return

tested_by = name_edit.text().strip()
test_date_q = date_edit.date()
try:
    # PySide6 6.4+ provides toPython(); fallback to ISO string otherwise
    test_date = test_date_q.toPython()  # type: ignore[attr-defined]
except Exception:
    test_date = test_date_q.toString("yyyy-MM-dd")
device_serial = serial_edit.text().strip()

# Stash for downstream use (e.g., report generator)
_report_meta = {
    "tested_by": tested_by,
    "test_date": test_date,
    "RK-300_serial_number": device_serial,
}
