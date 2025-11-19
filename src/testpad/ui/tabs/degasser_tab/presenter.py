"""Degasser tab presenter."""

from datetime import datetime
from typing import TYPE_CHECKING, cast

from PySide6.QtWidgets import QFileDialog

from testpad.config import DEFAULT_EXPORT_DIR

from .config import (
    MEASURED_COL_INDEX,
    PASS_FAIL_COL_INDEX,
    SPEC_MAX_COL_INDEX,
    SPEC_MIN_COL_INDEX,
)
from .generate_pdf_report import GenerateReport
from .model import DegasserModel
from .view_state import DegasserViewState

if TYPE_CHECKING:
    from .view import DegasserTab


class DegasserPresenter:
    """Degasser tab presenter."""

    def __init__(self, model: DegasserModel, view: "DegasserTab") -> None:
        self._model = model
        self._view = view
        self._state = DegasserViewState()
        self._updating = False

    def initialize(self) -> None:
        """Call after view is constructed."""
        self._refresh_view()
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect view signals to presenter event handlers."""
        self._view.connect_signals(self)

    def on_name_changed(self, text: str) -> None:
        """Handle name edit changes."""
        if self._updating:
            return
        self._model.set_metadata_field("tester_name", text)

    def on_location_changed(self, text: str) -> None:
        """Handle location edit changes."""
        if self._updating:
            return
        self._model.set_metadata_field("location", text)

    def on_date_changed(
        self,
        date,  # noqa: ANN001
    ) -> None:  # TODO: Add proper type hints for this workflow
        """Handle date edit changes."""
        if self._updating:
            return
        if not isinstance(date, datetime):
            self._model.set_metadata_field("test_date", date.toPython())

    def on_serial_changed(self, text: str) -> None:
        """Handle serial edit changes."""
        if self._updating:
            return
        self._model.set_metadata_field("ds50_serial", text)

    def on_test_table_cell_changed(self, row: int, column: int) -> None:
        """Handle test table cell changes."""
        if self._updating:
            return
        if column == 0:
            return

        # Get cell value (already returns a string, stripped)
        value = self._view.get_test_table_cell_value(row, column)

        try:
            if column == PASS_FAIL_COL_INDEX:  # Pass/Fail
                self._model.update_test_row(row, pass_fail=value)
            elif column == SPEC_MIN_COL_INDEX:  # Spec Min
                self._model.update_test_row(
                    row, spec_min=None if value.strip() == "" else value
                )
            elif column == SPEC_MAX_COL_INDEX:  # Spec Max
                self._model.update_test_row(
                    row, spec_max=None if value.strip() == "" else value
                )
            elif column == MEASURED_COL_INDEX:  # Data Measured
                self._model.update_test_row(
                    row, measured=None if value.strip() == "" else value
                )

        except ValueError as e:
            self._view.log_message(f"Test table error: {e}")

    def on_pass_fail_changed(self, row: int, value: str) -> None:
        """Handle pass/fail combo box changes.

        Args:
            row (int): The row index of the test table.
            value (str): The new pass/fail value from the combo box.

        Raises:
            ValueError: If the value is invalid.

        """
        if self._updating:
            return
        try:
            self._model.update_test_row(row, pass_fail=value)
        except ValueError as e:
            self._view.log_message(f"Pass/Fail error: {e}")

    def on_time_series_changed(self, row: int, column: int) -> None:
        """Handle time series table cell changes.

        Args:
            row (int): The row index of the time series table.
            column (int): The column index of the time series table.

        Raises:
            ValueError: If oxygen level is invalid.

        """
        if self._updating:
            return
        if column != 1:
            return
        value = self._view.get_time_series_cell_value(row, column)

        if value is None:
            try:
                self._model.clear_measurement(row)
                self._refresh_view()
                self._view.log_message(
                    f"Cleared oxygen level measurement at minute {row}"
                )
            except ValueError as e:
                self._view.log_message(f"Clear error: {e}")
            return

        # Try to set the measurement (value is guaranteed to be float here)
        try:
            self._model.set_measurement(row, value)
            self._refresh_view()
            self._view.log_message(f"Set oxygen level at minute {row} to {value} mg/L")
        except ValueError as e:
            self._view.log_message(f"Invalid oxygen level at minute {row}: {e}")

    def on_temperature_changed(self, temp: str | None = None) -> None:
        """Handle temperature edit changes.

        Args:
            temp (str): The new temperature value from the text field.

        Raises:
            ValueError: If temperature is out of valid range.

        """
        if self._updating:
            return
        if temp == "":
            self._model.clear_temperature()
            self._refresh_view()
        else:
            temp = cast("str", temp).strip()
            try:
                self._model.set_temperature(temp)
                self._refresh_view()
            except ValueError as e:
                self._view.log_message(f"Temperature error: {e}")

    def on_reset(self) -> None:
        """Handle reset button click - clear all data."""
        if self._updating:
            return

        # Confirmation dialog
        reply = self._view.question_dialog(
            "Confirm Reset Data",
            "Are you sure you want to reset all data? This action cannot be undone.",
        )

        if reply:
            self._model.reset()
            self._refresh_view()
            self._view.log_message("All data reset.")

    def on_generate_report(self) -> None:
        """Generate a PDF report when 'Generate Report' button is clicked.

        Passes data to model for report generation.

        Raises:
            ValueError: If report generation fails due to invalid state.
            Exception: For any other unexpected errors.

        """
        if self._updating:
            return
        data_dict = self._model.to_dict()
        time_series = data_dict["time_series"]
        temperature_c = data_dict["temperature_c"]
        metadata = data_dict["metadata"]
        test_data = data_dict["test_table"]

        output_path = DEFAULT_EXPORT_DIR

        report_generator = GenerateReport(
            time_series=time_series,
            metadata=metadata,
            test_data=test_data,
            temperature=temperature_c,
            output_dir=output_path,
        )
        try:
            report_generator.generate_report()
            self._view.log_message(
                "✅ Report generated successfully. "
                f"The report was saved to {output_path}"
            )
        except (ValueError, OSError) as e:
            self._view.log_message(f"❌ Report generation error: {e}")
            self._view.critical_dialog(
                title="Report Generation Error",
                text=f"Failed to generate report: {e}"
                "\nConfirm the following before proceeding:"
                "\n- Ensure you have write permissions for the output directory."
                "\n- Close any open instances of the report file if it already exists."
                "\n- Check if the output directory is valid and accessible.",
            )
        # except Exception as e:
        #     self._view.log_message(
        #         f"❌ Unexpected error during report generation: {e}"
        #     )
        #     self._view.critical_dialog(
        #         title="Report Generation Error",
        #         text=f"An unexpected error occurred: {e}",
        #     )

    def _on_import_csv(self) -> None:
        """Handle import CSV button click.

        Raises:
            ValueError: If import fails due to invalid file format.
            Exception: For any other unexpected errors.

        """
        if self._updating:
            return
        # TODO: remove pyside dependency
        path, _ = QFileDialog.getOpenFileName(
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
        # except Exception as e:
        #     self._view.log_message(f"❌ Unexpected error during import: {e}")

    def _on_export_csv(self) -> None:
        """Handle export CSV button click.

        Raises:
            ValueError: If export fails due to invalid state.
            Exception: For any other unexpected errors.

        """
        if self._updating:
            return
        timestamp = datetime.now().strftime("%y%m%d-%H%M%")
        # TODO: remove pyside dependency
        path, _ = QFileDialog.getSaveFileName(
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
        # except Exception as e:
        #     self._view.log_message(f"❌ Unexpected error during export: {e}")

    def _refresh_view(self) -> None:
        """Update all view widgets from current model state."""
        if self._updating:
            return
        self._updating = True
        try:
            state = self._build_view_state()
            self._view.update_view(state)
        finally:
            self._updating = False

    def _build_view_state(self) -> DegasserViewState:
        """Build a complete ViewState from the current model state.

        This method bridges Model and View - it extracts all
        necessary data from the model and packages it into a ViewState that
        the view can be updated.

        Returns:
            DegasserViewState containing all current display data

        """
        # Gather all data from model
        metadata = self._model.get_metadata()
        measurements = self._model.list_measurements()
        temperature_c = self._model.get_temperature_c()
        test_rows = self._model.get_test_rows()
        time_series_rows = self._model.build_time_series_rows()

        # Package into ViewState
        return DegasserViewState(
            tester_name=metadata.tester_name,
            location=metadata.location,
            ds50_serial=metadata.ds50_serial,
            test_date=metadata.test_date,
            time_series_measurements=measurements,
            temperature_c=temperature_c,
            test_rows=test_rows,
            time_series_table_rows=time_series_rows,
        )

    def shutdown(self) -> None:
        """Cleanup hooks/resources."""

    # Future example:
    def load_data(self) -> None:
        """Load data (stub)."""
