"""
Default application settings for FUS Instruments TestPad.

These are user-facing defaults that can be overridden by user preferences
or loaded from configuration files.
"""
from datetime import date
from pathlib import Path

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
PACKAGE_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT_DIR = Path.home() / 'Documents' / 'FUS Instruments' / 'Testpad'
DEFAULT_EXPORT_DIR = DEFAULT_OUTPUT_DIR / 'Exports'
DEFAULT_FUS_LOGO_PATH = PACKAGE_ROOT / 'resources' / 'FUS_logo_text_icon_ms_v3.svg'
DEFAULT_CSV_ENCODING = 'utf-8'
DEFAULT_CSV_DELIMITER = ','

# === Date Defaults ===
ISO_8601_DATE_FORMAT = "yyyy/MM/dd"
def default_date() -> date:
    """Returns today's date as a date object (no time component)."""
    return date.today()
