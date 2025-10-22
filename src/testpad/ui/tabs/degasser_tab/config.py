"""
Configuration specific to the Degasser (Dissolved O2) tab.

Contains DS-50 specifications, test descriptions, and validation rules.
"""

# === Time Series Configuration ===
from PySide6.QtGui import QColor
from testpad.config.defaults import (
        DEFAULT_TEMPERATURE_C    
)

MIN_MINUTE = 0
MAX_MINUTE = 10
TIME_SERIES_RESOLUTION_MINUTES = 1  # Measurement interval
DEFAULT_TIME_SERIES_TEMP = DEFAULT_TEMPERATURE_C
# === Metadata Fields ===
METADATA_FIELDS = {
    "tester_name": "Tester Name",
    "test_date": "Test Date",
    "ds50_serial_number": "DS-50 Serial Number",
    "location": "Location",
}

# === DS-50 Test Specifications ===
# These are the standard test descriptions for DS-50 degasser testing
DEFAULT_TEST_DESCRIPTIONS = [
    "Vacuum Pressure:",
    "Flow Rate:",
    "Dissolved Oxygen level test:",
    "Dissolved Oxygen re-circulation test (1000 mL):",
    "   Starting DO Level:",
    "   Time to read 4 mg/L (min):",
    "   Time to reach 2 mg/L (min):",
]

# === DS-50 Specification Ranges ===
# Default specification ranges for each test
# Format: (min, max) where None means no limit
DS50_SPEC_RANGES = {
    "vacuum_pressure": (-22, None),
    "flow_rate": (300, 700),
    "do_level": (None, 3.0),
    "recirculation_start": (7.0, None),
    "recirculation_to_4mg": (None, 5),
    "recirculation_to_2mg": (None, 10),
}

# Units for each specification (displayed in table)
DS50_SPEC_UNITS = {
    "vacuum_pressure": "inHg",
    "flow_rate": "mL/min",
    "do_level": "mg/L",
    "recirculation_start": "mg/L",
    "recirculation_to_4mg": "min",
    "recirculation_to_2mg": "min",
}

# Symbol to display when no limit exists
NO_LIMIT_SYMBOL = "--"

# Row index to spec key mapping
# Maintains the order that specs appear in the test table
# Row 3 is None because it's the header row
ROW_SPEC_MAPPING = [
    "vacuum_pressure",      # Row 0
    "flow_rate",           # Row 1
    "do_level",            # Row 2
    None,                  # Row 3 - Header row
    "recirculation_start", # Row 4
    "recirculation_to_4mg",# Row 5
    "recirculation_to_2mg",# Row 6
]

# === CSV Import Configuration ===
# Recognized column headers for CSV import
CSV_TIME_ALIASES = {"time", "Time", "minute", "minutes", "t_min"}
CSV_OXYGEN_ALIASES = {"oxygen", "oxygen_mg_per_L", "o2", "O2", "do2", "DO2"}
CSV_TEMPERATURE_ALIASES = {"temperature_c", "temp_c", "Temperature", "temp"}

# === Validation Rules ===
MIN_OXYGEN_VALUE = 0.0  # mg/L, must be positive
REQUIRE_TEMPERATURE_FOR_REPORT = False  # Temperature is optional

# === Tables and Report Configuration ===
NUM_TEST_ROWS = 7
NUM_TEST_COLS = 5
NUM_TIME_SERIES_ROWS = 11
NUM_TIME_SERIES_COLS = 2
HEADER_ROW_INDEX = 3
HEADER_ROW_COLOR = QColor(60, 60, 60)
REPORT_VERSION = "2025.0.4"
TEST_TABLE_HEADERS = [
    "Test Procedure/Description",
    "Pass/Fail",
    "Minimum Spec",
    "Maximum Spec",
    "Data Measured"
]

