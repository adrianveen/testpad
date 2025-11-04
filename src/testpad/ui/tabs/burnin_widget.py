"""View for the Burn-in tab.

This module contains the Burn-in tab view, which is responsible for
displaying the burn-in graph and providing user interactions.

"""

import sys
from typing import TYPE_CHECKING

from matplotlib.backends.backend_qt import (
    NavigationToolbar2QT as NavigationToolbar,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from testpad.core.burnin.burnin_graph import BurninGraph
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
    ) -> None:
        """Initialize the Burn-in tab view.

        Args:
            parent (QWidget): The parent widget for this Burn-in tab.

        Note:
            Presenter must be set via the factory function before use.

        """
        super().__init__(parent)

        self._construct_ui()
        self.presenter: BurninPresenter  # Type annotation - will be set by factory

    def connect_signals(self, presenter: "BurninPresenter") -> None:
        """Connect all view signals for burn-in tab to handlers.

        This is a public interface for the presenter/controller to
        register view events without accessing private widget members.

        Future work:
            - Expand to include all signals

        """
        self._select_burnin_file_btn.clicked.connect(self._on_burnin_file_clicked)
        self._summary_statistics_checkbox.toggled.connect(
            presenter.on_print_stats_toggled
        )
        self._separated_errors_checkbox.toggled.connect(
            presenter.on_separate_errors_toggled
        )
        self._moving_average_checkbox.toggled.connect(
            presenter.on_moving_average_toggled
        )
        self._print_graph_btn.clicked.connect(presenter.on_print_graph_clicked)
        self._generate_report_btn_new.clicked.connect(
            presenter.on_generate_report_clicked
        )

    def build_graph_display(self) -> QTabWidget:
        """Build the graph display."""
        self._new_graph_display = QTabWidget()
        self._graph_display.addTab(self._create_main_graph_tab(), "Burn-in Graph")
        return self._new_graph_display

    def show_warning(self, message: str) -> None:
        """Show a warning message in the text display."""
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setWindowTitle("Warning")
        message_box.setText(message)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        message_box.exec()

    def display_selected_files(self, filepaths: list[str]) -> None:
        """Display the selected burn-in files in the text display."""
        self.text_display.append("Burn-in File(s): ")
        for filepath in filepaths:
            self.text_display.append(f"  {filepath}\n")

    def _construct_ui(self) -> None:
        """Construct the user interface for the Burn-in tab.

        This method creates the user interface for the Burn-in tab, including
        the selections group, the print statistics checkbox, the separate errors
        checkbox, the moving average checkbox, and the print graph button.

        """
        # user interaction area
        main_layout = QGridLayout(self)
        main_layout.addWidget(self._build_selections_group(), 0, 0)
        main_layout.addWidget(self._build_output_btns(), 1, 0)
        main_layout.addWidget(self._build_text_display(), 2, 0)
        main_layout.addWidget(self._build_graph_display(), 0, 1, 3, 1)

    def _build_selections_group(self) -> QGroupBox:
        """Build the selections group for the Burn-in tab."""
        selections_group = QGroupBox()
        selections_layout = QGridLayout()

        self._select_burnin_file_btn = QPushButton("Select Burn-in File")
        self._summary_statistics_checkbox = QCheckBox("Print Summary Statistics")
        self._separated_errors_checkbox = QCheckBox(
            "Show error values separated by direction"
        )
        self._moving_average_checkbox = QCheckBox("Add moving average")

        selections_layout.addWidget(self._select_burnin_file_btn, 0, 0, 1, 2)
        selections_layout.addWidget(self._summary_statistics_checkbox, 1, 0)
        selections_layout.addWidget(self._separated_errors_checkbox, 2, 0)
        selections_layout.addWidget(self._moving_average_checkbox, 3, 0)
        selections_group.setLayout(selections_layout)

        return selections_group

    def _build_output_btns(self) -> QWidget:
        """Build the report button and its layout.

        Returns:
            QWidget: The report button and its layout

        """
        # Create parent widget to hold the button
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        # TODO: Move to stylesheet or config file

        button_style = "background-color: #66A366; color: black;"  # Create Widgets
        self._print_graph_btn = QPushButton("Print Graph(s)")
        self._print_graph_btn.setStyleSheet(
            button_style,
        )
        self._generate_report_btn_new = QPushButton("Generate Report")
        self._generate_report_btn_new.setStyleSheet(
            button_style,
        )
        layout.addWidget(self._print_graph_btn)
        layout.addWidget(self._generate_report_btn_new)

        return widget

    def _build_text_display(self) -> QTextBrowser:
        self.text_display = QTextBrowser()
        return self.text_display

    def _build_graph_display(self) -> QTabWidget:
        self._graph_display = QTabWidget()
        return self._graph_display

    def _create_main_graph_tab(self) -> None:
        """Create the main graph tab."""
        # burn_graph = self.burnin.get_graph()
        # nav_tool = NavigationToolbar(burn_graph)

        burn_widget = _MyQWidget(burnin_graph=self.burnin)
        burn_widget.setContentsMargins(5, 5, 5, 5)
        burn_layout = QVBoxLayout()
        burn_layout.setContentsMargins(5, 5, 5, 5)
        # burn_layout.addWidget(nav_tool)
        # burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)

    def _create_separated_error_graph_tab(self) -> None:
        """Create the separated error graph tab."""

    def _create_moving_average_graph_tab(self) -> None:
        """Create the moving average graph tab."""

    def _on_burnin_file_clicked(self) -> None:
        """Handle burn-in file selection button click."""
        if not hasattr(self, "presenter"):
            msg = "BurninTab.presenter not initialized. Use create_burnin_tab()\
            factory function instead of direct instantiation."
            raise RuntimeError(msg)

        # TODO: Move values to config file
        filepath = self._open_file_dialog(
            "Select Burn-in File",
            QFileDialog.FileMode.ExistingFiles,
            "*.hdf5",
            DEFAULT_PATH_BURNIN_DATA,
        )
        if filepath:
            self.presenter.on_burnin_file_selected(filepath)

    def _on_save_folder_clicked(self) -> None:
        filepath = self._open_file_dialog(
            "Select Save Folder",
            QFileDialog.FileMode.Directory,
            None,
            DEFAULT_PATH_BURNIN_DATA,
        )
        if filepath:
            self.text_display.append("Save Folder(s): ")
            self.save_folder = filepath[0]
        self.text_display.append(self.save_folder + "\n")

    def _open_file_dialog(
        self,
        # TODO: turn args into kwargs or list of args
        window_title: str,
        file_mode: QFileDialog.FileMode,
        name_filter: str | None,
        starting_directory: str,
    ) -> list[str] | None:
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(window_title)
        file_dialog.setFileMode(file_mode)
        if name_filter is not None:
            file_dialog.setNameFilter(name_filter)

        # Set starting directory
        file_dialog.setDirectory(str(starting_directory))

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            return files if files else None
        return None

    def _block_signals(self, block: bool) -> None:
        """Block or unblock signals from all input widgets.

        Used during programmatic updates to prevent triggering change handlers
        that would send updates back to the presenter (feedback loop).

        Args:
            block: True to block signals, False to unblock

        """
        # Metadata fields
        for name in self.__dict__:
            attr = getattr(self, name)
            attr.blockSignals(block)

    # prints burn-in graph with navigation tool bar to pan/zoom
    def _print_graphs(self, filepath: list[str]) -> None:
        # TODO: abstract to plotting module or something similar
        self._graph_display.clear()

        self.burnin = BurninGraph(
            filepath[0],
            [
                self._moving_average_checkbox.isChecked(),
                self._separated_errors_checkbox.isChecked(),
            ],
        )
        # self.stats_class = BurninStats(filepath[0], self.text_display)

        # Determine the axis name based on the filename
        if "_axis_A_" in filepath[0]:
            axis_name = "Axis A"
        elif "_axis_B_" in filepath[0]:
            axis_name = "Axis B"
        else:
            axis_name = "Unknown Axis"

        # Extract the test number after the last underscore
        try:
            test_number = (
                filepath[0].split("_")[-1].split(".")[0]
            )  # Split by underscore and get the last part, then remove file extension
        except IndexError:
            test_number = "Unknown"

        # Update text display with axis-specific and test number message.

        #     self.text_display.append(
        #         f"Summary Statistics for: {axis_name}; test no. {test_number}:\n",
        #     )
        #     # self.stats_class.print_stats()

        burn_graph = self.burnin.get_graph()
        nav_tool = NavigationToolbar(burn_graph)

        burn_widget = _MyQWidget(burnin_graph=self.burnin)
        burn_widget.setContentsMargins(5, 5, 5, 5)
        burn_layout = QVBoxLayout()
        burn_layout.setContentsMargins(5, 5, 5, 5)
        burn_layout.addWidget(nav_tool)
        burn_layout.addWidget(burn_graph)
        burn_widget.setLayout(burn_layout)

        self._graph_display.addTab(burn_widget, "Burn-in Graph")

        # Create Tab for separated error values
        if self._separated_errors_checkbox.isChecked():
            seperate_graph = self.burnin.get_graphs_separated()
            nav_tool_sep = NavigationToolbar(seperate_graph)
            separated_widget = _MyQWidget(burnin_graph=self.burnin)
            separated_widget.setContentsMargins(5, 5, 5, 5)
            separated_layout = QVBoxLayout()
            separated_layout.setContentsMargins(5, 5, 5, 5)
            separated_layout.addWidget(nav_tool_sep)
            separated_layout.addWidget(seperate_graph)
            separated_widget.setLayout(separated_layout)

            self._graph_display.addTab(
                separated_widget,
                "Error vs Time with directions separated",
            )
        else:
            pass

        # add tab for positive error and negative error if moving average is checked
        if self._moving_average_checkbox.isChecked():
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

            self._graph_display.addTab(
                pos_error_widget, "Positive Error w/ Moving Avg"
            )

            # create tab for negative error values
            nav_tool_neg = NavigationToolbar(neg_avg)

            neg_error_widget = _MyQWidget(burnin_graph=self.burnin)
            neg_error_widget.setContentsMargins(5, 5, 5, 5)
            neg_error_layout = QVBoxLayout()
            neg_error_layout.setContentsMargins(5, 5, 5, 5)
            neg_error_layout.addWidget(nav_tool_neg)
            neg_error_layout.addWidget(neg_avg)
            neg_error_widget.setLayout(neg_error_layout)

            self._graph_display.addTab(
                neg_error_widget, "Negative Error w/ Moving Avg"
            )
        else:
            pass


def _main() -> None:
    app = QApplication(sys.argv)
    window = BurninTab()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
