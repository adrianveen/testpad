from typing import Optional
import PySide6.QtCore
import PySide6.QtWidgets
import PySide6.QtGui

from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.degasser_tab.model import DEFAULT_TEST_DESCRIPTIONS, DegasserModel
from testpad.ui.tabs.degasser_tab.presenter import DegasserPresenter
from testpad.ui.tabs.degasser_tab.degasser_plot import TimeSeriesChartWidget

class DegasserTab(BaseTab):
    """Degasser tab view."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._model = DegasserModel()
        self._presenter = DegasserPresenter(self._model, self)
        self._chart_widget = TimeSeriesChartWidget()

        layout = PySide6.QtWidgets.QGridLayout(self)
        layout.addWidget(self._build_metadata_section(), 0, 0, 1, 2)
        layout.addWidget(self._build_test_table(), 1, 0, 1, 2)
        layout.addWidget(self._build_time_series_section(), 2, 0, 1, 1)
        #layout.addWidget(self._build_chart_section(), 2, 1, 1, 1)
        layout.addWidget(self._build_action_buttons(), 3, 0, 1, 2)
        layout.addWidget(self._build_console_section(), 4, 0, 1, 2)

        self._presenter.initialize()

    def _build_metadata_section(self) -> PySide6.QtWidgets.QWidget:
        """Build the metadata section."""
        widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QFormLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._name_edit = PySide6.QtWidgets.QLineEdit()
        self._location_edit = PySide6.QtWidgets.QLineEdit()
        self._date_edit = PySide6.QtWidgets.QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(PySide6.QtCore.QDate.currentDate())
        self._serial_edit = PySide6.QtWidgets.QLineEdit()

        # Layout
        layout.addRow("Tester: ", self._name_edit)
        layout.addRow("Date: ", self._date_edit)
        layout.addRow("Location: ", self._location_edit)
        layout.addRow("DS-50 Serial #: ", self._serial_edit)

        return widget

    def _build_test_table(self) -> PySide6.QtWidgets.QWidget:
        """Build the test table section."""
        widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._test_table = PySide6.QtWidgets.QTableWidget(7, 5)
        self._test_table.setHorizontalHeaderLabels(
            ["Test Procedure/Description", "Pass/Fail", "Spec_Min", "Spec_Max", "Data Measured"]
        )
        # get the row height to force calculation
        row_height = self._test_table.rowHeight(0)  # Force row height calculation
        self._test_table.setFixedHeight(row_height * 7.7)  # Set fixed height for all rows

        # Pre-fill descriptions (these are read-only)
        for row, desc in enumerate(DEFAULT_TEST_DESCRIPTIONS):
            # Column 0: Description only
            item = PySide6.QtWidgets.QTableWidgetItem(desc)
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
                pass_fail_combo = PySide6.QtWidgets.QComboBox()
                pass_fail_combo.addItems(["", "Pass", "Fail"])
                self._test_table.setCellWidget(row, 1, pass_fail_combo)

        header = self._test_table.horizontalHeader()
        header.setSectionResizeMode(PySide6.QtWidgets.QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self._test_table)
        return widget
    
    def _build_time_series_section(self) -> PySide6.QtWidgets.QWidget:
        """Build the time series data entry section."""
        widget = PySide6.QtWidgets.QWidget()
        main_layout = PySide6.QtWidgets.QVBoxLayout()
        widget.setLayout(main_layout)

        # Horizontal layout for chart and table
        h_layout = PySide6.QtWidgets.QHBoxLayout()

        # Left: Time Series Table
        table_container = PySide6.QtWidgets.QWidget()
        table_layout = PySide6.QtWidgets.QVBoxLayout()
        table_container.setLayout(table_layout)

        # Create Widgets
        self._time_series_widget = PySide6.QtWidgets.QTableWidget(11, 2)
        self._time_series_widget.setHorizontalHeaderLabels(
            ["Time (minutes)", "Dissolved O2 (mg/L)"]
        )
        self._time_series_widget.verticalHeader().setVisible(True)  # Push to left
        
        for row in range(11):
            minute_item = PySide6.QtWidgets.QTableWidgetItem(str(row))
            minute_item.setTextAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
            minute_item.setFlags(minute_item.flags() & ~PySide6.QtCore.Qt.ItemIsEditable) # Make read-only
            self._time_series_widget.setItem(row, 0, minute_item)

            # Oxygen column - pre-create empty editable cells for alignment purposes
            oxygen_item = PySide6.QtWidgets.QTableWidgetItem()
            oxygen_item.setTextAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
            self._time_series_widget.setItem(row, 1, oxygen_item)

        table_layout.addWidget(self._time_series_widget)

        header = self._time_series_widget.horizontalHeader()
        header.setSectionResizeMode(PySide6.QtWidgets.QHeaderView.ResizeMode.Stretch)

        # Temperature widget
        temp_layout = PySide6.QtWidgets.QHBoxLayout()
        temp_label = PySide6.QtWidgets.QLabel("Temperature °C (Optional): ")
        self._temperature_edit = PySide6.QtWidgets.QDoubleSpinBox()
        self._temperature_edit.setDecimals(1)
        self._temperature_edit.setRange(-273.15, 1000.0)  # Physical range for temperature
        self._temperature_edit.setSuffix(" °C")
        self._temperature_edit.setMaximumWidth(100)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self._temperature_edit)
        temp_layout.addStretch()
        table_layout.addLayout(temp_layout)

        # Right: Placeholder for Chart
        chart_container = PySide6.QtWidgets.QWidget()
        chart_layout = PySide6.QtWidgets.QVBoxLayout()
        chart_container.setLayout(chart_layout)

        self._chart_widget.setLayout(PySide6.QtWidgets.QVBoxLayout())
        chart_layout.addWidget(self._chart_widget)

        # Add to main layout
        h_layout.addWidget(table_container, 1)
        h_layout.addWidget(chart_container, 1)

        main_layout.addLayout(h_layout)

        return widget

    def update_chart_widget(self, data: list[float], temp: Optional[float] = None) -> None:
        """Update the chart widget in the time series section."""
        self._chart_widget.update_plot(data, temp)
    
    def _build_action_buttons(self) -> PySide6.QtWidgets.QWidget:
        """Build the action buttons section."""
        widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QHBoxLayout()
        widget.setLayout(layout)

        # Create Widgets
        self._import_csv_btn = PySide6.QtWidgets.QPushButton("Import CSV")
        self._export_csv_btn = PySide6.QtWidgets.QPushButton("Export CSV")
        self._generate_report_btn = PySide6.QtWidgets.QPushButton("Generate Report")

        # Reset Button
        self._reset_btn = PySide6.QtWidgets.QPushButton("Reset All")
        # Add to Layout
        layout.addWidget(self._import_csv_btn)
        layout.addWidget(self._export_csv_btn)
        layout.addStretch()  # Spacer
        layout.addWidget(self._generate_report_btn)
        layout.addWidget(self._reset_btn)

        return widget
    
    def _build_console_section(self) -> PySide6.QtWidgets.QWidget:
        """Build the console section."""
        self._console_group_box = PySide6.QtWidgets.QGroupBox("Console Output")
        self._console_group_box.setCheckable(True)
        self._console_group_box.setChecked(False)  # Start collapsed

        layout = PySide6.QtWidgets.QVBoxLayout()
        self._console_group_box.setLayout(layout)

        # Create Widget
        self._console_output = PySide6.QtWidgets.QTextBrowser()
        self._console_output.setReadOnly(True)
        self._console_output.setMaximumHeight(150)

        layout.addWidget(self._console_output)

        # Connect toggle to hide/show content
        self._console_group_box.toggled.connect(self._on_console_toggled)

        # Start with content hidden
        self._console_output.setVisible(False)

        return self._console_group_box

    def _on_console_toggled(self, checked: bool) -> None:
        """Show/hide console output when checkbox is toggled."""
        self._console_output.setVisible(checked)