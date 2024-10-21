import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from PySide6.QtWidgets import QTextBrowser

#placeholder file name for testing
filename = "_axis_A_complete_raw_error_29.hdf5"

class BurninStats():
    def __init__(self, burnin_file, textbox: QTextBrowser) -> None:
        self.burnin_file = burnin_file
        self.textbox = textbox

        # open burn-in file and extract error/time 
        with h5py.File(self.burnin_file) as file:
            self.error = list(file['Error (counts)'])
            self.time = list(file['Time (s)'])

    def printStats(self):
        def calculate_stats(errors):
            """Calculate statistics for the given error array."""
            mean_error = np.nanmean(errors)
            median_error = np.nanmedian(errors)
            std_error = np.nanstd(errors)
            var_error = np.nanvar(errors)
            max_error = np.nanmax(errors)
            min_error = np.nanmin(errors)
            rms_error = np.sqrt(np.nanmean(errors**2))
            return mean_error, median_error, std_error, var_error, max_error, min_error, rms_error

        def display_stats(title, stats):
            """Display the calculated statistics in the textbox."""
            mean, median, std, var, max_val, min_val, rms = stats
            self.textbox.append(f"\n{title}")
            self.textbox.append(f"Mean: {int(mean)}")
            self.textbox.append(f"Median: {int(median)}")
            self.textbox.append(f"Min: {int(min_val)}")
            self.textbox.append(f"Max: {int(max_val)}")
            self.textbox.append("Standard Deviation: {:.2f}".format(std))
            self.textbox.append("Variance: {:.2f}".format(var))
            self.textbox.append("RMS error: {:.2f}".format(rms))

        # Separate positive and negative errors
        positive_errors = np.array([e if e > 0 else np.nan for e in self.error])
        negative_errors = np.array([e if e < 0 else np.nan for e in self.error])

        # Calculate and display positive error statistics
        positive_stats = calculate_stats(positive_errors)
        display_stats("Positive Error Statistics:", positive_stats)

        # Calculate and display negative error statistics
        negative_stats = calculate_stats(negative_errors)
        display_stats("Negative Error Statistics:", negative_stats)
