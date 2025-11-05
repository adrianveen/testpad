"""Pure plotting functions for testpad modules.

This module provides pure functions for creating matplotlib figures

"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from testpad.config.plotting import (
    AVG_LINE_COLOR,
    DEFAULT_LINE_STYLE,
    GRID_ALPHA,
    GRID_ENABLED,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH,
    PRIMARY_COLOR,
    THIN_LINE_WIDTH,
)


def plot_xy(
    x: np.ndarray,
    y: np.ndarray,
    labels: dict[str, str],
    colors: list[str],
) -> Figure:
    """Plot x vs y.

    Args:
        x: x values
        y: y values
        labels: Dictionary of labels for x and y
        colors: List of colors for each y value

    Returns:
        matplotlib Figure object ready for saving or display

    """
    # Create figure
    fig = plt.figure()

    # Plot data
    plt.plot(
        x,
        y,
        color=colors[0],
        linestyle=DEFAULT_LINE_STYLE,
        linewidth=THIN_LINE_WIDTH,
    )

    title = labels["title"]
    xlabel = labels["xlabel"]
    ylabel = labels["ylabel"]
    # Set labels
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # Set title
    plt.title(title)

    fig.tight_layout(pad=0.5)

    return fig


def plot_x_multiple_y(
    x: np.ndarray,
    y: list[np.ndarray],
    line_labels: dict[str, str],
    data_labels: list[str],
    colors: list[str],
) -> Figure:
    """Plot x1 vs x2 vs y.

    Args:
        x: x values
        y: List of arrays of y values
        line_labels: Dictionary of labels for x and y
        data_labels: List legend of labels for each y value
        colors: List of colors for each y value

    Returns:
        matplotlib Figure object ready for saving or display

    Raises:
        ValueError: If the lengths of colors and y are not equal.

    """
    # Validate lengths
    if len(colors) != len(y):
        msg = f"colors length ({len(colors)}) must match y length ({len(y)})"
        raise ValueError(msg)

    if data_labels is not None and len(data_labels) != len(y):
        msg = (
            f"data_labels length ({len(data_labels)}) must match y length ({len(y)})"
        )
        raise ValueError(msg)

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Plot data
    for i, y_vals in enumerate(y):
        ax.plot(
            x,
            y_vals,
            color=colors[i],
            label=data_labels[i],
            linestyle=DEFAULT_LINE_STYLE,
            linewidth=THIN_LINE_WIDTH,
        )

    # Set labels
    ax.set_xlabel(line_labels["xlabel"])
    ax.set_ylabel(line_labels["ylabel"])
    ax.set_title(line_labels["title"])

    ax.legend()

    # Set grid
    ax.grid(
        visible=GRID_ENABLED,
        alpha=GRID_ALPHA,
        linestyle=GRID_LINE_STYLE,
        linewidth=GRID_LINE_WIDTH,
    )

    fig.tight_layout(pad=0.5)

    return fig


### WE MIGHT NOT NEED THIS - can possibly use plot_x_multiple_y
def plot_overlay(x: np.ndarray, y: list, labels: dict[str, str]) -> Figure:
    """Plot data with an overlaid line.

    Args:
        x: x values
        y: y values
        labels: Dictionary of labels for x and y

    Returns:
        matplotlib Figure object ready for saving or display

    """
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Plot data
    for i, y_vals in enumerate(y):
        if i == 0:
            ax.plot(
                x,
                y_vals,
                color=PRIMARY_COLOR,
                linestyle=DEFAULT_LINE_STYLE,
                linewidth=THIN_LINE_WIDTH,
            )
            ax.plot(
                x,
                y_vals,
                color=AVG_LINE_COLOR,
                linestyle=DEFAULT_LINE_STYLE,
                linewidth=THIN_LINE_WIDTH,
            )

    title = labels["title"]
    xlabel = labels["xlabel"]
    ylabel = labels["ylabel"]
    # Set labels
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # Set title
    plt.title(title)

    fig.tight_layout(pad=0.5)

    return fig
