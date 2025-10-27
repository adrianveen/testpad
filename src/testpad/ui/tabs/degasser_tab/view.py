from typing import Optional, cast

import PySide6.QtCore
from PySide6.QtCore import QDate, QSignalBlocker, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from testpad.config.defaults import ISO_8601_DATE_FORMAT
from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.degasser_tab.chart_widgets import TimeSeriesChartWidget
from testpad.ui.tabs.degasser_tab.config import (
    DEFAULT_TEST_DESCRIPTIONS,
    DEFAULT_TIME_SERIES_TEMP,
    DS50_SPEC_RANGES,
    DS50_SPEC_UNITS,
    HEADER_ROW_COLOR,
    HEADER_ROW_INDEX,
    METADATA_FIELDS,
    NO_LIMIT_SYMBOL,
    NUM_TEST_COLS,
    NUM_TEST_ROWS,
    NUM_TIME_SERIES_COLS,
    NUM_TIME_SERIES_ROWS,
    ROW_SPEC_MAPPING,
    TEST_TABLE_HEADERS,
)
from testpad.ui.tabs.degasser_tab.model import DegasserModel
from testpad.ui.tabs.degasser_tab.presenter import DegasserPresenter
from testpad.ui.tabs.degasser_tab.view_state import DegasserViewState
from testpad.utils.lineedit_validators import FixupDoubleValidator, ValidatedLineEdit


class ColumnMajorTableWidget(QTableWidget):
    """QTableWidget with column-major tab navigation (top→bottom, left→right).

    Overrides default Qt behavior where Tab moves left→right across columns.
    Instead, Tab moves top→bottom within a column, then wraps to the next column.
    """

    def _get_next_cell(
        self, row: int, col: int, forward: bool = True
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
            elif col < cols - 1:
                # At bottom of column, jump to top of next column
                return 0, col + 1
            else:
                # At bottom-right corner, wrap around to top-left
                return 0, 0
        else:
            # Backward navigation: up column, then left to previous column
            if row > 0:
                # Not at top of column yet, move up one row
                return row - 1, col
            elif col > 0:
                # At top of column, jump to bottom of previous column
                return rows - 1, col - 1
            else:
                # At top-left corner, wrap around to bottom-right
                return rows - 1, cols - 1

    def keyPressEvent(self, event):
        """Override Qt's default key handling to implement column-major navigation.

        By default, QTableWidget uses row-major Tab navigation (left→right).
        This override intercepts Tab/Enter/Backtab keys and implements column-major
        navigation instead. Other keys are passed to Qt's default handler.
        """
        key = event.key()

        if key in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
            # Tab and Enter both move forward in column-major order
            event.accept()  # Prevent Qt's default row-major navigation
            new_row, new_col = self._get_next_cell(
                self.currentRow(), self.currentColumn(), forward=True
            )
            self.setCurrentCell(new_row, new_col)
        elif key == Qt.Key_Backtab:
            # Shift+Tab moves backward in column-major order
            event.accept()  # Prevent Qt's default behavior
            new_row, new_col = self._get_next_cell(
                self.currentRow(), self.currentColumn(), forward=False
            )
            self.setCurrentCell(new_row, new_col)
        else:
            # For all other keys (arrows, letters, etc.), use Qt's default handling
            super().keyPressEvent(event)


class ColumnMajorNavigationMixin:
    """Mixin for item delegates to support column-major navigation during cell editing.

    This mixin installs an event filter on editor widgets to intercept Tab/Enter
    keys and forward them to the table's navigation logic. Any delegate class that inherits
    from this mixin will automatically support column-major navigation during editing.

    Usage: class MyDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate): ...
    Note: Mixin must come BEFORE QStyledItemDelegate in the inheritance list for proper MRO.
    """

    def eventFilter(self, editor, event):
        """Intercept key events from editor widgets and redirect navigation keys.

        When we detect Tab/Enter, we bypass the editor and send the event directly
        to the table's keyPressEvent for custom handling.

        Args:
            editor: The editor widget (e.g., QLineEdit) that received the event
            event: The QEvent being processed

        Returns:
            True if event was handled (prevents further processing)
            False to allow normal event propagation
        """
        if event.type() == PySide6.QtCore.QEvent.Type.KeyPress:
            if event.key() in (
                Qt.Key_Tab,
                Qt.Key_Backtab,
                Qt.Key_Return,
                Qt.Key_Enter,
            ):
                # This is a navigation key - don't let the editor process it
                table = self.parent()  # Delegate's parent is the table widget
                if isinstance(table, ColumnMajorTableWidget):
                    # Forward the event to the table's custom navigation handler
                    table.keyPressEvent(event)
                    return True  # Event handled, stop propagation
        # Not a navigation key, or not our custom table - use default behavior
        return super().eventFilter(editor, event)

    def createEditor(self, parent, option, index):
        """Create editor widget and install this delegate as an event filter.
        Qt calls this method when a cell begins editing.

        Args:
            parent: Parent widget for the editor (the table viewport)
            option: Style options for the editor
            index: Model index of the cell being edited

        Returns:
            The editor widget with event filter installed
        """
        editor = super().createEditor(parent, option, index)
        if editor:
            # Install this delegate as an event filter on the editor
            # Now our eventFilter() method will intercept the editor's key events
            editor.installEventFilter(self)
        return editor


class DegasserTab(BaseTab):
    """Degasser tab view."""

    def __init__(
        self,
        parent=None,
        model: Optional["DegasserModel"] = None,
        presenter: Optional["DegasserPresenter"] = None,
    ) -> None:
        super().__init__(parent)

        self._model = model
        self._presenter = presenter
        self._time_series_chart = TimeSeriesChartWidget()
        self._time_series_section: Optional[QWidget] = None

        layout = QGridLayout(self)
        layout.addWidget(self._build_metadata_section(), 0, 0, 1, 2)
        layout.addWidget(self._build_test_table(), 1, 0, 1, 2)
        layout.addWidget(self._build_time_series_section(), 2, 0, 1, 1)
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
        self._block_signals(True)
        try:
            # Update Metadata
            self._name_edit.setText(state.tester_name)
            self._location_edit.setText(state.location)
            self._serial_edit.setText(state.ds50_serial)
            if state.test_date is not None:
                # Convert Python date to QDate for type safety
                qdate = QDate(
                    state.test_date.year, state.test_date.month, state.test_date.day
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

        finally:
            self._block_signals(False)

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
        self._generate_report_btn.clicked.connect(presenter.on_generate_report)
        self._reset_btn.clicked.connect(presenter.on_reset)

        # Pass/Fail Combo Boxes
        for row in range(NUM_TEST_ROWS):
            if row == HEADER_ROW_INDEX:
                continue
            combo = self._test_table.cellWidget(row, 1)
            if combo:
                combo = cast(QComboBox, combo)
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

        if column == 4:
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
                spec = DS50_SPEC_RANGES.get(spec_key, (None, None))
                unit = DS50_SPEC_UNITS.get(spec_key, "")

                if unit:
                    units_by_row[row] = unit

                for col in range(2, NUM_TEST_COLS):
                    if col == 2:  # Spec_Min
                        if spec[0] is None:
                            spec_value = NO_LIMIT_SYMBOL
                        else:
                            spec_value = f"{spec[0]} {unit}" if unit else str(spec[0])
                    elif col == 3:  # Spec_Max
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
                            spec_item.flags()
                            & ~PySide6.QtCore.Qt.ItemFlag.ItemIsEditable
                        )
                    self._test_table.setItem(row, col, spec_item)

            if row != HEADER_ROW_INDEX:
                # Column 1: Pass/Fail dropdown for non header rows
                pass_fail_combo = QComboBox()
                pass_fail_combo.addItems(["", "Pass", "Fail"])
                self._test_table.setCellWidget(row, 1, pass_fail_combo)

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

    def _build_time_series_section(self) -> QWidget:
        """Build the time series data entry section."""
        widget = QWidget()
        main_layout = QVBoxLayout()
        widget.setLayout(main_layout)

        # Horizontal layout for chart and table
        h_layout = QHBoxLayout()

        # Left: Time Series Table
        table_container = QWidget()
        table_layout = QVBoxLayout()
        table_container.setLayout(table_layout)

        # Create Widgets
        self._time_series_widget = ColumnMajorTableWidget(
            NUM_TIME_SERIES_ROWS, NUM_TIME_SERIES_COLS
        )
        self._time_series_widget.setItemDelegateForColumn(
            1, ValidatedFloatDelegate(self._time_series_widget)
        )
        self._time_series_widget.setHorizontalHeaderLabels(
            ["Time (minutes)", "Dissolved O2 (mg/L)"]
        )
        self._time_series_widget.verticalHeader().setVisible(True)  # Push to left

        for row in range(NUM_TIME_SERIES_ROWS):
            minute_item = QTableWidgetItem(str(row))
            minute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            minute_item.setFlags(
                minute_item.flags() & ~PySide6.QtCore.Qt.ItemFlag.ItemIsEditable
            )  # Make read-only
            self._time_series_widget.setItem(row, 0, minute_item)

            # Oxygen column - pre-create empty editable cells for alignment purposes
            oxygen_item = QTableWidgetItem()
            oxygen_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._time_series_widget.setItem(row, 1, oxygen_item)

        table_layout.addWidget(self._time_series_widget)

        header = self._time_series_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Configure vertical header with fixed row heights for minimum size calculation
        vertical_header = self._time_series_widget.verticalHeader()
        vertical_header.setDefaultSectionSize(30)  # Set desired row height
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Calculate minimum height with fixed row sizes
        minimum_height = self._autosize_table(self._time_series_widget)
        self._time_series_widget.setMinimumHeight(minimum_height)

        # Now switch to Stretch mode for runtime behavior
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Temperature widget
        temp_layout = QHBoxLayout()
        temp_checkbox = QCheckBox("Temperature Measured (°C):")
        temp_checkbox.setChecked(False)
        self._temperature_edit = QLineEdit()
        self._temperature_edit.hide()  # Start hidden
        self._temperature_edit.setEnabled(False)
        self._temperature_edit.setText("")  # Start empty
        self._temperature_edit.setPlaceholderText("Optional")
        self._temperature_edit.setMaximumWidth(75)
        temp_layout.addWidget(temp_checkbox)
        temp_layout.addWidget(self._temperature_edit)
        temp_layout.addStretch()
        table_layout.addLayout(temp_layout)

        temp_checkbox.toggled.connect(self._temperature_edit.setVisible)
        temp_checkbox.toggled.connect(self._temperature_edit.setEnabled)
        temp_checkbox.toggled.connect(
            lambda checked: self._temperature_edit.setText(
                str(DEFAULT_TIME_SERIES_TEMP)
            )
            if checked
            else self._temperature_edit.setText("")
        )

        # Add to main layout
        h_layout.addWidget(table_container, 1)
        h_layout.addWidget(self._time_series_chart, 1)

        main_layout.addLayout(h_layout)

        self._time_series_section = widget
        return widget

    def _build_action_buttons(self) -> QWidget:
        """Build the action buttons section."""
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._import_csv_btn = QPushButton("Import CSV")
        self._export_csv_btn = QPushButton("Export CSV")
        self._generate_report_btn = QPushButton("Generate Report")

        # Reset Button
        self._reset_btn = QPushButton("Reset All")
        # Add to Layout
        layout.addWidget(self._import_csv_btn)
        layout.addWidget(self._export_csv_btn)
        layout.addStretch()  # Spacer
        layout.addWidget(self._generate_report_btn)
        layout.addWidget(self._reset_btn)

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

    def _on_console_toggled(self, checked: bool) -> None:
        """Show/hide console output when checkbox is toggled."""
        self._console_output.setVisible(checked)
        # Controls window resize on hide
        main_win = self.window()
        if main_win and not main_win.isMaximized() and not main_win.isFullScreen():
            QTimer.singleShot(0, lambda: main_win.resize(main_win.sizeHint()))

    def _update_test_table(self, test_rows: list) -> None:
        """Update the test table from state data.

        Args:
            test_rows: List of TestResultRow objects to display
        """
        for row_idx, row_data in enumerate(test_rows):
            # Column 0 (Description) is read-only, set once in __init__

            # Column 1: Pass/Fail dropdown
            combo = self._test_table.cellWidget(row_idx, 1)
            if combo:
                combo = cast(QComboBox, combo)
                with QSignalBlocker(combo):
                    combo.setCurrentText(row_data.pass_fail)

            # Column 2 & 3 (Spec Min/Max) are static, set once in __init__

            # Column 4: Data Measured
            self._set_table_cell_float(row_idx, 4, row_data.measured)

    def _update_time_series_table(
        self, table_rows: list[tuple[int, Optional[float]]]
    ) -> None:
        """Update the time series table from the state data.

        Args:
            table_rows: List of (minute, oxygen_level) tuples to display
        """
        for row_idx, (minute, oxygen_level) in enumerate(table_rows):
            # Column 0 (minute) is read-only; set once in __init__

            # Column 1: Dissolved O2 measured data
            oxy_item = self._time_series_widget.item(row_idx, 1)
            if oxy_item is None:
                oxy_item = QTableWidgetItem()
                self._time_series_widget.setItem(row_idx, 1, oxy_item)

            if oxygen_level is not None:
                oxy_item.setText(f"{oxygen_level:.2f}")
            else:
                oxy_item.setText("")

    def _set_table_cell_float(self, row: int, col: int, value: Optional[float]) -> None:
        """Helper to set table cell to a float value.

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
            numeric_text = f"{value:.2f}"
            item.setText(numeric_text)
            item.setData(Qt.ItemDataRole.EditRole, numeric_text)
        else:
            item.setText("")
            item.setData(Qt.ItemDataRole.EditRole, "")

    def _block_signals(self, block: bool) -> None:
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
        total_height = (
            h_header.height()  # Horizontal header (column names)
            + v_header.length()  # Sum of all row heights
            + (frame_width * 2)  # Top and bottom frame borders
            + 1  # Padding
        )

        return total_height

    def log_message(self, message: str) -> None:
        """Log a message to the console output."""
        self._console_output.append(message)


class _MeasuredValueDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate):
    """Delegate that appends units for measured values in the test table."""

    def __init__(
        self, units_by_row: dict[int, str], parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._units_by_row = units_by_row

    def initStyleOption(self, option, index) -> None:
        super().initStyleOption(option, index)

        if index.column() != 4:
            return

        unit = self._units_by_row.get(index.row())
        if not unit:
            return

        text = option.text
        if text and not text.endswith(unit):
            option.text = f"{text} {unit}"


class ValidatedFloatDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate):
    """Delegate enforcing numeric-only, visually validated input in table cells."""

    def createEditor(self, parent, option, index):
        editor = ValidatedLineEdit(parent)
        validator = FixupDoubleValidator(
            0.0, 100.0, 3, editor
        )  # adjust range/precision as needed
        editor.setValidator(validator)
        editor.setPlaceholderText("Enter number")
        # Install event filter via mixin
        editor.installEventFilter(self)
        return editor
