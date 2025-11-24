"""Degasser Tab View.

This module provides the user interface for the Degasser Tab.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast, override

import PySide6.QtCore
from PySide6.QtCore import QDate, QSignalBlocker, Qt
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent, QModelIndex, QObject, QPersistentModelIndex
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QStyleOptionViewItem


from testpad.config.defaults import ISO_8601_DATE_FORMAT
from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.degasser_tab.chart_widgets import TimeSeriesChartWidget
from testpad.ui.tabs.degasser_tab.config import (
    DEFAULT_TEST_DESCRIPTIONS,
    DEFAULT_TIME_SERIES_TEMP,
    DS50_DECIMAL_PRECISION,
    DS50_SPEC_RANGES,
    DS50_SPEC_UNITS,
    HEADER_ROW_COLOR,
    HEADER_ROW_INDEX,
    MEASURED_COL_INDEX,
    METADATA_FIELDS,
    NO_LIMIT_SYMBOL,
    NUM_TEST_COLS,
    NUM_TEST_ROWS,
    NUM_TIME_SERIES_COLS,
    NUM_TIME_SERIES_ROWS,
    ROW_SPEC_MAPPING,
    SPEC_MAX_COL_INDEX,
    SPEC_MIN_COL_INDEX,
    TEST_TABLE_HEADERS,
    TIME_SERIES_HEADERS,
)
from testpad.ui.tabs.degasser_tab.model import DegasserModel, TestResultRow
from testpad.ui.tabs.degasser_tab.presenter import DegasserPresenter
from testpad.ui.tabs.degasser_tab.view_state import DegasserViewState


class ColumnMajorTableWidget(QTableWidget):
    """QTableWidget with column-major tab navigation (top→bottom, left→right).

    Overrides default Qt behavior where Tab moves left→right across columns.
    Instead, Tab moves top→bottom within a column, then wraps to the next column.
    """

    def _get_next_cell(
        self, row: int, col: int, *, forward: bool = True
    ) -> tuple[int, int]:
        """Calculate next cell position in column-major order.

        Column-major order means: fill cells vertically down a column, then move
        to the next column. For example, in a 3x2 table, the order is:
        (0,0) → (1,0) → (2,0) → (0,1) → (1,1) → (2,1) → wraps back to (0,0)

        Args:
            row: Current row index (0-based)
            col: Current column index (0-based)
            forward: True to move forward (Tab), False to move backward (Shift+Tab)

        Returns:
            Tuple of (new_row, new_col) representing the next cell position

        """
        rows, cols = self.rowCount(), self.columnCount()

        if forward:
            # Forward navigation: down column, then right to next column
            if row < rows - 1:
                # Not at bottom of column yet, move down one row
                return row + 1, col
            if col < cols - 1:
                # At bottom of column, jump to top of next column
                return 0, col + 1
            # At bottom-right corner, wrap around to top-left
            return 0, 0
        # Backward navigation: up column, then left to previous column
        if row > 0:
            # Not at top of column yet, move up one row
            return row - 1, col
        if col > 0:
            # At top of column, jump to bottom of previous column
            return rows - 1, col - 1
        # At top-left corner, wrap around to bottom-right
        return rows - 1, cols - 1

    @override
    def keyPressEvent(self, event: "QKeyEvent") -> None:
        """Override Qt's default key handling to implement column-major navigation.

        By default, QTableWidget uses row-major Tab navigation (left→right).
        This override intercepts Tab/Enter/Backtab keys and implements column-major
        navigation instead. Other keys are passed to Qt's default handler.
        """
        key = event.key()

        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Tab and Enter both move forward in column-major order
            event.accept()  # Prevent Qt's default row-major navigation
            new_row, new_col = self._get_next_cell(
                self.currentRow(),
                self.currentColumn(),
                forward=True,
            )
            self.setCurrentCell(new_row, new_col)
        elif key == Qt.Key.Key_Backtab:
            # Shift+Tab moves backward in column-major order
            event.accept()  # Prevent Qt's default behavior
            new_row, new_col = self._get_next_cell(
                self.currentRow(),
                self.currentColumn(),
                forward=False,
            )
            self.setCurrentCell(new_row, new_col)
        else:
            # For all other keys (arrows, letters, etc.), use Qt's default handling
            super().keyPressEvent(event)


class ColumnMajorNavigationMixin:
    """Mixin for item delegates to support column-major navigation during cell editing.

    This mixin installs an event filter on editor widgets to intercept Tab/Enter
    keys and forward them to the table's navigation logic. Any delegate class that
    inherits from this mixin will automatically support column-major navigation during
    editing.

    Usage: class MyDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate): ...
    Note: Mixin must come BEFORE QStyledItemDelegate in the inheritance list
    for proper MRO.

    """

    def eventFilter(self, watched: "QObject", event: "QEvent") -> bool:
        """Intercept key events from editor widgets and redirect navigation keys.

        When we detect Tab/Enter, we bypass the editor and send the event directly
        to the table's keyPressEvent for custom handling.

        Args:
            watched: The object being watched (the editor widget)
            event: The QEvent being processed

        Returns:
            True if event was handled (prevents further processing)
            False to allow normal event propagation

        """
        if event.type() == PySide6.QtCore.QEvent.Type.KeyPress:
            # Cast to QKeyEvent to access key()
            key_event: QKeyEvent = event  # type: ignore[assignment]
            if key_event.key() in (
                Qt.Key.Key_Tab,
                Qt.Key.Key_Backtab,
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            ):
                # This is a navigation key - don't let the editor process it
                table = self.parent()  # type: ignore[attr-defined]  # Delegate's parent is the table widget
                if isinstance(table, ColumnMajorTableWidget):
                    # Forward the event to the table's custom navigation handler
                    table.keyPressEvent(key_event)
                    return True  # Event handled, stop propagation
        # Not a navigation key, or not our custom table - use default behavior
        return super().eventFilter(watched, event)  # type: ignore[misc]

    def createEditor(
        self,
        parent: QWidget | None,
        option: "QStyleOptionViewItem",
        index: "QModelIndex | QPersistentModelIndex",
    ) -> QWidget:
        """Create editor widget and install this delegate as an event filter.

        Qt calls this method when a cell begins editing.

        Args:
            parent: Parent widget for the editor (the table viewport)
            option: Style options for the editor
            index: Model index of the cell being edited

        Returns:
            The editor widget with event filter installed

        """
        editor = super().createEditor(parent, option, index)  # type: ignore[misc]
        if editor:
            # Install this delegate as an event filter on the editor
            # Now our eventFilter() method will intercept the editor's key events
            editor.installEventFilter(self)  # type: ignore[attr-defined]
        return editor


class DegasserTab(BaseTab):
    """Degasser tab view."""

    def __init__(
        self,
        parent: QWidget | None = None,
        model: DegasserModel | None = None,
        presenter: DegasserPresenter | None = None,
    ) -> None:
        """Initialize the Degasser tab.

        Args:
            parent: The parent widget for this tab.
            model: The model object for the tab.
            presenter: The presenter object for the tab.

        """
        super().__init__(parent)

        self._model = model
        self.presenter = presenter
        self._time_series_chart = TimeSeriesChartWidget()
        self._time_series_section: QWidget | None = None
        self._construct_ui()

    def _construct_ui(self) -> None:
        layout = QGridLayout(self)
        layout.addWidget(self._build_metadata_section(), 0, 0, 1, 2)
        layout.addWidget(self._build_test_table(), 1, 0, 1, 2)
        layout.addWidget(self._build_time_series_table(), 2, 0, 1, 1)
        layout.addWidget(self._build_action_buttons(), 3, 0, 1, 2)
        layout.addWidget(self._build_console_section(), 4, 0, 1, 2)
        layout.setRowStretch(0, 0)  # Metadata section not stretchable
        layout.setRowStretch(1, 0)  # Test table section not stretchable
        layout.setRowStretch(2, 1)  # Time series section stretchable
        layout.setRowStretch(3, 0)  # Action buttons not stretchable
        layout.setRowStretch(4, 0)  # Console section not stretchable

    def update_view(self, state: DegasserViewState) -> None:
        """Update the view based on the provided state.

        This is the primary interface between Presenter and View. The Presenter
        creates a ViewState from the Model and passes it here. This method
        updates all UI widgets to reflect the state.

        Args:
            state: Complete UI state to accurately update the view

        Note: This method handles signal blocking internally to prevent
            feedback loops during updates.

        """
        self._block_signals(block=True)
        try:
            # Update Metadata
            self._name_edit.setText(state.tester_name)
            self._location_edit.setText(state.location)
            self._serial_edit.setText(state.ds50_serial)
            if state.test_date is not None:
                # Convert Python date to QDate for type safety
                qdate = QDate(
                    state.test_date.year,
                    state.test_date.month,
                    state.test_date.day,
                )
                self._date_edit.setDate(qdate)

            # Update Chart
            self._time_series_chart.update_plot(
                state.time_series_measurements, state.temperature_c
            )

            # Update temperature display
            # Only update if field is not in focus - user may be editing
            if not self._temperature_edit.hasFocus():
                if state.temperature_c is not None:
                    self._temperature_edit.setText(f"{state.temperature_c:.1f}")
                else:
                    self._temperature_edit.setText("")

            self._update_test_table(state.test_rows)

            self._update_time_series_table(state.time_series_table_rows)
            self._output_dir_line_edit.setText(state.output_directory)

        finally:
            self._block_signals(block=False)

    def connect_signals(self, presenter: "DegasserPresenter") -> None:
        """Connect all view signals to presenter event handlers.

        This is the public interface for the Presenter to register
        view events without accessing private widget memebers.

        Args:
            presenter: The presenter instance with event handler methods

        """
        # Metadata fields
        self._name_edit.textChanged.connect(presenter.on_name_changed)
        self._location_edit.textChanged.connect(presenter.on_location_changed)
        self._date_edit.dateChanged.connect(presenter.on_date_changed)
        self._serial_edit.textChanged.connect(presenter.on_serial_changed)

        # Test Table
        self._test_table.cellChanged.connect(presenter.on_test_table_cell_changed)

        # Time Series
        self._time_series_widget.cellChanged.connect(presenter.on_time_series_changed)
        self._temperature_edit.textChanged.connect(presenter.on_temperature_changed)

        # Action Buttons
        self._select_output_folder_btn.clicked.connect(
            presenter.on_select_output_folder_clicked
        )
        self._generate_report_btn.clicked.connect(presenter.on_generate_report)
        self._reset_btn.clicked.connect(presenter.on_reset)

        # Pass/Fail Combo Boxes
        for row in range(NUM_TEST_ROWS):
            if row == HEADER_ROW_INDEX:
                continue
            combo = self._test_table.cellWidget(row, 1)
            if combo:
                combo = cast("QComboBox", combo)
                combo.textActivated.connect(
                    lambda text, r=row: presenter.on_pass_fail_changed(r, text)
                )
        # TODO: Add CSV import and export connections

    def get_test_table_cell_value(self, row: int, column: int) -> str:
        """Get the text value from a test table cell.

        Args:
          row: Row index
          column: Column index

        Returns:
          Cell text value, or empty string if cell doesn't exist

        """
        item = self._test_table.item(row, column)
        if item is None:
            return ""

        if column == MEASURED_COL_INDEX:
            edit_value = item.data(Qt.ItemDataRole.EditRole)
            if edit_value not in (None, ""):
                return str(edit_value).strip()

        return item.text().strip()

    def get_time_series_cell_value(self, row: int, column: int) -> float | None:
        """Get the numeric value from a time series table cell.

        Args:
          row: Row index
          column: Column index

        Returns:
          Cell value as float, or None if cell is empty

        Raises:
          ValueError: If cell text is not a valid number

        """
        item = self._time_series_widget.item(row, column)
        if item is None:
            return None

        text = item.text().strip()
        if not text:
            return None

        try:
            return float(text)
        except ValueError:
            return None

    def show_folder_dialog(self, current_path: str = "") -> str | None:
        """Show folder selection dialog and return the selected path.

        Args:
            current_path: The current path to set as the initial directory.
                Will attempt to create this directory if it doesn't exist.
                Falls back to Qt default if creation fails.

        Returns:
            The selected path, or None if the dialog was cancelled.

        """
        # Try to ensure the default directory exists
        start_path = ""
        if current_path:
            try:
                path_obj = Path(current_path)
                path_obj.mkdir(parents=True, exist_ok=True)
                if path_obj.exists() and path_obj.is_dir():
                    start_path = current_path
            except (OSError, PermissionError):
                # Fall back to Qt default (empty string)
                pass

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            start_path,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        return folder if folder else None

    def question_dialog(self, title: str, text: str) -> bool:
        """Show a question dialog and return the result."""
        reply = QMessageBox.question(
            self,
            title,
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def info_dialog(self, title: str, text: str) -> bool:
        """Show an info dialog."""
        reply = QMessageBox.information(
            self,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )
        return reply == QMessageBox.StandardButton.Ok

    def warning_dialog(self, title: str, text: str) -> bool:
        """Show a warning dialog."""
        reply = QMessageBox.warning(
            self,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )
        return reply == QMessageBox.StandardButton.Ok

    def critical_dialog(self, title: str, text: str) -> bool:
        """Show a critical dialog."""
        reply = QMessageBox.critical(
            self,
            title,
            text,
            QMessageBox.StandardButton.Ok,
        )
        return reply == QMessageBox.StandardButton.Ok

    def existing_file_dialog(self, title: str, text: str) -> str:
        """Show an existing file dialog.

        Args:
            title: The title of the dialog.
            text: The text of the dialog.

        Returns:
            The result of the dialog.
            "change_serial" if the user clicked the change serial button.
            "create_second_file" if the user clicked the create second file button.

        """
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setText(text)
        message_box.setWindowTitle(title)
        change_serial = message_box.addButton(
            "Change Serial Number", QMessageBox.ButtonRole.RejectRole
        )
        create_second_file = message_box.addButton(
            "Create New Report", QMessageBox.ButtonRole.ApplyRole
        )
        message_box.exec()
        if message_box.clickedButton() == change_serial:
            return "change_serial"
        if message_box.clickedButton() == create_second_file:
            return "create_new_file"
        return ""

    def missing_values_dialog(self, title: str, text: str) -> bool:
        """If values are missing, prompt the user on how to proceed.

        Args:
            title: The title of the dialog.
            text: The text of the dialog.

        Returns:
            True if the user clicked continue, False if they clicked cancel.

        """
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setStandardButtons(
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes
        )
        message_box.setDefaultButton(QMessageBox.StandardButton.Cancel)

        return message_box.exec() == QMessageBox.StandardButton.Yes

    def _build_metadata_section(self) -> QWidget:
        """Build the metadata section."""
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._name_edit = QLineEdit()
        self._location_edit = QLineEdit()
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat(ISO_8601_DATE_FORMAT)  # ISO 8601 format
        self._serial_edit = QLineEdit()

        # Layout
        layout.addWidget(
            QLabel(f"{METADATA_FIELDS['tester_name']}: "),
            0,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(self._name_edit, 0, 1)
        layout.addWidget(
            QLabel(f"{METADATA_FIELDS['test_date']}: "),
            0,
            2,
            Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(self._date_edit, 0, 3)
        layout.addWidget(
            QLabel(f"{METADATA_FIELDS['ds50_serial_number']}: "),
            1,
            0,
            Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(self._serial_edit, 1, 1)
        layout.addWidget(
            QLabel(f"{METADATA_FIELDS['location']}: "),
            1,
            2,
            Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(self._location_edit, 1, 3)

        return widget

    def _build_test_table(self) -> QWidget:
        """Build the test table section."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create Widgets - use custom widget with column-major tab navigation
        self._test_table = ColumnMajorTableWidget(NUM_TEST_ROWS, NUM_TEST_COLS)
        self._test_table.setHorizontalHeaderLabels(TEST_TABLE_HEADERS)
        self._test_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )  # Disable vertical scrollbar

        units_by_row: dict[int, str] = {}

        self._populate_test_table_rows(units_by_row)

        # Configure table headers
        header = self._test_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Set a fixed height to prevent scrollbars based on table contents
        fixed_height = self._autosize_table(self._test_table)
        self._test_table.setFixedHeight(fixed_height)
        self._test_table.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )

        self._test_table.setItemDelegateForColumn(
            4, _MeasuredValueDelegate(units_by_row, self._test_table)
        )

        layout.addWidget(self._test_table)
        return widget

    def _populate_test_table_rows(self, units_by_row: dict[int, str]) -> None:
        """Populate the test table with default rows and specs."""
        # Pre-fill descriptions (these are read-only)
        for row, desc in enumerate(DEFAULT_TEST_DESCRIPTIONS):
            # Column 0: Description only
            item = QTableWidgetItem(desc)
            item.setFlags(
                item.flags() & ~PySide6.QtCore.Qt.ItemFlag.ItemIsEditable
            )  # Make read-only
            # Bold and gray background for re-circulation header rows
            if row == HEADER_ROW_INDEX:
                font = item.font()
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)
                item.setFont(font)
                item.setBackground(HEADER_ROW_COLOR)  # Light gray background
                # Span all columns for 2nd re-circulation header
                self._test_table.setSpan(HEADER_ROW_INDEX, 0, 1, NUM_TEST_COLS)
            self._test_table.setItem(row, 0, item)

            # Get spec key for this row (None for header row)
            spec_key = ROW_SPEC_MAPPING[row]

            # Only add spec cells for non-header rows
            if spec_key is not None:
                self._populate_spec_cells(row, spec_key, units_by_row)

            if row != HEADER_ROW_INDEX:
                # Column 1: Pass/Fail dropdown for non header rows
                pass_fail_combo = QComboBox()
                pass_fail_combo.addItems(["", "Pass", "Fail"])
                self._test_table.setCellWidget(row, 1, pass_fail_combo)

    def _populate_spec_cells(
        self, row: int, spec_key: str, units_by_row: dict[int, str]
    ) -> None:
        """Populate spec cells for a given row."""
        spec = DS50_SPEC_RANGES.get(spec_key, (None, None))
        unit = DS50_SPEC_UNITS.get(spec_key, "")

        if unit:
            units_by_row[row] = unit

        for col in range(2, NUM_TEST_COLS):
            if col == SPEC_MIN_COL_INDEX:  # Spec_Min
                if spec[0] is None:
                    spec_value = NO_LIMIT_SYMBOL
                else:
                    spec_value = f"{spec[0]} {unit}" if unit else str(spec[0])
            elif col == SPEC_MAX_COL_INDEX:  # Spec_Max
                if spec[1] is None:
                    spec_value = NO_LIMIT_SYMBOL
                else:
                    spec_value = f"{spec[1]} {unit}" if unit else str(spec[1])
            else:  # Data Measured (col == 4)
                spec_value = ""

            spec_item = QTableWidgetItem(spec_value)
            spec_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col in (2, 3):  # Spec columns are read-only
                spec_item.setFlags(
                    spec_item.flags() & ~PySide6.QtCore.Qt.ItemFlag.ItemIsEditable
                )
            self._test_table.setItem(row, col, spec_item)

    def _build_time_series_table(self) -> QWidget:
        """Build just the time series table."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self._time_series_widget = QTableWidget(
            NUM_TIME_SERIES_ROWS, NUM_TIME_SERIES_COLS
        )
        self._time_series_widget.setVerticalHeaderLabels(TIME_SERIES_HEADERS)
        self._time_series_widget.verticalHeader().setVisible(True)

        # Hide the horizontal header (column numbers)
        self._time_series_widget.horizontalHeader().setVisible(False)

        # Configure fixed column widths (all uniform for minutes 0-20)
        h_header = self._time_series_widget.horizontalHeader()
        # h_header.setDefaultSectionSize(35)  # Fixed width for each column
        h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Configure fixed row heights
        v_header = self._time_series_widget.verticalHeader()
        v_header.setDefaultSectionSize(35)  # Increased from 30 for more space
        # v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Enable horizontal scrollbar when needed, disable vertical scrollbar
        self._time_series_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._time_series_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Populate table cells
        for col in range(NUM_TIME_SERIES_COLS):
            minute_item = QTableWidgetItem(str(col))
            minute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            minute_item.setFlags(
                minute_item.flags() & ~PySide6.QtCore.Qt.ItemFlag.ItemIsEditable
            )
            self._time_series_widget.setItem(0, col, minute_item)
            # Oxygen column - pre-create empty editable cells for alignment purposes
            oxygen_item = QTableWidgetItem()
            oxygen_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._time_series_widget.setItem(1, col, oxygen_item)

        # Set fixed height for table
        fixed_height = self._autosize_table(self._time_series_widget)
        self._time_series_widget.setFixedHeight(fixed_height)

        # Add table to layout
        layout.addWidget(self._time_series_widget)

        # Create and add temperature widget to layout
        temp_layout = self._add_temperature_layout()
        layout.addLayout(temp_layout)

        # Add chart to layout with stretch factor to fill remaining vertical space
        self._time_series_chart.setMinimumHeight(300)
        layout.addWidget(self._time_series_chart, 1)

        self._time_series_section = widget

        return widget

    def _add_temperature_layout(self) -> QHBoxLayout:
        """Build temperate widget and layout."""
        # Create temperature widget layout and checkbox
        temp_layout = QHBoxLayout()
        temp_checkbox = QCheckBox("Water Temperature Measured (°C):")
        temp_checkbox.setChecked(False)
        # Create temperature line edit widget with behaviour
        self._temperature_edit = QLineEdit()
        self._temperature_edit.hide()  # Start hidden
        self._temperature_edit.setEnabled(False)
        self._temperature_edit.setText("")  # Start empty
        self._temperature_edit.setPlaceholderText("Optional")
        self._temperature_edit.setMaximumWidth(75)
        # Add widgets to layout
        temp_layout.addWidget(temp_checkbox)
        temp_layout.addWidget(self._temperature_edit)
        temp_layout.addStretch()

        # Show or hide temperature edit based on checkbox state
        temp_checkbox.toggled.connect(self._temperature_edit.setVisible)
        temp_checkbox.toggled.connect(self._temperature_edit.setEnabled)
        temp_checkbox.toggled.connect(
            lambda checked: self._temperature_edit.setText(
                str(DEFAULT_TIME_SERIES_TEMP)
            )
            if checked
            else self._temperature_edit.setText("")
        )

        return temp_layout

    def _build_action_buttons(self) -> QWidget:
        """Build the action buttons section.

        Also include a line for the output directory path.
        """
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        # Create Import/Export
        self._import_csv_btn = QPushButton("Import CSV")
        self._export_csv_btn = QPushButton("Export CSV")
        # Create Ouput Directory path display, report generation button and reset button
        output_dir = self._model.get_output_directory() if self._model else ""
        self._output_dir_label = QLabel("Current Output Directory: ")
        self._output_dir_line_edit = QLineEdit(str(output_dir))
        self._output_dir_line_edit.setReadOnly(True)
        self._output_dir_line_edit.setMinimumWidth(len(str(output_dir)) * 6)
        # Create Folder Selection Button and Report Generation Button
        self._select_output_folder_btn = QPushButton("Select Output Folder...")
        self._generate_report_btn = QPushButton("Generate Report")
        # Reset Button
        self._reset_btn = QPushButton("Reset All")

        # Add output directory widgets to horizontal layout
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(self._output_dir_label)
        directory_layout.addWidget(self._output_dir_line_edit)

        # Add to Layout
        layout.addWidget(self._import_csv_btn, 1, 0, 1, 1)
        layout.addWidget(self._export_csv_btn, 1, 1, 1, 1)
        layout.setColumnStretch(2, 1)  # Column idx 2 stretches to fill space
        layout.addLayout(directory_layout, 0, 3, 1, 3)
        layout.addWidget(self._select_output_folder_btn, 1, 3, 1, 1)
        layout.addWidget(self._generate_report_btn, 1, 4, 1, 1)
        layout.addWidget(self._reset_btn, 1, 5, 1, 1)

        return widget

    def _build_console_section(self) -> QWidget:
        """Build the console section."""
        self._console_group_box = QGroupBox("Console Output")
        self._console_group_box.setCheckable(True)
        self._console_group_box.setChecked(False)  # Start collapsed

        layout = QVBoxLayout()
        self._console_group_box.setLayout(layout)

        # Create Widget
        self._console_output = QTextBrowser()
        self._console_output.setReadOnly(True)
        self._console_output.setMinimumHeight(150)

        layout.addWidget(self._console_output)

        # Connect toggle to hide/show content
        self._console_group_box.toggled.connect(self._on_console_toggled)

        # Start with content hidden
        self._console_output.setVisible(False)

        return self._console_group_box

    def _on_console_toggled(self, checked: bool) -> None:  # noqa: FBT001
        """Show/hide console output when checkbox is toggled."""
        self._console_output.setVisible(checked)

    def _update_test_table(self, test_rows: list[TestResultRow]) -> None:
        """Update the test table from state data.

        Args:
            test_rows: List of TestResultRow objects to display

        """
        for row_idx, row_data in enumerate(test_rows):
            # Column 0 (Description) is read-only, set once in __init__

            # Column 1: Pass/Fail dropdown
            combo = self._test_table.cellWidget(row_idx, 1)
            if combo:
                combo = cast("QComboBox", combo)
                with QSignalBlocker(combo):
                    combo.setCurrentText(row_data.pass_fail)

            # Column 2 & 3 (Spec Min/Max) are static, set once in __init__

            # Column 4: Data Measured
            self._set_table_cell_float(row_idx, 4, row_data.measured)

    def _update_time_series_table(
        self, table_rows: list[tuple[int, float | None]]
    ) -> None:
        """Update the time series table from the state data.

        Args:
            table_rows: List of (minute, oxygen_level) tuples to display

        """
        for col_idx, (_minute, oxygen_level) in enumerate(table_rows):
            # Row 0 (minute labels) is read-only; set once in __init__

            # Row 1: Dissolved O2 measured data (horizontal layout)
            oxy_item = self._time_series_widget.item(1, col_idx)
            if oxy_item is None:
                oxy_item = QTableWidgetItem()
                oxy_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._time_series_widget.setItem(1, col_idx, oxy_item)

            if oxygen_level is not None:
                oxy_item.setText(f"{oxygen_level:.2f}")
            else:
                oxy_item.setText("")

    def _set_table_cell_float(self, row: int, col: int, value: float | None) -> None:
        """Set table cell to a float value with row-specific precision.

        Args:
            row: Row index
            col: Column index
            value: Float value to display, or None for empty cell

        """
        item = self._test_table.item(row, col)
        if item is None:
            item = QTableWidgetItem()
            self._test_table.setItem(row, col, item)

        if value is not None:
            # Get decimal precision for this row type
            spec_key = ROW_SPEC_MAPPING[row]
            precision = DS50_DECIMAL_PRECISION.get(spec_key, 2) if spec_key else 2

            # Format with appropriate precision
            numeric_text = f"{value:.{precision}f}"
            item.setText(numeric_text)
            item.setData(Qt.ItemDataRole.EditRole, numeric_text)
        else:
            item.setText("")
            item.setData(Qt.ItemDataRole.EditRole, "")

    def _block_signals(self, *, block: bool) -> None:
        """Block or unblock signals from all input widgets.

        Used during programmatic updates to prevent triggering change handlers
        that would send updates back to the presenter (feedback loop).

        Args:
            block: True to block signals, False to unblock

        """
        # Metadata fields
        self._name_edit.blockSignals(block)
        self._location_edit.blockSignals(block)
        self._date_edit.blockSignals(block)
        self._serial_edit.blockSignals(block)

        # Test Table Fields
        self._test_table.blockSignals(block)
        for row in range(NUM_TEST_ROWS):
            if row == HEADER_ROW_INDEX:
                continue
            combo = self._test_table.cellWidget(row, 1)
            if combo:
                combo.blockSignals(block)

        # Time Series Fields
        self._time_series_widget.blockSignals(block)
        self._temperature_edit.blockSignals(block)

        # Action Buttons
        self._import_csv_btn.blockSignals(block)
        self._export_csv_btn.blockSignals(block)
        self._generate_report_btn.blockSignals(block)

    def _autosize_table(self, table: QTableWidget) -> int:
        """Auto-size the test table to fit its contents without scrollbars.

        Uses verticalHeader().length() to get the sum of all row heights,
        rather than manually iterating through rows.
        """
        h_header = table.horizontalHeader()
        v_header = table.verticalHeader()

        frame_width = table.frameWidth()

        # Calculate total height: header + all rows + frame borders + padding
        h_header_height = 0 if not h_header.isVisible() else h_header.height()

        return (
            h_header_height  # Horizontal header (column names)
            + v_header.length()  # Sum of all row heights
            + (frame_width * 2)  # Top and bottom frame borders
            + table.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
        )

    def log_message(self, message: str) -> None:
        """Log a message to the console output."""
        self._console_output.append(message)


class _MeasuredValueDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate):
    """Delegate that appends units for measured values in the test table."""

    def __init__(
        self,
        units_by_row: dict[int, str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._units_by_row = units_by_row

    def initStyleOption(
        self,
        option: "QStyleOptionViewItem",
        index: "QModelIndex | QPersistentModelIndex",
    ) -> None:
        super().initStyleOption(option, index)

        if index.column() != MEASURED_COL_INDEX:
            return

        unit = self._units_by_row.get(index.row())
        if not unit:
            return

        text = option.text
        if text and not text.endswith(unit):
            option.text = f"{text} {unit}"


def _main() -> None:
    """Call Main function."""
    app = QApplication(sys.argv)
    window = DegasserTab()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
