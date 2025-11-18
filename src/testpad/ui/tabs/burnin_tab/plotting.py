"""Plotting functions for burn-in error report."""
# TODO: Refactor to include plotting calls in presenter (possibly)

import contextlib
import os
import tempfile
from pathlib import Path

from matplotlib.figure import Figure


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
    except Exception:
        # Clean up on error
        with contextlib.suppress(OSError):
            Path(temp_path).unlink()
        raise
    else:
        return temp_path
