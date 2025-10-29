#!/usr/bin/env python
import os
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from PySide6 import QtWidgets, QtCore
from testpad.ui.tabs.burnin_tab.generate_report import GenerateReport

if TYPE_CHECKING:
    from testpad.ui.tabs.burnin_tab import BurninTab as BurninView


class BurninPresenter:
    def __init__(self, view: "BurninView") -> None:
        self._view = view

    def initialize(self) -> None:
        """Called after view is constructed."""
        # self._refresh_view()  # TODO: implement
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect view signals to presenter event handlers."""
        # TODO: implement
        self._view.connect_signals(self)

    def _on_select_file_cliked(self) -> None:
        """Called when the select file button is clicked."""
        # TODO: implement
        pass

    def _on_print_stats_toggled(self) -> None:
        """Called when the print stats checkbox is toggled."""
        # TODO: implement
        pass

    def _on_separate_eorros_toggled(self) -> None:
        """Called when the separate erors checkbox is toggled."""
        # TODO: implement
        pass

    def _on_print_graph_clicked(self) -> None:
        """Called when the print graph button is clicked."""
        # TODO: implement
        pass

    def _on_generate_report_clicked(self) -> None:
        """Genearte a PDF report when "GENERATE REPORT" button is clicked.

        Pass data to model for report generation.

        Raises:
            ValueError: If the report generation fails due to invalid state.
            RuntimeError: If the report generation fails due to an unknown error.

        """
        report_generator = GenerateReport()

        try:
            report_generator.generate_report()
        except (ValueError, RuntimeError) as e:
            (
                QtWidgets.QmessageBox.critical(
                    self._view,
                    "Report Generation Error",
                    f"Failed to generate report: {e}"
                    "\nConfirm the following before proceeding:"
                    "\n- Ensure you have write permissions for the output directory."
                    "\n- Close any open instances of the report file if it already exists."
                    "\n- Check if the output directory is valid and accessible.",
                ),
            )
        pass
