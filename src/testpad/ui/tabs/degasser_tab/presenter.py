from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING
import PySide6.QtCore
import PySide6.QtWidgets
from .model import DegasserModel
if TYPE_CHECKING:
    from .view import DegasserTab


class DegasserPresenter:
    """Placeholder presenter coordinating view <-> model."""

    def __init__(self, model: DegasserModel, view: "DegasserTab") -> None:
        self._model = model
        self._view = view

    def initialize(self) -> None:
        """Called after view is constructed."""
        self._connect_signals()
        self._refresh_view()
        pass

    def _connect_signals(self) -> None:
        """Connect view signals to presenter slots.
        
        Raises:
            ValueError: If any signal connection fails.
        """
        # Metadata fields
        self._view._name_edit.textChanged.connect(self._on_name_changed)
        self._view._location_edit.textChanged.connect(self._on_location_changed)
        self._view._date_edit.dateChanged.connect(self._on_date_changed)
        self._view._serial_edit.textChanged.connect(self._on_serial_changed)
        # Test Table Fields
        self._view._test_table.cellChanged.connect(self._on_test_table_cell_changed)
        # Time Series Fields
        self._view._time_series_widget.cellChanged.connect(self._time_series_changed)
        self._view._temperature_edit.textChanged.connect(self._on_temperature_changed)
        # Action Buttons
        self._view._import_csv_btn.clicked.connect(self._on_import_csv)
        self._view._export_csv_btn.clicked.connect(self._on_export_csv)
        self._view._generate_report_btn.clicked.connect(self._on_generate_report)
        self._view._reset_btn.clicked.connect(self._on_reset)

        # Pass/Fail combo boxes
        for row in range(7):
            if row == 3:
                continue
            combo = self._view._test_table.cellWidget(row, 1)
            if combo:
                combo.currentTextChanged.connect(
                    lambda text, r=row: self._on_pass_fail_changed(r, text)
                )

    def _on_name_changed(self, text: str) -> None:
        """Handle name edit changes."""
        self._model.set_metadata_field("tester_name", text)

    def _on_location_changed(self, text: str) -> None:
        """Handle location edit changes."""
        self._model.set_metadata_field("location", text)

    def _on_date_changed(self, date: Any) -> None:
        """Handle date edit changes."""
        self._model.set_metadata_field("test_date", date.toPython())

    def _on_serial_changed(self, text: str) -> None:
        """Handle serial edit changes."""
        self._model.set_metadata_field("ds50_serial", text)

    def _on_test_table_cell_changed(self, row: int, column: int) -> None:
        """Handle test table cell changes."""
        if column == 0:
            return

        item = self._view._test_table.item(row, column)
        if item is None:
            return

        value = item.text().strip()

        try:
            if column == 1:  # Pass/Fail
                self._model.update_test_row(row, pass_fail=value)
            elif column == 2:  # Spec Min
                self._model.update_test_row(row, spec_min=value if value else None)
            elif column == 3:  # Spec Max
                self._model.update_test_row(row, spec_max=value if value else None)
            elif column == 4:  # Data Measured
                self._model.update_test_row(row, measured=value if value else None)
        except ValueError as e:
            self._view.log_message(f"Test table error: {e}")

    def _on_pass_fail_changed(self, row: int, value: str) -> None:
        """Handle pass/fail combo box changes.
        
        Args:
            row (int): The row index of the test table.
            value (str): The new pass/fail value from the combo box.
        
        Raises:
            ValueError: If the value is invalid.
        """
        try:
            self._model.update_test_row(row, pass_fail=value)
        except ValueError as e:
            self._view.log_message(f"Pass/Fail error: {e}")

    def _time_series_changed(self, row: int, column: int) -> None:
        """Handle time series table cell changes.
        
        Args:
            row (int): The row index of the time series table.
            column (int): The column index of the time series table.

        Raises:
            ValueError: If oxygen level is invalid.
        """
        if column != 1:
            return
        item = self._view._time_series_widget.item(row, column)
        if item is None:
            return

        value = item.text().strip()

        if value == "":
            try:
                self._model.clear_measurement(row)
                self._view.log_message(
                    f"Cleared oxygen level measurement at minute {row}"
                )
                self._refresh_view()
            except ValueError as e:
                self._view.log_message(f"Clear error: {e}")
            return

        # Try to set the measurement
        try:
            self._model.set_measurement(row, value)
            self._view.log_message(
                f"Set oxygen level at minute {row} to {value} mg/L"
            )
            self._refresh_view()
        except ValueError as e:
            self._view.log_message(
                f"Invalid oxygen level at minute {row}: {e}"
            )
            item.setText("")  # Clear invalid entry

    def _on_temperature_changed(self, temp: str = None) -> None:
        """Handle temperature edit changes.
        
        Args:
            value (str): The new temperature value from the text field.

        Raises:
            ValueError: If temperature is out of valid range.
        """        
        if temp == "":
            self._model.clear_temperature()
            self._refresh_view()
        else:
            temp = temp.strip()
            try:
                self._model.set_temperature(temp)
                self._refresh_view()
            except ValueError as e:
                self._view.log_message(f"Temperature error: {e}")

    def _on_import_csv(self) -> None:
        """Handle import CSV button click.
        
        Raises:
            ValueError: If import fails due to invalid file format.
            Exception: For any other unexpected errors.
        """
        path, _ = PySide6.QtWidgets.QFileDialog.getOpenFileName(
            self._view,
            "Import Degasser Data",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not path:  # User cancelled
            return

        try:
            self._model.load_from_csv(path)
            self._refresh_view()  # Update UI with loaded data
            self._view.log_message(f"✅ Imported data from {path}")
        except ValueError as e:
            self._view.log_message(f"❌ Import error: {e}")
        except Exception as e:
            self._view.log_message(f"❌ Unexpected error during import: {e}")

    def _on_export_csv(self) -> None:
        """Handle export CSV button click.
        Raises:
            ValueError: If export fails due to invalid state.
            Exception: For any other unexpected errors.        
        """
        timestamp = datetime.now().strftime("%y%m%d-%H%M%")
        path, _ = PySide6.QtWidgets.QFileDialog.getSaveFileName(
            self._view,
            "Export Degasser Data",
            f"degasser_data_{timestamp}.csv",  # Filename + time stamp
            "CSV Files (*.csv);;All Files (*)",
        )

        if not path:  # User cancelled
            return

        try:
            self._model.export_csv(path)
            self._view.log_message(f"✅ Exported data to {path}")
        except ValueError as e:
            self._view.log_message(f"❌ Export error: {e}")
        except Exception as e:
            self._view.log_message(f"❌ Unexpected error during export: {e}")

    def _on_generate_report(self) -> None:
        """Handle generate report button click."""
        pass

    def _refresh_view(self) -> None:
        """Update all view widgets from current model state."""
        # Temporarily block signals
        self._block_signals(True)

        try:
            # 1. Refresh Metadata
            metadata = self._model.get_metadata()
            self._view._name_edit.setText(metadata.tester_name)
            self._view._location_edit.setText(metadata.location)
            self._view._serial_edit.setText(metadata.ds50_serial)
            if metadata.test_date:
                qdate = PySide6.QtCore.QDate(metadata.test_date)
                self._view._date_edit.setDate(qdate)

            # 2. Refresh Test Table
            self._refresh_test_table()
            # 3. Refresh Time Series
            self._refresh_time_series()
            # 4. Refresh Temperature
            temp = self._model.get_temperature_c()
            # 5. Refresh chart
            self._update_chart_widget()

            if not self._view._temperature_edit.hasFocus():
                if temp is not None:
                    self._view._temperature_edit.setText(f"{temp:.1f}")
                else:
                    self._view._temperature_edit.setText("")

        finally:
            self._block_signals(False)

    def _on_reset(self) -> None:
        """Handle reset button click - clear all data"""
        # Confirmation dialog
        reply = PySide6.QtWidgets.QMessageBox.question(
            self._view,
            "Confirm Reset Data",
            "Are you sure you want to reset all data? This action cannot be undone.",
            PySide6.QtWidgets.QMessageBox.StandardButton.Yes
            | PySide6.QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == PySide6.QtWidgets.QMessageBox.StandardButton.Yes:
            self._model.reset()
            self._refresh_view()
            self._view.log_message("All data reset.")

    def _refresh_test_table(self) -> None:
        """Update test table from model state."""
        rows = self._model.get_test_rows()

        for row_idx, row_data in enumerate(rows):
            # Column 0 (description) already set in view, read only
            # Column 1: Pass/Fail
            combo = self._view._test_table.cellWidget(row_idx, 1)
            if combo:
                combo.setCurrentText(row_data.pass_fail)

            # Column 2: Spec Min
            self._set_table_cell_float(row_idx, 2, row_data.spec_min)

            # Column 3: Spec Max
            self._set_table_cell_float(row_idx, 3, row_data.spec_max)

            # Column 4: Data Measured
            self._set_table_cell_float(row_idx, 4, row_data.measured)

    def _set_table_cell_float(self, row: int, col: int, value: Optional[float]) -> None:
        """Helper to set a table cell to a float value."""
        item = self._view._test_table.item(row, col)
        if item is None:
            item = PySide6.QtWidgets.QTableWidgetItem()
            self._view._test_table.setItem(row, col, item)

        if value is not None:
            item.setText(f"{value:.2f}")
        else:
            item.setText("")

    def _refresh_time_series(self) -> None:
        """Update time series table from model state."""
        time_series_rows = self._model.build_time_series_rows()

        for row_idx, (minute, oxygen_level) in enumerate(time_series_rows):
            # Column 0 (minute) already set in view, read only
            # Column 1: Dissolved O2
            oxy_item = self._view._time_series_widget.item(row_idx, 1)
            if oxy_item is None:
                oxy_item = PySide6.QtWidgets.QTableWidgetItem()
                self._view._time_series_widget.setItem(row_idx, 1, oxy_item)

            if oxygen_level is not None:
                oxy_item.setText(f"{oxygen_level:.2f}")
            else:
                oxy_item.setText("")

    def _update_chart_widget(self) -> None:
        """
        Chart widget for plotting time series data.

        Args:
            data: List[tuple[int, float]] - minute, oxygen pairs

        Raises:
            NotImplementedError: Placeholder for future charting implementation.
        """
        measurements = self._model.list_measurements()
        temperature_c = self._model.get_temperature_c()
        self._view.update_chart_widget(measurements, temperature_c)

    def shutdown(self) -> None:
        """Cleanup hooks/resources."""

    # Future example:
    def load_data(self, source: Any) -> None:
        """Load data (stub)."""

    def _block_signals(self, block: bool) -> None:
        """Helper to block/unblock signals from view widgets."""
        # Metadata fields
        self._view._name_edit.blockSignals(block)
        self._view._location_edit.blockSignals(block)
        self._view._date_edit.blockSignals(block)
        self._view._serial_edit.blockSignals(block)
        # Test Table Fields
        self._view._test_table.blockSignals(block)
        # Time Series Fields
        self._view._time_series_widget.blockSignals(block)
        self._view._temperature_edit.blockSignals(block)
        # Action Buttons
        self._view._import_csv_btn.blockSignals(block)
        self._view._export_csv_btn.blockSignals(block)
        self._view._generate_report_btn.blockSignals(block)