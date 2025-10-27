"""
Centralized configuration for FUS Instruments Testpad.

Import from this module to access application-wide constants and defaults.

Example:
    from testpad.config import ABSOLUTE_ZERO_CELSIUS, DEFAULT_TEMPERATURE_CELSIUS
"""

from testpad.config.constants import (
    ABSOLUTE_ZERO_C,
    MAX_REASONABLE_TEMP_C,
    MIN_OXYGEN_LEVEL_MG_L,
    STANDARD_ROOM_TEMP_C,
    WATER_BOILING_C,
)
from testpad.config.defaults import (
    DEFAULT_CSV_ENCODING,
    DEFAULT_DECIMAL_PLACES,
    DEFAULT_EXPORT_DIR,
    DEFAULT_RANGE,
    DEFAULT_TABLE_ROW_HEIGHT,
    DEFAULT_TEMPERATURE_C,
)

__all__ = [
    # Constants
    "ABSOLUTE_ZERO_C",
    "WATER_BOILING_C",
    "STANDARD_ROOM_TEMP_C",
    "MIN_OXYGEN_LEVEL_MG_L",
    "MAX_REASONABLE_TEMP_C",
    # Defaults
    "DEFAULT_TEMPERATURE_C",
    "DEFAULT_RANGE",
    "DEFAULT_DECIMAL_PLACES",
    "DEFAULT_TABLE_ROW_HEIGHT",
    "DEFAULT_EXPORT_DIR",
    "DEFAULT_CSV_ENCODING"
]
