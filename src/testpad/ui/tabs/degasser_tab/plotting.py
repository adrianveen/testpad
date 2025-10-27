"""Pure plotting functions for degasser time series charts.

This module provides pure functions for creating matplotlib figures without
any Qt dependencies, following separation of concerns principles.
"""
import os
import tempfile
from typing import Mapping, Optional, Sequence, Tuple

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from testpad.config.plotting import (
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
    GRID_ALPHA,
    GRID_ENABLED,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH,
    PRIMARY_COLOR,
)


def make_time_series_figure(
    data: Mapping[int, float] | Sequence[Tuple[int, float]],
    temperature_c: Optional[float] = None,
    size_inches: tuple[float, float] = (5.0, 3.5),
    dpi: int = 300,
) -> Figure:
    """Create a matplotlib figure for time series data.

    Args:
        data: Either a dict {minute: oxygen_level} or list of (minute, oxygen_level) tuples
        temperature_c: Optional temperature in Celsius for title
        size_inches: Figure size in inches (width, height)
        dpi: Dots per inch for the figure

    Returns:
        matplotlib Figure object ready for saving or display
    """
    # Create figure
    fig = Figure(figsize=size_inches, tight_layout=True)
    ax = fig.add_subplot(111)

    # Use the axis-level plotting function to avoid duplication
    plot_time_series_on_axis(ax, data, temperature_c)

    # Set DPI
    fig.set_dpi(dpi)

    return fig

def save_figure_to_temp_file(figure: Figure, output_dir: str = ".") -> str:
    """Save a matplotlib figure to a temporary PNG file.
    
    Args:
        figure: matplotlib Figure to save
        output_dir: Directory to save the temporary file
        
    Returns:
        Path to the saved PNG file
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.png', dir=output_dir)
    os.close(temp_fd)  # Close the file descriptor
    
    try:
        figure.savefig(temp_path, dpi=figure.get_dpi(), bbox_inches='tight')
        return temp_path
    except Exception:
        # Clean up on error
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise

def normalize_time_series_data(
    data: Mapping[int, float] | Sequence[Tuple[int, float]]
    ) -> list[tuple[int, float]]:
    """Normalize data to sorted list of (minute, oxygen) tuples."""
    if hasattr(data, "items"):
          return sorted((int(k), float(v)) for k, v in data.items())
    return sorted((int(k), float(v)) for k, v in data)


def plot_time_series_on_axis(
    ax: Axes,
    data: Mapping[int, float] | Sequence[Tuple[int, float]],
    temperature_c: Optional[float] = None,
) -> None:
    """Plot time series data on an existing matplotlib axis.

    This function draws the time series plot on the provided axis without
    creating a new figure. Useful for embedding plots in existing figures
    or updating widget axes.

    Args:
        ax: Matplotlib Axes object to plot on
        data: Either a dict {minute: oxygen_level} or list of (minute, oxygen_level) tuples
        temperature_c: Optional temperature in Celsius for title
    """
    # Normalize data to list of tuples
    pairs = normalize_time_series_data(data)

    # Plot data if available
    if pairs:
        time_min, ox_level = zip(*pairs)
        ax.plot(
            time_min, ox_level,
            color='k',
            marker=DEFAULT_MARKER,
            markersize=DEFAULT_MARKER_SIZE,
            mew=1,
            mec='k',
            mfc=PRIMARY_COLOR,
            linestyle=DEFAULT_LINE_STYLE,
            linewidth=DEFAULT_LINE_WIDTH,
            label='Oxygen Level (mg/L)'
        )

    # Set title with optional temperature
    if temperature_c is not None:
        ax.set_title(f"Dissolved Oxygen vs Time (Temp: {temperature_c:.1f} °C)")
    else:
        ax.set_title("Dissolved Oxygen vs Time")

    # Set labels
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Dissolved O2 (mg/L)")

    # Add grid
    ax.grid(GRID_ENABLED, alpha=GRID_ALPHA, linestyle=GRID_LINE_STYLE, linewidth=GRID_LINE_WIDTH)