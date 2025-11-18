"""Physical and scientific constants for FUS Instruments Testpad.

These values are based on physical laws and should never change.
"""

# === Temperature Constants ===
ABSOLUTE_ZERO_C = -273.15  # Celsius
WATER_BOILING_C = 100.0  # Celsius
STANDARD_ROOM_TEMP_C = 25.0  # Celsius
ABSOLUTE_ZERO_K = 0.0  # Kelvin

# === Physical Limits ===
MIN_OXYGEN_LEVEL_MG_L = 0.0  # mg/L
MAX_OXYGEN_LEVEL_MG_L = 50.0  # mg/L (approximate max for water at sea level)
MAX_REASONABLE_TEMP_C = 60.0  # Celsius (beyond this is unlikely for water samples)
