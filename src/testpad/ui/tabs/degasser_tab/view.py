from typing import Optional
import PySide6.QtCore
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
import PySide6.QtGui

from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.degasser_tab.model import DEFAULT_TEST_DESCRIPTIONS, DegasserModel
from testpad.ui.tabs.degasser_tab.presenter import DegasserPresenter
from testpad.ui.widgets.chart_widgets import TimeSeriesChartWidget

class DegasserTab(BaseTab):
    """Degasser tab view."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._model = DegasserModel()
        self._presenter = DegasserPresenter(self._model, self)
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

        self._presenter.initialize()

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
        self._date_edit.setDate(PySide6.QtCore.QDate.currentDate())
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

    def update_chart_widget(self, data: list[tuple[int, float]], temp: Optional[float] = None) -> None:
        """Update the chart widget in the time series section."""
        self._time_series_chart.update_plot(data, temp)

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
        #self._console_output.setMaximumHeight(150)

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