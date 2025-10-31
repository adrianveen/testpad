"""Report layout configuration for PDF generation.

This module defines layout constants and configuration objects
to eliminate magic numbers and provide a single source of truth
for PDF layout decisions.
"""

from dataclasses import dataclass

from fpdf.enums import TextEmphasis


@dataclass(frozen=True)
class ReportLayout:
    """Immutable configuration for PDF report layout.

    All measurements are in millimeters (mm) for consistency with FPDF.
    """

    # Page margins
    left_margin_mm: float = 10
    top_margin_mm: float = 10
    right_margin_mm: float = 10
    bottom_margin_mm: float = 10

    # Table dimensions
    table_width_mm: float = 70
    table_gap_mm: float = 5  # Gap between table and figure

    # Figure constraints
    figure_max_width_mm: float = 120
    figure_min_width_mm: float = 40
    figure_max_height_mm: float = 120  # Increased from 100mm

    # Spacing
    large_spacing_mm: float = 10
    section_spacing_mm: float = 5
    title_spacing_mm: float = 5

    def calculate_figure_width(self, page_width_mm: float) -> float:
        """Calculate optimal figure width based on available space.

        Args:
            page_width_mm: Total page width in mm

        Returns:
            Figure width in mm

        """
        available_width = (
            page_width_mm
            - self.left_margin_mm
            - self.right_margin_mm
            - self.table_width_mm
            - self.table_gap_mm
        )

        return max(
            self.figure_min_width_mm, min(self.figure_max_width_mm, available_width)
        )

    def get_figure_position(self, page_width_mm: float) -> tuple[float, float]:
        """Calculate figure position (x, y) in mm.

        Args:
            page_width_mm: Total page width in mm

        Returns:
            Tuple of (x_position_mm, y_position_mm)

        """
        x_position = self.left_margin_mm + self.table_width_mm + self.table_gap_mm
        return x_position, 0  # y_position will be set by caller


# Default layout instance
DEFAULT_LAYOUT = ReportLayout()


# Figure sizing configuration
@dataclass(frozen=True)
class FigureConfig:
    """Configuration for matplotlib figure generation."""

    size_inches: tuple[float, float] = (5.0, 5.0)  # Made taller (was 4.0)
    dpi: int = 300

    def calculate_size_for_width(self, target_width_mm: float) -> tuple[float, float]:
        """Calculate figure size to fit target width while maintaining aspect ratio.

        Args:
            target_width_mm: Desired width in mm

        Returns:
            Tuple of (width_inches, height_inches)

        """
        # Convert mm to inches (1 inch = 25.4 mm)
        target_width_inches = target_width_mm / 25.4

        # Maintain aspect ratio
        aspect_ratio = self.size_inches[1] / self.size_inches[0]
        height_inches = target_width_inches * aspect_ratio

        return target_width_inches, height_inches


# Default figure configuration
DEFAULT_FIGURE_CONFIG = FigureConfig()


# Color constants (module level for reuse)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (128, 128, 128)


@dataclass(frozen=True)
class ReportStyleConfig:
    """Configuration for report visual styling.

    Centralizes all typography, colors, and branding for PDF reports.
    Use DEFAULT_STYLE_CONFIG for standard styling.
    """

    # Typography
    font_family: str = "helvetica"

    # Colors (RGB tuples for FPDF compatibility)
    title_text_color: tuple[int, int, int] = COLOR_BLACK
    subtitle_text_color: tuple[int, int, int] = COLOR_BLACK
    header_text_color: tuple[int, int, int] = COLOR_BLACK
    spec_text_color: tuple[int, int, int] = COLOR_BLACK
    data_text_color: tuple[int, int, int] = COLOR_GREY

    # Font Emphasis (FPDF style strings: "B" = bold, "I" = italic, "BI" = both)
    title_text_style: TextEmphasis = TextEmphasis.B
    metadata_text_style: TextEmphasis = TextEmphasis.B
    subtitle_text_style: TextEmphasis = TextEmphasis.B
    header_text_style: TextEmphasis = TextEmphasis.B
    values_text_style: TextEmphasis = TextEmphasis.NONE

    # Font Sizes (in points)
    title_text_size: int = 16
    subtitle_text_size: int = 12
    metadata_text_size: int = 10
    header_text_size: int = 10
    spec_text_size: int = 10
    data_text_size: int = 10

    # Branding
    logo_width_mm: float = 60.0
    logo_keep_aspect_ratio: bool = True


# Default style configuration
DEFAULT_STYLE_CONFIG = ReportStyleConfig()
