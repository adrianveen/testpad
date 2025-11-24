"""Degasser tab presenter."""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QDate # Import QDate

from .config import (
    MEASURED_COL_INDEX,
    PASS_FAIL_COL_INDEX,
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
        date: "QDate",
    ) -> None:
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
            elif column == MEASURED_COL_INDEX:  # Data Measured
                self._model.update_test_row(
                    row, measured=None if value.strip() == "" else value
                )
                # Refresh view to show auto-calculated Pass/Fail
                self._refresh_view()

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
        if row != 1:
            return
        value = self._view.get_time_series_cell_value(row, column)

        if value is None:
            try:
                self._model.clear_measurement(column)
                self._refresh_view()
                self._view.log_message(
                    f"Cleared oxygen level measurement at minute {column}"
                )
            except ValueError as e:
                self._view.log_message(f"Clear error: {e}")
            return

        # Try to set the measurement (value is guaranteed to be float here)
        try:
            self._model.set_measurement(column, value)
            self._refresh_view()
            self._view.log_message(
                f"Set oxygen level at minute {column} to {value} mg/L"
            )
        except ValueError as e:
            self._view.log_message(f"Invalid oxygen level at minute {column}: {e}")

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

    def on_select_output_folder_clicked(self) -> None:
        """Handle output folder selection button click."""
        if self._updating:
            return

        # Get the current output folder path
        current_path = str(self._model.get_output_directory())

        # Ask view to show dialog
        selected_path = self._view.show_folder_dialog(current_path)

        if selected_path:
            # Validate the path
            path = Path(selected_path)
            if not path.is_absolute():
                self._view.log_message("Error: Selected path must be absolute.")
                return

            # Update the model with the new path
            self._model.set_output_directory(path)

            # Update the UI with the new path
            self._refresh_view()
            self._view.log_message(f"Output folder set to {path}")

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

        # Validate any missing values before report generation
        missing_values = self._model.validate_for_report()
        if missing_values and not self._prompt_continue_missing_values(missing_values):
            # User cancelled
            self._view.log_message("Report generation cancelled")
            return

        data_dict = self._model.to_dict()
        time_series = data_dict["time_series"]
        temperature_c = data_dict["temperature_c"]
        metadata = data_dict["metadata"]
        test_data = data_dict["test_table"]

        output_path = self._model.get_output_directory()

        report_generator = GenerateReport(
            time_series=time_series,
            metadata=metadata,
            test_data=test_data,
            temperature=temperature_c,
            output_dir=output_path,
        )
        try:
            report_generator.generate_report()
            msg = (
                "Report generated successfully. The report was saved to:\n"
                f"{output_path}"
            )
            self._view.log_message(msg)
            self._view.info_dialog(title="Report Generated", text=msg)
        except FileExistsError:
            # Ask user how to handle
            title = "Report already exists"
            serial = data_dict["metadata"]["ds50_serial"]
            msg = (
                f"A file with the serial number '{serial}' already exists.\n"
                "How do you want to proceed?"
            )

            response = self._view.existing_file_dialog(title=title, text=msg)

            if response == "create_new_file":
                try:
                    # Let GenerateReport handle incrementing
                    generated_file = report_generator.generate_report(
                        auto_increment=True,
                    )
                    msg = (
                        "Report generated successfully. The report was saved to:\n"
                        f"{generated_file.parent}"
                    )
                    self._view.log_message(msg)
                    self._view.info_dialog(title="Report Generated", text=msg)
                except (ValueError, OSError) as err:
                    self._view.log_message(f"Error: {err}")
                    self._view.critical_dialog(
                        title="Error Generating Report",
                        text=f"Failed to generate report: {err}",
                    )
            elif response == "change_serial":
                # Cancel to allow user to change serial number
                return
            else:
                # User cancelled
                self._view.log_message("Report generation cancelled")

        except (ValueError, OSError, PermissionError) as e:
            self._view.log_message(f"Report generation error: {e}")
            self._view.critical_dialog(
                title="Report Generation Error",
                text=f"Failed to generate report: {e}"
                "\nConfirm the following before proceeding:"
                "\n- Ensure you have write permissions for the output directory."
                "\n- Close any open instances of the report file if it already exists."
                "\n- Check if the output directory is valid and accessible."
                f"\n\nOutput directory: {output_path}",
            )

    def _prompt_continue_missing_values(self, warnings: list[str]) -> bool:
        """Handle missing values dialog.

        Args:
            warnings: List of human-readable warning messages about missing data.

        Returns:
            The result of the dialog.
            "change_serial" if the user clicked the change serial button.
            "create_second_file" if the user clicked the create second file button.

        """
        title = "Missing Values"
        message = (
            "The following fields are missing or invalid:\n\n"
            + "\n".join(f"- {w}" for w in warnings)
            + "\n\nDo you want to continue generating the report anyway?"
        )
        return self._view.missing_values_dialog(title, message)

    def _on_import_csv(self) -> None:
        """Handle import CSV button click.

        Raises:
            ValueError: If import fails due to invalid file format.
            Exception: For any other unexpected errors.

        """
        if self._updating:
            return
        # TODO: move pyside dependency to view
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

    def _on_export_csv(self) -> None:
        """Handle export CSV button click.

        Raises:
            ValueError: If export fails due to invalid state.
            Exception: For any other unexpected errors.

        """
        if self._updating:
            return
        timestamp = datetime.now().strftime("%y%m%d-%H%M")
        # TODO: move pyside dependency to view
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
        output_dir = self._model.get_output_directory()

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
            output_directory=str(output_dir),
        )

    def shutdown(self) -> None:
        """Cleanup hooks/resources."""

    # Future example:
    def load_data(self) -> None:
        """Load data (stub)."""
