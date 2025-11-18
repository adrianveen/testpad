"""View for the Burn-in tab.

This module contains the Burn-in tab view, which is responsible for
displaying the burn-in graph and providing user interactions.

"""

import sys
from typing import TYPE_CHECKING

from matplotlib.backends.backend_qt import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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

from testpad.core.burnin.config import DEFAULT_PATH_BURNIN_DATA

if TYPE_CHECKING:
    from testpad.core.burnin.burnin_presenter import BurninPresenter


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
        self.canvas: FigureCanvas | None = None

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

    def display_graphs(self, figures: list[Figure]) -> None:
        """Display the given figures in the graph display.

        Args:
            figures: List of Figures objects to display.

        """
        canvases = self._create_figure_canvas_list(figures)
        self._create_graph_display(canvases)

    def _create_figure_canvas_list(self, figures: list[Figure]) -> list[FigureCanvas]:
        """Create a list of FigureCanvas objects from a list of Figure objects."""
        return [FigureCanvas(figure) for figure in figures]

    def _create_graph_display(self, canvas_list: list[FigureCanvas]) -> None:
        """Create a graph display with the given canvases."""
        nav_tool_list = [self._add_nav_toolbar(canvas) for canvas in canvas_list]

        for i, canvas in enumerate(canvas_list):
            display_widget = QWidget()
            display_layout = QVBoxLayout()
            display_widget.setLayout(display_layout)
            display_layout.addWidget(nav_tool_list[i])
            display_layout.addWidget(canvas)

            self.graph_display.addTab(
                display_widget, f"{canvas.figure.get_suptitle()}"
            )

    def show_warning(self, message: str) -> None:
        """Show a warning message in the text disqplay."""
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setWindowTitle("Warning")
        message_box.setText(message)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        message_box.exec()

    def show_critical(self, message: str) -> None:
        """Show a critical message in the text disqplay."""
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Critical)
        message_box.setWindowTitle("Critical Error")
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
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

        # Create buttons and apply stylesheet class
        self._print_graph_btn = QPushButton("Print Graph(s)")
        self._print_graph_btn.setProperty("class", "action-button")

        self._generate_report_btn_new = QPushButton("Generate Report")
        self._generate_report_btn_new.setProperty("class", "action-button")

        layout.addWidget(self._print_graph_btn)
        layout.addWidget(self._generate_report_btn_new)

        return widget

    def _build_text_display(self) -> QTextBrowser:
        self.text_display = QTextBrowser()
        return self.text_display

    def _build_graph_display(self) -> QTabWidget:
        self.graph_display = QTabWidget()
        return self.graph_display

    def _add_nav_toolbar(self, canvas: FigureCanvas) -> NavigationToolbar:
        """Add a NavigationToolbar to the canvas."""
        return NavigationToolbar(canvas, self)

    def _create_separated_error_graph_tab(self) -> None:
        """Create the separated error graph tab."""
        # TODO: possible remove this

    def _create_moving_average_graph_tab(self) -> None:
        """Create the moving average graph tab."""
        # TODO: possible remove this

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


def _main() -> None:
    app = QApplication(sys.argv)
    window = BurninTab()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
