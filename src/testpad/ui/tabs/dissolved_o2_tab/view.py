import PySide6.QtCore
import PySide6.QtWidgets

from testpad.ui.tabs.base_tab import BaseTab
from testpad.ui.tabs.dissolved_o2_tab.model import DEFAULT_TEST_DESCRIPTIONS, DissolvedO2Model
from testpad.ui.tabs.dissolved_o2_tab.presenter import DissolvedO2Presenter

class DissolvedO2Tab(BaseTab):
    """Dissolved O2 tab."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._model = DissolvedO2Model()
        self._presenter = DissolvedO2Presenter(self._model, self)

        layout = PySide6.QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._build_metadata_section())
        layout.addWidget(self._build_test_table())
        layout.addWidget(self._build_time_series_section())
        layout.addWidget(self._build_chart_section())
        layout.addWidget(self._build_action_buttons())
        layout.addWidget(self._build_console_section())

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
        self._test_table = PySide6.QtWidgets.QTableWidget(4, 5)
        self._test_table.setHorizontalHeaderLabels(
            ["Test Procedure/Description", "Pass/Fail", "Spec_Min", "Spec_Max", "Data Measured"]
        )
        
        # Pre-fill descriptions (these are read-only)
        for row, desc in enumerate(DEFAULT_TEST_DESCRIPTIONS):
            item = PySide6.QtWidgets.QTableWidgetItem(desc)
            item.setFlags(item.flags() & ~PySide6.QtCore.Qt.ItemIsEditable) # Make read-only
            self._test_table.setItem(row, 0, item)
        
        layout.addWidget(self._test_table)

        return widget
    
    def _build_time_series_section(self) -> PySide6.QtWidgets.QWidget:
        """Build the time series data entry section."""
        widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QVBoxLayout()
        widget.setLayout(layout)


        # Create Widgets
        self._time_series_widget = PySide6.QtWidgets.QTableWidget(11, 2)
        self._time_series_widget.setHorizontalHeaderLabels(
            ["Time (minutes)", "Dissolved O2 (mg/L)"]
        )
        self._time_series_widget.verticalHeader().setVisible(True)  # Push to left

        for row in range(11):
            minute_item = PySide6.QtWidgets.QTableWidgetItem(str(row))
            minute_item.setFlags(minute_item.flags() & ~PySide6.QtCore.Qt.ItemIsEditable) # Make read-only
            self._time_series_widget.setItem(row, 0, minute_item)

        layout.addWidget(self._time_series_widget)

        # Temperature widget
        temp_layout = PySide6.QtWidgets.QHBoxLayout()
        temp_label = PySide6.QtWidgets.QLabel("Temperature (°C): ")
        self._temperature_edit = PySide6.QtWidgets.QLineEdit()
        self._temperature_edit.setPlaceholderText("Optional")
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self._temperature_edit)
        temp_layout.addStretch()
        layout.addLayout(temp_layout)

        return widget

    def _build_chart_section(self) -> PySide6.QtWidgets.QWidget:
        """Build the chart section."""
        widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        # Create Widget
        self._chart_widget = PySide6.QtWidgets.QWidget()
        self._chart_widget.setLayout(PySide6.QtWidgets.QVBoxLayout())

        layout.addWidget(self._chart_widget)

        return widget
    
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
        group_box = PySide6.QtWidgets.QGroupBox("Console Output")
        group_box.setCheckable(True)
        group_box.setChecked(False) # Start Collapsed
        
        layout = PySide6.QtWidgets.QVBoxLayout()
        group_box.setLayout(layout)

        # Create Widget
        self._console_output = PySide6.QtWidgets.QTextBrowser()
        self._console_output.setReadOnly(True)
        self._console_output.setMaximumHeight(150)

        layout.addWidget(self._console_output)

        return group_box