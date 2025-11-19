"""Contains the BurninPresenter class, which is the presenter for the Burnin tab."""

import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog

from testpad.config.plotting import (
    AVG_LINE_COLOR,
    PRIMARY_COLOR,
    PRIMARY_COMP_COLOR,
)
from testpad.core.burnin.burnin_stats import BurninStats
from testpad.core.burnin.model import BurninData, BurninFileInfo, BurninModel
from testpad.core.plotting.plotting import plot_x_multiple_y, plot_xy
from testpad.ui.tabs.burnin_tab.generate_pdf_report import GenerateReport
from testpad.ui.tabs.burnin_tab.metadata_dialog import MetadataDialog
from testpad.ui.tabs.burnin_tab.plotting import save_figure_to_temp_file

if TYPE_CHECKING:
    from testpad.ui.tabs.burnin_widget import BurninTab as BurninView


class BurninPresenter:
    """Burn in presenter connects view and model."""

    def __init__(self, model: BurninModel, view: "BurninView") -> None:
        """Burn in presenter connects view and model."""
        self._view = view
        self._model = model
        self._updating = False
        self._figures: list = []
        self._stats_classes: list = []

    def initialize(self) -> None:
        """Call after view is constructed."""
        self._refresh_view()
        self._connect_signals()

    def on_burnin_file_selected(self, filepaths: list[str]) -> None:
        """Call when a file is selected from the file dialog.

        Args:
            filepaths: List of file paths.

        """
        if self._updating:
            return
        paths = [Path(filepath) for filepath in filepaths]
        file_infos = [BurninFileInfo.from_path(path) for path in paths]
        if not self._all_same_test_number(file_infos):
            self._view.show_warning("Files from different tests were selected.")
            return
        self._model.set_burnin_files(file_infos)
        self._view.display_selected_files(filepaths)

    def _all_same_test_number(self, file_infos: list[BurninFileInfo]) -> bool:
        """Check if all files have the same test number.

        Args:
            file_infos: List of BurninFileInfo objects.

        Returns:
            bool: True if all files have the same test number, False otherwise.

        """
        # Check if all files have the same test number
        if not file_infos:
            return True
        first_test = file_infos[0].test_number
        return all(info.test_number == first_test for info in file_infos)

    def on_print_stats_toggled(self) -> None:
        """Call when the print stats checkbox is toggled."""
        if self._updating:
            return
        self._model.set_print_stats_option()

    def on_separate_errors_toggled(self) -> None:
        """Call when the separate erors checkbox is toggled."""
        if self._updating:
            return
        self._model.set_separate_errors_option()

    def on_moving_average_toggled(self) -> None:
        """Call when the separate erors checkbox is toggled."""
        if self._updating:
            return
        self._model.set_moving_average_option()

    def on_print_graph_clicked(self) -> None:
        """Call when the print graph button is clicked."""
        if self._updating:
            return
        if not self._model.has_burnin_file():
            self._view.show_warning("No burn-in file selected.")
            return
        # Clear previous figures and stats
        self._figures = []
        self._stats_classes = []
        self._view.graph_display.clear()

        # Get data
        burnin_file_infos = self._model.get_burnin_file()
        settings = self._model.get_graph_options_state()
        burnin_data = []
        max_workers = min(4, len(burnin_file_infos))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_info = {
                executor.submit(self._model.load_burnin_data, info): info
                for info in burnin_file_infos
            }
            for future in as_completed(future_to_info):
                data = future.result()
                burnin_data.append(data)

        # Generate figures based on settings
        figures = []
        # Always plot total error
        figures.extend(self._plot_total_axis_error(burnin_data))
        # Conditionally add separated errors
        if settings.separate_errors:
            figures.extend(self._plot_separated_error(burnin_data))
        # Conditionally add moving average
        if settings.moving_average:
            figures.extend(self._plot_error_and_moving_average(burnin_data))

        self._figures = figures  # can access this for the report
        # Send figures to view and tell it to display plots
        self._view.display_graphs(figures)

        # Conditionally display stats
        if settings.print_stats:
            self._display_stats(burnin_file_infos)

    def _plot_total_axis_error(self, burnin_data: list[BurninData]) -> list:
        """Plot the total axis error."""
        figures = []
        for data in burnin_data:
            labels = {
                "title": f"Axis {data.axis_name} Error",
                "xlabel": "Time (s)",
                "ylabel": "Error (counts)",
            }
            colors = [PRIMARY_COLOR if data.axis_name == "A" else PRIMARY_COMP_COLOR]
            figure = plot_xy(data.time, data.error, labels, colors)
            figure.suptitle(f"Axis {data.axis_name} Burn-in Error", alpha=0)
            figures.append(figure)
        return figures

    def _plot_separated_error(self, burnin_data: list[BurninData]) -> list:
        """Plot the error by axis."""
        figures = []
        for data in burnin_data:
            line_labels = {
                "title": f"Axis {data.axis_name} Error",
                "xlabel": "Time (s)",
                "ylabel": "Error (counts)",
            }
            data_labels = ["Positive Errors", "Negative Errors"]
            colors = [PRIMARY_COLOR, PRIMARY_COMP_COLOR]
            figure = plot_x_multiple_y(
                data.time,
                [data.positive_errors, data.negative_errors],
                line_labels,
                data_labels,
                colors,
            )

            figure.suptitle(f"Axis {data.axis_name} Error by Direction", alpha=0)
            figures.append(figure)
        return figures

    def _plot_error_and_moving_average(self, burnin_data: list[BurninData]) -> list:
        """Plot the error with moving average overlaid."""
        figures = []

        for data in burnin_data:
            signed_errors = [data.positive_errors, data.negative_errors]
            # Calculate moving average for both directions
            averages = [
                self._model.calculate_moving_average(error, 10000)
                for error in signed_errors
            ]
            for i, avg in enumerate(averages):
                direction = "Positive" if i == 0 else "Negative"
                line_labels = {
                    "title": f"Axis {data.axis_name} - {
                        direction
                    } Error with Moving Average",
                    "xlabel": "Time (s)",
                    "ylabel": "Error (counts)",
                }
                data_labels = ["Error Data", "Moving Average"]
                colors = [
                    (PRIMARY_COLOR if data.axis_name == "A" else PRIMARY_COMP_COLOR),
                    AVG_LINE_COLOR,
                ]
                figure = plot_x_multiple_y(
                    data.time,
                    [signed_errors[i], avg],
                    line_labels,
                    data_labels,
                    colors,
                )
                figure.suptitle(
                    f"Axis {data.axis_name} - {direction} Error w/ Moving Average",
                    alpha=0,
                )

                figures.append(figure)

        return figures

    def _display_stats(self, burnin_file_info: list[BurninFileInfo]) -> None:
        """Display the statistics in the textbox."""
        for file in burnin_file_info:
            stats_class = BurninStats(
                str(file.file_path), file.axis_name, self._view.text_display
            )
            stats_class.print_stats()
            self._stats_classes.append(stats_class)

    def on_generate_report_clicked(self) -> None:
        """Genearte a PDF report when "GENERATE REPORT" button is clicked.

        Pass data to model for report generation.

        Raises:
            ValueError: If the report generation fails due to invalid state.
            RuntimeError: If the report generation fails due to an unknown error.

        """
        # Check if file is selected
        if self._updating:
            return

        if not self._model.has_burnin_file():
            self._view.show_warning("No burn-in file selected.")
            return

        # Get data
        burnin_file_infos = self._model.get_burnin_file()

        # Check if stats exist; generate if not
        if self._stats_classes == [] or self._stats_classes is None:
            for file in burnin_file_infos:
                stats_class = BurninStats(
                    str(file.file_path), file.axis_name, self._view.text_display
                )
                self._stats_classes.append(stats_class)

        dialog = MetadataDialog(parent=self._view)
        initial_values = self._model.get_metadata()
        dialog.set_initial_values(initial_values)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_metadata()
            self._model.update_metadata(data)

        metadata = self._model.get_metadata()
        # Convert QDate to Python datetime.date for PDF generation
        test_date_value = metadata.test_date
        test_date = None
        if test_date_value is not None and isinstance(test_date_value, QDate):
            test_date = datetime.date(
                test_date_value.year(), test_date_value.month(), test_date_value.day()
            )
        report_meta = {
            "Tested By": metadata.tested_by,
            "Test Name": metadata.test_name,
            "Test Date": test_date,
            "RK300 Serial #": metadata.rk300_serial,
        }
        # Generate report
        # Create list for figures
        list_of_figs = self._figures

        list_of_pngs = [save_figure_to_temp_file(fig) for fig in list_of_figs]

        report_generator = GenerateReport(
            meta_data=report_meta,
            burnin_stats=self._stats_classes,
            list_of_temp_pngs=list_of_pngs,
        )

        try:
            report_generator.generate_report()
        except (ValueError, RuntimeError) as e:
            self._view.show_critical(
                f"Failed to generate report: {e}"
                "\nConfirm the following before proceeding:"
                "\n- Ensure you have write permissions for the output directory."
                "\n- Close open instances of the report file if it already exists."
                "\n- Check if the output directory is valid and accessible.",
            )
            # QMessageBox.critical(
            #     self._view,
            #     "Report Generation Error",
            #     f"Failed to generate report: {e}"
            #     "\nConfirm the following before proceeding:"
            #     "\n- Ensure you have write permissions for the output directory."
            #     "\n- Close open instances of the report file if it already exists."
            #     "\n- Check if the output directory is valid and accessible.",
            # )

    def _refresh_view(self) -> None:
        """Update all view widgets from current model state."""
        if self._updating:
            return

    def _connect_signals(self) -> None:
        """Connect view signals to presenter event handlers."""
        # TODO: implement
        self._view.connect_signals(self)
