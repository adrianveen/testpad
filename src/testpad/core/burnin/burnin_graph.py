"""BurninGraph class for generating graphs of the error vs time."""

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class BurninGraph:
    """BurninGraph class for generating graphs of the error vs time."""

    def __init__(
        self, burnin_file: str, separate_errors_flags: list | None = None
    ) -> None:
        """Initialize the BurninGraph class.

        Args:
            burnin_file (str): Path to the burn-in file.
            separate_errors_flags (list | None): A list of flags indicating whether
                the error values should be separated into positive and negative values.
                If None, the error values will not be separated.

        Attributes:
            burnin_file (str): Path to the burn-in file.
            separate_errors (bool): Whether the error values should be separated.
            positive_errors (list): List of positive error values.
            negative_errors (list): List of negative error values.

        """
        if separate_errors_flags is None:
            separate_errors_flags = []
        self.burnin_file = burnin_file

        # check if any of the checkboxes that require the error
        # values to be separated have been checked
        self.separate_errors = (
            any(separate_errors_flags) if separate_errors_flags else False
        )

        # open burn-in file and extract error/time
        with h5py.File(self.burnin_file) as file:
            self.error = np.array(file["Error (counts)"])
            self.time = np.array(file["Time (s)"])

        # conditionally separate error values
        if self.separate_errors:
            self.positive_errors = np.where(self.error > 0, self.error, np.nan)
            self.negative_errors = np.where(self.error < 0, self.error, np.nan)

    # graphs error vs time
    def get_graph(self) -> FigureCanvas:
        """Generate canvas for the error vs time graph.

        :param self: Description
        :return: Description
        :rtype: FigureCanvasQTAgg
        """
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)

        # Determine title based on filename
        if "_axis_A_" in self.burnin_file:
            title = "Axis A Error"
            self.ax.plot(self.time, self.error, color="#73A89E")
        elif "_axis_B_" in self.burnin_file:
            title = "Axis B Error"
            self.ax.plot(self.time, self.error, color="#5A8FAE")
        else:
            title = (
                "Unknown Axis"  # Fallback title in case of unexpected filename
            )

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Error (counts)")

        self.ax.set_title(title)

        self.fig.tight_layout(pad=0.5)

        self.fig.set_canvas(self.canvas)

        plt.close("all")

        return self.canvas

    # graph error vs time with 0 values remove
    def get_graphs_separated(self) -> FigureCanvas:
        """Generate canvas for the error vs time graph.

        :param self: Description
        :return: Description
        :rtype: FigureCanvasQTAgg
        """
        # generate the figure and axis
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 6))

        try:
            self.canvas = FigureCanvas(self.fig)

            # Plotting
            self.ax.plot(
                self.time,
                self.positive_errors,
                label="Positive Error (counts)",
                color="#5A8FAE",
            )
            self.ax.plot(
                self.time,
                self.negative_errors,
                label="Negative Error (counts)",
                color="#73A89E",
            )

            # Labels and title
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Error (counts)")

            # Determine title based on filename
            if "_axis_A_" in self.burnin_file:
                title = "Axis A Error"
            elif "_axis_B_" in self.burnin_file:
                title = "Axis B Error"
            else:
                title = "Unknown Axis"  # Fallback title in case of unexpected filename

            self.ax.set_title(title)
            # add the legend in the best location around the center of the graph
            self.ax.legend(loc="best")

            # reduce white space
            self.fig.tight_layout(pad=0.5)

            self.fig.set_canvas(self.canvas)

            plt.close("all")  # close all figures to prevent memory leak

            return self.canvas

        finally:
            pass

    # calculate moving average of error values and
    # produce graph for positive and negative error separately
    def moving_avg_plot(self) -> list[FigureCanvas]:
        """Take the separated negative and positive error, and produces two graphs.

        The old code is commented out below the for loop.
        Each graph will have it's own canvas and will be returned as a list of canvases.
        The graphs will display the error values and their respective moving averages.
        """
        errors_list = [self.positive_errors, self.negative_errors]
        canvases = []

        for i, errors in enumerate(errors_list):
            error_df = pd.DataFrame({"time": self.time, "error": errors})

            error_df["moving_avg"] = (
                error_df["error"].rolling(window=10000, min_periods=1).mean()
            )

            self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 6))

            if i == 0:
                self.ax.plot(
                    error_df["time"],
                    error_df["error"],
                    label="Error Data",
                    color="#5A8FAE",
                )
                self.ax.plot(
                    error_df["time"],
                    error_df["moving_avg"],
                    label="Moving Average",
                    color="#A8737E",
                )
            else:
                self.ax.plot(
                    error_df["time"],
                    error_df["error"],
                    label="Error Data",
                    color="#73A89E",
                )
                self.ax.plot(
                    error_df["time"],
                    error_df["moving_avg"],
                    label="Moving Average",
                    color="#A8737E",
                )

            if i == 0:
                self.ax.set_title("Error in Positive Direction")
            else:
                self.ax.set_title("Error in Negative Direction")

            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Error (counts)")
            self.ax.legend()

            self.fig.tight_layout(pad=0.5)

            # append canvas to list
            canvases.append(FigureCanvas(self.fig))

            plt.close("all")  # close all figures to prevent memory leak

        return canvases  # return list of canvases

    def got_resize_event(self) -> None:
        """Resizes the figure to fit the canvas."""
        self.fig.tight_layout(pad=0.5)
