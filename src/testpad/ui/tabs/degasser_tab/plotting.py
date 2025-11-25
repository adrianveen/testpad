"""Pure plotting functions for degasser time series charts.

This module provides pure functions for creating matplotlib figures without
any Qt dependencies, following separation of concerns principles.
"""

import contextlib
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, MultipleLocator

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
from testpad.ui.tabs.degasser_tab.config import (
    DISSOLVED_OXYGEN_STRING,
    MG_PER_LITER_STRING,
    TIME_SERIES_HEADERS,
)


def make_time_series_figure(
    data: Mapping[int, float] | Sequence[tuple[int, float]],
    temperature_c: float | None = None,
    size_inches: tuple[float, float] = (5.0, 3.5),
    dpi: int = 300,
) -> Figure:
    """Create a matplotlib figure for time series data.

    Args:
        data: Either a dict {minute: oxygen_level} or list of
            (minute, oxygen_level) tuples
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


def save_figure_to_temp_file(
    figure: Figure, output_dir: str = ".", bbox_inches: str | None = "tight"
) -> str:
    """Save a matplotlib figure to a temporary PNG file.

    Args:
        figure: matplotlib Figure to save
        output_dir: Directory to save the temporary file
        bbox_inches: Bbox strategy for saving (default: "tight")

    Returns:
        Path to the saved PNG file

    """
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".png", dir=output_dir)
    os.close(temp_fd)  # Close the file descriptor

    try:
        figure.savefig(temp_path, dpi=figure.get_dpi(), bbox_inches=bbox_inches)

    except Exception:
        # Clean up on error
        with contextlib.suppress(OSError):
            Path(temp_path).unlink()
        raise
    else:
        return temp_path


def normalize_time_series_data(
    data: Mapping[int, float] | Sequence[tuple[int, float]],
) -> list[tuple[int, float]]:
    """Normalize data to sorted list of (minute, oxygen) tuples."""
    if isinstance(data, Mapping):
        return sorted((int(k), float(v)) for k, v in data.items())
    return sorted((int(k), float(v)) for k, v in data)


def plot_time_series_on_axis(
    ax: Axes,
    data: Mapping[int, float] | Sequence[tuple[int, float]],
    temperature_c: float | None = None,
) -> None:
    """Plot time series data on an existing matplotlib axis.

    This function draws the time series plot on the provided axis without
    creating a new figure. Useful for embedding plots in existing figures
    or updating widget axes.

    Args:
        ax: Matplotlib Axes object to plot on
        data: Either a dict {minute: oxygen_level} or list of
            (minute, oxygen_level) tuples
        temperature_c: Optional temperature in Celsius for title

    """
    # Normalize data to list of tuples
    pairs = normalize_time_series_data(data)

    # Plot data if available
    if pairs:
        time_min, ox_level = zip(*pairs, strict=False)
        ax.plot(
            time_min,
            ox_level,
            color="k",
            marker=DEFAULT_MARKER,
            markersize=DEFAULT_MARKER_SIZE,
            mew=1,
            mec="k",
            mfc=PRIMARY_COLOR,
            linestyle=DEFAULT_LINE_STYLE,
            linewidth=DEFAULT_LINE_WIDTH,
            label=f"Oxygen Level ({MG_PER_LITER_STRING})",
        )
        # Set x-limits to avoid negative ticks while keeping 0 offset
        max_time = max(time_min)
        ax.set_xlim(left=-0.5, right=max_time + 0.5)
        ax.set_ylim(bottom=0 - 0.5)
    else:
        # Default limits if no data
        ax.set_xlim(left=-0.5, right=20.5)

    # Set title with optional temperature
    if temperature_c is not None:
        ax.set_title(
            f"{DISSOLVED_OXYGEN_STRING} vs Time (Temp: {temperature_c:.1f} °C)"
        )
    else:
        ax.set_title(f"{DISSOLVED_OXYGEN_STRING} vs Time")

    # Set labels
    ax.set_xlabel(TIME_SERIES_HEADERS[0])
    ax.set_ylabel(TIME_SERIES_HEADERS[1])

    # Make ticks more frequent
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=10))

    # Add grid
    ax.grid(
        GRID_ENABLED,
        alpha=GRID_ALPHA,
        linestyle=GRID_LINE_STYLE,
        linewidth=GRID_LINE_WIDTH,
    )
