"""Pure plotting functions for burn-in error report.

This module provides pure functions for creating matplotlib figures

"""

import contextlib
import os
import tempfile
from pathlib import Path

import h5py
from matplotlib.figure import Figure


def make_axis_error_figure(
    data: h5py.File,
    size_inches: tuple[float, float] = (5.0, 3.5),
    dpi: int = 300,
) -> None:
    """Create matplotlib figure for Axis error.

    Args:
        data: hdf5 file containing time in seconds and error in counts
        size_inches: Figure size in inches (width, height)
        dpi: Dots per inch for the figure

    Returns:
        matplotlib Figure object ready for saving or display

    """


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
        with contextlib.suppress(OSError):
            Path(temp_path).unlink()
        raise
