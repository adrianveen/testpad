"""Centralized plotting configuration for FUS Instruments Testpad.

This module provides constants for consistent plot styling across all tabs.
Individual plots can pick and choose which constants to use.
"""

# === Colors ===
# Primary color palette
PRIMARY_COLOR = '#73A89E'      # FUS Instruments teal/green
PRIMARY_COMP_COLOR = "#5A8FAE"
SECONDARY_COLOR = 'k'      # If you have a secondary brand color
ERROR_COLOR = 'r'           # For error/warning indicators

# === Line Styling ===
DEFAULT_LINE_WIDTH = 2.0
THIN_LINE_WIDTH = 1.0
THICK_LINE_WIDTH = 3.0
DEFAULT_LINE_STYLE = '-'       # solid
DASHED_LINE_STYLE = '--'

# === Marker Styling ===
DEFAULT_MARKER = 'o'
DEFAULT_MARKER_SIZE = 6

# === Grid Styling ===
GRID_ENABLED = True
GRID_ALPHA = 0.5
GRID_LINE_STYLE = '--'
GRID_LINE_WIDTH = 0.6

# === Figure Sizing ===
DEFAULT_FIGURE_SIZE = (5, 3)
LARGE_FIGURE_SIZE = (8, 5)

# === Font Sizes ===
TITLE_FONT_SIZE = 12
LABEL_FONT_SIZE = 10
TICK_FONT_SIZE = 8

# === Other ===
DPI = 100  # For saving figures