"""Pure plotting functions for burn-in error report.

This module provides pure functions for creating matplotlib figures

"""

import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

import h5py
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from testpad.config.plotting import (
    DEFAULT_LINE_STYLE,
    DEFAULT_LINE_WIDTH,
    GRID_ALPHA,
    GRID_ENABLED,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH,
    PRIMARY_COLOR,
)


def make_axis_error_figure(
    data: h5py.File,
    size_inches: tuple[float, float] = (5.0, 3.5),
    dpi: int = 300,
) -> Figure:
    """Create matplotlib figure for Axis error.

    Args:
        data: hdf5 file containing time in seconds and error in counts
        size_inches: Figure size in inches (width, height)
        dpi: Dots per inch for the figure

    Returns:
        matplotlib Figure object ready for saving or display

    """
    with data as file:
        error = list(file["Error (counts)"])
        time = list(file["Time (s)"])

    # Separate error values

    # Create figure
    fig = Figure(figsize=size_inches, tight_layout=True)
    ax = fig.add_subplot(111)

    data_tuple = (time, error)
    # Plot data
    plot_time_series_on_axis(ax, data_tuple)

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
    temp_fd, temp_path = tempfile.mkstemp(suffix=".png", dir=output_dir)
    os.close(temp_fd)  # Close the file descriptor

    try:
        figure.savefig(temp_path, dpi=figure.get_dpi(), bbox_inches="tight")
        return temp_path
    except Exception:
        # Clean up on error
        try:
            Path(temp_path).unlink()
        except OSError:
            pass
        raise


def normalize_time_series_data(
    data: Mapping[int, float] | Sequence[tuple[int, float]],
) -> list[tuple[int, float]]:
    """Normalize data to sorted list of (seconds, error) tuples."""
    if hasattr(data, "items"):
        return sorted((int(k), float(v)) for k, v in data.items())
    return sorted((int(k), float(v)) for k, v in data)


def plot_time_series_on_axis(
    ax: Axes,
    data: Mapping[int, float] | Sequence[tuple[int, float]],
) -> None:
    """Plot time series data on an existing matplotlib axis.

    This function draws the time series plot on the provided axis without
    creating a new figure. Useful for embedding plots in existing figures
    or updating widget axes.

    Args:
        ax: Matplotlib Axes object to plot on
        data: Either a dict {seconds: error} or list of (seconds, erorr(counts)) tuples

    """
    # Normalize data to list of tuples
    pairs = normalize_time_series_data(data)

    # Plot data if available
    if pairs:
        time_s, err_counts = zip(*pairs, strict=False)
        ax.plot(
            time_s,
            err_counts,
            color=PRIMARY_COLOR,
            linestyle=DEFAULT_LINE_STYLE,
            linewidth=DEFAULT_LINE_WIDTH,
            label="Error (counts)",
        )

    # Set title
    ax.set_title("Error (counts) vs Time (seconds)")

    # Set labels
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Error (counts)")

    # Add grid
    ax.grid(
        GRID_ENABLED,
        alpha=GRID_ALPHA,
        linestyle=GRID_LINE_STYLE,
        linewidth=GRID_LINE_WIDTH,
    )
