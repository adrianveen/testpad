from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import date

import PySide6.QtCore
import PySide6.QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHeaderView,
    QPushButton,
    QTextBrowser,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QDateEdit,
    QTableWidget,
    QLabel,
    QTableWidgetItem
)

from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.degasser_tab.model import DegasserModel
from testpad.ui.tabs.degasser_tab.presenter import DegasserPresenter
from testpad.ui.tabs.degasser_tab.view_state import DegasserViewState
from testpad.ui.widgets.chart_widgets import TimeSeriesChartWidget
from testpad.ui.tabs.degasser_tab.config import (
    DEFAULT_TEST_DESCRIPTIONS,
    DS50_SPEC_RANGES,
    DS50_SPEC_UNITS,
    NO_LIMIT_SYMBOL,
    ROW_SPEC_MAPPING,
    NUM_TEST_ROWS,
    NUM_TEST_COLS,
    HEADER_ROW_INDEX
)


class DegasserTab(BaseTab):
    """Degasser tab view."""
    def __init__(
            self,
            parent=None,
            model: Optional["DegasserModel"] = None,
            presenter: Optional["DegasserPresenter"] = None
    ) -> None:
        super().__init__(parent)

        self._model = model
        self._presenter = presenter
        self._time_series_chart = TimeSeriesChartWidget()

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

    def render(self, state: DegasserViewState) -> None:
        """Render the view based on the provided state.

        This is the primary interface between Presenter and View. The Presenter
        creates a ViewState from the Model and passes it here. This method
        updates all UI widgets to reflect the state.

        Args:
            state: Complete UI state to render

        Note: This method handles signal blocking internally to prevent
            feedback loops during updates.
        """
        self._block_signals(True)
        try:
            # Update Metadata
            self._name_edit.setText(state.tester_name)
            self._location_edit.setText(state.location)
            self._serial_edit.setText(state.ds50_serial)

            if state.test_date:
                qdate = PySide6.QtCore.QDate(state.test_date)
                self._date_edit.setDate(qdate)

            # Render Chart
            self._time_series_chart.update_plot(
                state.time_series_measurements,
                state.temperature_c
            )

            # Render temperature display
            # Only update if field is not in focus - user may be editing
            if not self._temperature_edit.hasFocus():
                if state.temperature_c is not None:
                    self._temperature_edit.setText(f"{state.temperature_c:.1f}")
                else:
                    self._temperature_edit.setText("")

            self._render_test_table(state.test_rows)

            self._render_time_series_table(state.time_series_table_rows)

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
                combo.currentTextChanged.connect(
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
        return item.text().strip() if item else ""

    def get_time_series_cell_value(self, row: int, column: int) -> str:
        """Get the text value from a time series table cell.

        Args:
          row: Row index
          column: Column index

        Returns:
          Cell text value, or empty string if cell doesn't exist
        """
        item = self._time_series_widget.item(row, column)
        return item.text().strip() if item else "" 

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
        self._serial_edit = QLineEdit()

        # Layout
        layout.addWidget(QLabel("Tester: "), 0, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._name_edit, 0, 1)
        layout.addWidget(QLabel("Date: "), 0, 2, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._date_edit, 0, 3)
        layout.addWidget(QLabel("DS-50 Serial #: "), 1, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._serial_edit, 1, 1)
        layout.addWidget(QLabel("Location: "), 1, 2, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._location_edit, 1, 3)

        return widget

    def _build_test_table(self) -> QWidget:
        """Build the test table section."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._test_table = QTableWidget(7, 5)
        self._test_table.setHorizontalHeaderLabels(
            ["Test Procedure/Description", "Pass/Fail", "Spec_Min", "Spec_Max", "Data Measured"]
        )
        self._test_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Disable vertical scrollbar

        # Pre-fill descriptions (these are read-only)
        for row, desc in enumerate(DEFAULT_TEST_DESCRIPTIONS):
            # Column 0: Description only
            item = QTableWidgetItem(desc)
            item.setFlags(item.flags() & ~PySide6.QtCore.Qt.ItemIsEditable) # Make read-only
            # Bold and gray background for re-circulation header rows
            if row == 3:
                font = item.font()
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)
                item.setFont(font)
                item.setBackground(PySide6.QtGui.QColor(60, 60, 60)) # Light gray background
                # Span all columns for 2nd re-circulation header
                self._test_table.setSpan(3, 0, 1, 5)
            self._test_table.setItem(row, 0, item)

            # Get spec key for this row (None for header row)
            spec_key = ROW_SPEC_MAPPING[row]

            # Only add spec cells for non-header rows
            if spec_key is not None:
                spec = DS50_SPEC_RANGES.get(spec_key, (None, None))
                unit = DS50_SPEC_UNITS.get(spec_key, "")

                for col in range(2, 5):
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
                        spec_item.setFlags(spec_item.flags() & ~Qt.ItemIsEditable)
                    self._test_table.setItem(row, col, spec_item)

            if row != 3:
                # Column 1: Pass/Fail dropdown for non header rows
                pass_fail_combo = QComboBox()
                pass_fail_combo.addItems(["", "Pass", "Fail"])
                self._test_table.setCellWidget(row, 1, pass_fail_combo)

        height = self._test_table.horizontalHeader().height()
        for row in range(7):
            height += self._test_table.rowHeight(row)

        height += self._test_table.frameWidth() * 2  # Add frame width
        height += 2  # Add a little extra padding

        self._test_table.setFixedHeight(height)

        header = self._test_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

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
        self._time_series_widget = QTableWidget(11, 2)
        self._time_series_widget.setHorizontalHeaderLabels(
            ["Time (minutes)", "Dissolved O2 (mg/L)"]
        )
        self._time_series_widget.verticalHeader().setVisible(True)  # Push to left

        for row in range(11):
            minute_item = QTableWidgetItem(str(row))
            minute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            minute_item.setFlags(minute_item.flags() & ~Qt.ItemIsEditable) # Make read-only
            self._time_series_widget.setItem(row, 0, minute_item)

            # Oxygen column - pre-create empty editable cells for alignment purposes
            oxygen_item = QTableWidgetItem()
            oxygen_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._time_series_widget.setItem(row, 1, oxygen_item)

        table_layout.addWidget(self._time_series_widget)

        header = self._time_series_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        vertical_header = self._time_series_widget.verticalHeader()
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
            lambda checked: self._temperature_edit.setText("25.0") if checked else self._temperature_edit.setText("")
        )

        # Add to main layout
        h_layout.addWidget(table_container, 1)
        h_layout.addWidget(self._time_series_chart, 1)

        main_layout.addLayout(h_layout)

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

        layout.addWidget(self._console_output)

        # Connect toggle to hide/show content
        self._console_group_box.toggled.connect(self._on_console_toggled)

        # Start with content hidden
        self._console_output.setVisible(False)

        return self._console_group_box

    def _on_console_toggled(self, checked: bool) -> None:
        """Show/hide console output when checkbox is toggled."""
        self._console_output.setVisible(checked)

    def log_message(self, message: str) -> None:
        """Log a message to the console output."""
        self._console_output.append(message)


    def _render_test_table(self, test_rows: list) -> None:
        """Render the test table from state data.

        Args:
            test_rows: List of TestResultRow objects to display
        """
        for row_idx, row_data in enumerate(test_rows):
            # Column 0 (Description) is read-only, set once in __init__

            # Column 1: Pass/Fail dropdown
            combo = self._test_table.cellWidget(row_idx, 1)
            if combo:
                combo.setCurrentText(row_data.pass_fail)

            # Column 2 & 3 (Spec Min/Max) are static, set once in __init__

            # Column 4: Data Measured
            self._set_table_cell_float(row_idx, 4, row_data.measured)

    def _render_time_series_table(
        self,
        table_rows: list[tuple[int, Optional[float]]]
    ) -> None:
        """Render the time series table from the state data.

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
    def _set_table_cell_float(
        self,
        row: int,
        col: int,
        value: Optional[float]
    ) -> None:
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
            item.setText(f"{value:.2f}")
        else:
            item.setText("")

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

        # Time Series Fields
        self._time_series_widget.blockSignals(block)
        self._temperature_edit.blockSignals(block)

        # Action Buttons
        self._import_csv_btn.blockSignals(block)
        self._export_csv_btn.blockSignals(block)
        self._generate_report_btn.blockSignals(block)
