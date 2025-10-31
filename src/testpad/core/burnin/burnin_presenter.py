#!/usr/bin/env python
"""Contains the BurninPresenter class, which is the presenter for the Burnin tab."""

from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from testpad.core.burnin.burnin_graph import BurninGraph
from testpad.core.burnin.burnin_stats import BurninStats
from testpad.core.burnin.model import BurninModel
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

    def initialize(self) -> None:
        """Call after view is constructed."""
        # self._refresh_view()  # TODO: implement refresh view
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect view signals to presenter event handlers."""
        # TODO: implement
        self._view.connect_signals(self)

    def _on_select_file_cliked(self) -> None:
        """Call when the select file button is clicked."""
        # TODO: implement

    def _on_print_stats_toggled(self) -> None:
        """Call when the print stats checkbox is toggled."""
        # TODO: implement

    def _on_separate_eorros_toggled(self) -> None:
        """Call when the separate erors checkbox is toggled."""
        # TODO: implement

    def _on_print_graph_clicked(self) -> None:
        """Call when the print graph button is clicked."""
        # TODO: implement

    def on_generate_report_clicked(self) -> None:
        """Genearte a PDF report when "GENERATE REPORT" button is clicked.

        Pass data to model for report generation.

        Raises:
            ValueError: If the report generation fails due to invalid state.
            RuntimeError: If the report generation fails due to an unknown error.

        """
        # Check if file is selected
        if not hasattr(self._view, "burnin_file") or not self._view.burnin_file:
            QtWidgets.QMessageBox.warning(
                self._view,
                "No File",
                "Please select a burn-in file first",
            )
            return

        # Check if stats exist; generate if not
        if (
            not getattr(self._view, "stats_class", None)
            or self._view.stats_class is None
        ):
            self._view.stats_class = BurninStats(self._view.burnin_file, textbox=None)

        dialog = MetadataDialog(parent=self._view)
        initial_values = self._model.get_metadata()
        dialog.set_initial_values(initial_values)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_metadata()
            self._model.update_metadata(data)

        metadata = self._model.get_metadata()
        report_meta = {
            "Tested By": metadata.tested_by,
            "Test Name": metadata.test_name,
            "Test Date": metadata.test_date,
            "RK300 Serial #": metadata.rk300_serial,
        }
        # Generate report
        # Get figures from BurninGraph
        separate_errors_checked = self._view.separate_errors_box.isChecked()
        moving_avg_checked = self._view.moving_avg_box.isChecked()
        additional_plot_flags = [separate_errors_checked, moving_avg_checked]

        burnin = BurninGraph(self._view.burnin_file, additional_plot_flags)
        # Create list for figures
        list_of_figs = []
        # Get main figure
        main_canvas = burnin.get_graph()
        main_fig = main_canvas.figure
        list_of_figs.append(main_fig)
        # Get saparated figure
        if self._view.separate_errors_box.isChecked():
            separate_canvas = burnin.get_graphs_separated()
            separate_fig = separate_canvas.figure
            list_of_figs.append(separate_fig)
        else:
            pass

        # Moving Averages
        if self._view.moving_avg_box.isChecked():
            pos_canvas, neg_canvas = burnin.moving_avg_plot()
            pos_avg_fig = pos_canvas.figure
            neg_avg_fig = neg_canvas.figure
            list_of_figs.append(pos_avg_fig)
            list_of_figs.append(neg_avg_fig)
        else:
            pass

        list_of_pngs = [save_figure_to_temp_file(fig) for fig in list_of_figs]

        report_generator = GenerateReport(
            meta_data=report_meta,
            burnin_stats=self._view.stats_class,
            figures=list_of_pngs,
        )

        try:
            report_generator.generate_report()
        except (ValueError, RuntimeError) as e:
            QtWidgets.QMessageBox.critical(
                self._view,
                "Report Generation Error",
                f"Failed to generate report: {e}"
                "\nConfirm the following before proceeding:"
                "\n- Ensure you have write permissions for the output directory."
                "\n- Close open instances of the report file if it already exists."
                "\n- Check if the output directory is valid and accessible.",
            )
