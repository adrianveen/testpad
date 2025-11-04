"""Module contains the BurninStats class, used to compute various statistics."""

from typing import TYPE_CHECKING

import h5py
import numpy as np
from PySide6.QtWidgets import QTextBrowser
from scipy.signal import find_peaks
from scipy.stats import kurtosis, skew

if TYPE_CHECKING:
    from numpy.typing import NDArray

# placeholder file name for testing
filename = "_axis_A_complete_raw_error_29.hdf5"


class BurninStats:
    """Class to compute various statistics for the burn-in data."""

    def __init__(self, burnin_file: str, textbox: QTextBrowser | None = None) -> None:
        """Initialize the BurninStats class.

        Args:
            burnin_file (str): Path to the burn-in file.
            textbox (QTextBrowser): Optional QTextBrowser object to display statistics.

        """
        self.burnin_file = burnin_file
        self.textbox = textbox or QTextBrowser()
        self.negative_stats: tuple = ()
        self.positive_stats: tuple = ()

        # open burn-in file and extract error/time
        with h5py.File(self.burnin_file) as file:
            err_obj = file["Error (counts)"]
            time_obj = file["Time (s)"]

            if not isinstance(err_obj, h5py.Dataset) or not isinstance(
                time_obj, h5py.Dataset
            ):
                msg = "Expected h5py.Dataset for 'Error (counts)' and 'Time (s)'"
                raise TypeError(msg)

            # self.error: NDArray[np.float64] = np.asarray(err_obj[()], dtype=float)
            self.error: NDArray[np.float64] = err_obj[:]
            # self.time: NDArray[np.float64] = np.asarray(time_obj[()], dtype=float)
            self.time = self.time[:]

        # Separate positive and negative errors
        positive_errors = np.where(self.error > 0, self.error, np.nan)
        negative_errors = np.where(self.error < 0, self.error, np.nan)

        # Calculate positive and negative error statistics
        self.positive_stats = self.calculate_stats(positive_errors)
        self.negative_stats = self.calculate_stats(negative_errors)

    def calculate_stats(self, errors: np.ndarray) -> tuple:
        """Calculate statistics for the given error array.

        Args:
            errors (numpy.ndarray): Array of error values.

        Returns:
            tuple: A tuple containing the calculated statistics.

        """
        # setup usful variables
        threshold = 40
        valid_count = np.sum(~np.isnan(errors))
        abs_errors = np.abs(errors)

        # most basic summary statistics
        mean_error = int(np.nanmean(errors))
        median_error = int(np.nanmedian(errors))
        std_error = round(np.nanstd(errors), 2)
        var_error = round(np.nanvar(errors), 2)
        max_error = int(np.nanmax(abs_errors))
        min_error = int(np.nanmin(abs_errors))

        # additional summary statistics
        q25_error = int(np.nanpercentile(abs(errors), 25))
        q75_error = int(np.nanpercentile(abs(errors), 75))
        skew_error = np.round(skew(errors, nan_policy="omit"), 2)
        kurtosis_error = np.round(kurtosis(errors, nan_policy="omit"), 2)

        # other info on data
        pct_above_thresh = round(np.sum(abs_errors > threshold) / valid_count, 2) * 100
        pct_below_thresh = round(np.sum(abs_errors < threshold) / valid_count, 2) * 100
        peaks, _ = find_peaks(errors, height=threshold)
        drops, _ = find_peaks(-errors, height=threshold)
        num_peaks = len(peaks)
        num_drops = len(drops)
        return (
            mean_error,
            median_error,
            min_error,
            max_error,
            std_error,
            var_error,
            q25_error,
            q75_error,
            skew_error,
            kurtosis_error,
            pct_above_thresh,
            pct_below_thresh,
            num_peaks,
            num_drops,
        )

    def display_stats(self, title: str, stats: tuple) -> list:
        """Display the calculated statistics in the textbox."""
        (
            mean,
            median,
            min_val,
            max_val,
            std,
            var,
            q25,
            q75,
            skew_val,
            kurt_val,
            pct_abv,
            pct_blw,
            peaks,
            drops,
        ) = stats

        # titles the table based on the iput (negative or positive error)
        self.textbox.append(f"<b><u>{title}</u></b>")

        return [
            ["Mean", int(mean)],
            ["Median", int(median)],
            ["Min", int(min_val)],
            ["Max", int(max_val)],
            ["Standard Deviation", f"{std:.2f}"],
            ["Variance", f"{var:.2f}"],
            ["25th Percentile (Q1)", f"-{int(q25)}"],
            ["75th Percentile (Q3)", f"-{int(q75)}"],
            ["Skewness", f"{skew_val:.2f}"],
            ["Kurtosis", f"{kurt_val:.2f}"],
            ["Percentage above threshold", f"{pct_abv / 100:.2%}"],
            ["Percentage below threshold", f"{pct_blw / 100:.2%}"],
            ["Number of peaks above threshold", peaks],
            ["Number of drops below threshold", drops],
        ]

    def display_table(self, data: list) -> None:
        """Display the statistics in a table format."""
        # create basic HTML table structure
        table_html = "<table border='1'> cellpadding='4' cellspacing='0' width='100%'>"
        # create table header
        table_html += "<tr><th> Statistic </th><th> Value </th></tr>"

        # add rows to the table based on the data
        for stat, value in data:
            table_html += f"<tr><td> {stat} </td><td> {value} </td></tr>"

        table_html += "</table>"

        self.textbox.append(table_html)
        self.textbox.append("<div style='line-height:0.5;'><br></div>")

    def print_stats(self) -> None:
        """Print the statistics to the textbox."""
        pos_listof_stats = self.display_stats(
            "Positive Error Statistics:",
            self.positive_stats,
        )
        self.display_table(pos_listof_stats)
        # Display negative error statistics
        neg_listof_stats = self.display_stats(
            "\nNegative Error Statistics:\n",
            self.negative_stats,
        )
        self.display_table(neg_listof_stats)
