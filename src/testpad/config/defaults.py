"""
Default application settings for FUS Instruments TestPad.

These are user-facing defaults that can be overridden by user preferences
or loaded from configuration files.
"""

from .constants import (
    ABSOLUTE_ZERO_C,
    MAX_REASONABLE_TEMP_C,
    STANDARD_ROOM_TEMP_C,
)

# === Temperature Defaults ===
DEFAULT_TEMPERATURE_C = STANDARD_ROOM_TEMP_C
DEFAULT_RANGE = (ABSOLUTE_ZERO_C, MAX_REASONABLE_TEMP_C)

# === UI Defaults ===
DEFAULT_DECIMAL_PLACES = 2
DEFAULT_TABLE_ROW_HEIGHT = 7

# === File Defaults ===
DEFAULT_EXPORT_DIR = '%USERPROFILE%\\Documents\\FUS Instruments\\Testpad Exports'
DEFAULT_CSV_ENCODING = 'utf-8'
DEFAULT_CSV_DELIMITER = ','