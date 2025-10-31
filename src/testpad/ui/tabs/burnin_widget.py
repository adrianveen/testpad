"""View for the Burn-in tab.

This module contains the Burn-in tab view, which is responsible for
displaying the burn-in graph and providing user interactions.

"""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from testpad.core.burnin.burnin_graph import BurninGraph
from testpad.core.burnin.burnin_stats import BurninStats
from testpad.core.burnin.config import DEFAULT_PATH_BURNIN_DATA

if TYPE_CHECKING:
    from testpad.core.burnin.burnin_presenter import BurninPresenter


class _MyQWidget(QWidget):
    def __init__(self, burnin_graph: BurninGraph) -> None:
        super().__init__()
        self.graph = burnin_graph

    def resizeEvent(self, event) -> None:
        self.graph.got_resize_event()


class BurninTab(QWidget):
    """Burn-in tab view."""

    def __init__(
        self,
        parent: QWidget | None = None,
        presenter: Optional["BurninPresenter"] = None,
    ) -> None:
        """Initialize the Burn-in tab view.

        Args:
            parent (QWidget): The parent widget for this Burn-in tab.
            presenter (BurninPresenter): The presenter for this Burn-in tab.

        """
        super().__init__(parent)

        self._presenter = presenter

        # user interaction area
        selections_group = QGroupBox()
        self.select_burnin_file_btn = QPushButton(
            "SELECT BURN-IN FILE",
        )  # checkbox for selecting burn-in file
        self.select_burnin_file_btn.clicked.connect(
            lambda: self._open_file_dialog("burn")
        )
        # check box for summary statistics
        self.print_statistics_lbl = QLabel(
            "Print Summary Statistics:",
        )  # checkbox for printing statistics
        self.print_statistics_box = QCheckBox()
        self.print_statistics_box.setChecked(
            False,
        )  # default for printing statistics is unchecked
        # check box to show separated error values by direction
        self.separate_errors_lbl = QLabel(
            "Show error values separated by direction:",
        )  # checkbox for separated error values
        self.separate_errors_box = QCheckBox()
        self.separate_errors_box.setChecked(
            False,
        )  # default for separated error values is unchecked
        # check box to show moving avg with separate graphs
        self.moving_avg_lbl = QLabel(
            "Add moving average:",
        )  # checkbox for adding a moving average
        self.moving_avg_box = QCheckBox()
        self.moving_avg_box.setChecked(
            False,
        )  # default for adding moving avg is unchecked
        # button to print graphs (this prints all selected graphs)
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #66A366; color: black;")
        self.print_graph_btn.clicked.connect(self._print_graphs)

        # layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_burnin_file_btn, 0, 0, 1, 2)
        # add print statistics label and checkbox
        selections_layout.addWidget(self.print_statistics_lbl, 1, 0)
        selections_layout.addWidget(self.print_statistics_box, 1, 1)
        # box to show separated error values by direction
        selections_layout.addWidget(self.separate_errors_lbl, 2, 0)
        selections_layout.addWidget(self.separate_errors_box, 2, 1)
        # add moving avg label and checkbox
        selections_layout.addWidget(self.moving_avg_lbl, 3, 0)
        selections_layout.addWidget(self.moving_avg_box, 3, 1)
        # print graph button - all figures produced with this button
        selections_layout.addWidget(self.print_graph_btn, 4, 0, 1, 2)
        _build_report_btn = self._build_report_btn()
        selections_layout.addWidget(self._build_report_btn(), 5, 0, 1, 2)
        selections_group.setLayout(selections_layout)

        self.text_display = QTextBrowser()

        self.graph_display = QTabWidget()

        # organizes layout in grid
        main_layout = QGridLayout()
        main_layout.addWidget(selections_group, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1, 2, 1)
        self.setLayout(main_layout)

    def connect_signals(self, presenter: "BurninPresenter") -> None:
        """Connect all view signals for burn-in tab to handlers.

        This is a public interface for the presenter/controller to
        register view events without accessing private widget members.

        Future work:
            - Expand to include all signals

        """
        # TODO: Connect Select Burn-in File button
        # TODO: Connect checkboxes for printing statistics, separated errors, moving average
        # TODO: Connect Print Graph button
        # Connect Generate Report button
        self._generate_report_btn.clicked.connect(presenter.on_generate_report_clicked)

    @Slot()
    # file dialog boxes
    def _open_file_dialog(self, d_type: str) -> None:
        default_path = str(DEFAULT_PATH_BURNIN_DATA)

        # check if default path exists, otherwise set to home directory
        if not Path(default_path).exists():
            default_path = os.path.expanduser("~")

        if d_type == "burn":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Burn-in File")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
            self.dialog1.setNameFilter("*.hdf5")

            # set default directory
            self.dialog1.setDirectory(default_path)

            if self.dialog1.exec():
                self.text_display.append("Burn-in File: ")
                self.burnin_file = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.burnin_file + "\n")

        elif (
            d_type == "save"
        ):  # not including save anymore because graph of burn-in is already saved as SVG
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Save Folder")
            self.dialog1.setFileMode(QFileDialog.FileMode.Directory)

            # set default directory
            self.dialog1.setDirectory(default_path)

            if self.dialog1.exec():
                self.text_display.append("Save Folder: ")
                self.save_folder = self.dialog1.selectedFiles()[0]
                self.text_display.append(self.save_folder + "\n")

    # prints burn-in graph with navigation tool bar to pan/zoom
    def _print_graphs(self) -> None:
        self.graph_display.clear()

        self.burnin = BurninGraph(
            self.burnin_file,
            [self.moving_avg_box.isChecked(), self.separate_errors_box.isChecked()],
        )
        self.stats_class = BurninStats(self.burnin_file, self.text_display)

        # Determine the axis name based on the filename
        if "_axis_A_" in self.burnin_file:
            axis_name = "Axis A"
        elif "_axis_B_" in self.burnin_file:
            axis_name = "Axis B"
        else:
            axis_name = "Unknown Axis"

        # Extract the test number after the last underscore
        try:
            test_number = self.burnin_file.split("_")[-1].split(".")[
                0
            ]  # Split by underscore and get the last part, then remove file extension
        except IndexError:
            test_number = "Unknown"

        # Update text display with axis-specific and test number message. Call printStats() as well
        if self.print_statistics_box.isChecked():
            self.text_display.append(
                f"Summary Statistics for: {axis_name}; test no. {test_number}:\n",
            )
            self.stats_class.print_stats()

        burn_graph = self.burnin.get_graph()
        nav_tool = NavigationToolbar(burn_graph)

        burn_widget = _MyQWidget(burnin_graph=self.burnin)
        burn_widget.setContentsMargins(5, 5, 5, 5)
        burn_layout = QVBoxLayout()
        burn_layout.setContentsMargins(5, 5, 5, 5)
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)

        self.graph_display.addTab(burn_widget, "Burn-in Graph")

        # Create Tab for separated error values
        if self.separate_errors_box.isChecked():
            seperate_graph = self.burnin.get_graphs_separated()
            nav_tool_sep = NavigationToolbar(seperate_graph)
            separated_widget = _MyQWidget(burnin_graph=self.burnin)
            separated_widget.setContentsMargins(5, 5, 5, 5)
            separated_layout = QVBoxLayout()
            separated_layout.setContentsMargins(5, 5, 5, 5)
            separated_layout.addWidget(nav_tool_sep)
            separated_layout.addWidget(seperate_graph)
            separated_widget.setLayout(separated_layout)

            self.graph_display.addTab(
                separated_widget,
                "Error vs Time with directions separated",
            )
        else:
            pass

        # add tab for positive error and negative error if moving average is checked
        if self.moving_avg_box.isChecked():
            # call moving_avg_plot() function from BurninGraph class
            pos_avg, neg_avg = self.burnin.moving_avg_plot()

            # create tab for positive error values
            nav_tool_pos = NavigationToolbar(pos_avg)

            pos_error_widget = _MyQWidget(burnin_graph=self.burnin)
            pos_error_widget.setContentsMargins(5, 5, 5, 5)
            pos_error_layout = QVBoxLayout()
            pos_error_layout.setContentsMargins(5, 5, 5, 5)
            pos_error_layout.addWidget(nav_tool_pos)
            pos_error_layout.addWidget(pos_avg)
            pos_error_widget.setLayout(pos_error_layout)

            self.graph_display.addTab(pos_error_widget, "Positive Error w/ Moving Avg")

            # create tab for negative error values
            nav_tool_neg = NavigationToolbar(neg_avg)

            neg_error_widget = _MyQWidget(burnin_graph=self.burnin)
            neg_error_widget.setContentsMargins(5, 5, 5, 5)
            neg_error_layout = QVBoxLayout()
            neg_error_layout.setContentsMargins(5, 5, 5, 5)
            neg_error_layout.addWidget(nav_tool_neg)
            neg_error_layout.addWidget(neg_avg)
            neg_error_widget.setLayout(neg_error_layout)

            self.graph_display.addTab(neg_error_widget, "Negative Error w/ Moving Avg")
        else:
            pass

    def _build_report_btn(self) -> QWidget:
        """Build the report button and its layout.

        Returns:
            QWidget: The report button and its layout

        **Future work**:
            Expand to build entire section instead of single button:
            - Add connection to report generation
            - Return QWidget in later version

        """
        # Create parent widget to hold the button
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Create Widgets (1 button for now
        # TODO: Epxand to include other buttons
        self._generate_report_btn = QPushButton("GENERATE REPORT")
        self._generate_report_btn.setStyleSheet(
            "background-color: #66A366; color: black;",
        )

        return self._generate_report_btn  # widget


def _main() -> None:
    app = QApplication(sys.argv)
    ex = BurninTab()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
