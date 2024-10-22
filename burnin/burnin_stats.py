import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.signal import find_peaks
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
            #setup usful variables
            threshold = 40
            valid_count = np.sum(~np.isnan(errors))
            abs_errors = np.abs(errors)
            
            #most basic summary statistics
            mean_error = np.nanmean(errors)
            median_error = np.nanmedian(errors)
            std_error = np.nanstd(errors)
            var_error = np.nanvar(errors)
            max_error = np.nanmax(abs_errors)
            min_error = np.nanmin(abs_errors)
            
            #additional summary statistics
            rms_error = np.sqrt(np.nanmean(errors**2))
            q25_error = np.nanpercentile(errors, 25)
            q75_error = np.nanpercentile(errors, 75)
            skew_error = pd.Series(errors).skew()
            kurtosis_error = pd.Series(errors).kurtosis()
            
            #other info on data
            pct_above_thresh = np.sum(abs_errors > threshold) / valid_count
            pct_below_thresh = np.sum(abs_errors < threshold) / valid_count
            peaks, _ = find_peaks(errors, height=threshold)
            drops, _ = find_peaks(-errors, height=threshold)
            num_peaks = len(peaks)
            num_drops = len(drops)
            return mean_error, median_error, std_error, var_error, max_error, min_error, rms_error, q25_error, q75_error, skew_error, kurtosis_error, pct_above_thresh, pct_below_thresh, num_peaks, num_drops

        def display_stats(title, stats):
            """Display the calculated statistics in the textbox."""
            mean, median, std, var, max_val, min_val, rms, q25, q75, skew, kurtosis, pct_abv, pct_blw, peaks, drops = stats
            self.textbox.append(f"{title}")
            self.textbox.append(f"Mean: {int(mean)}")
            self.textbox.append(f"Median: {int(median)}")
            self.textbox.append(f"Min: {int(min_val)}")
            self.textbox.append(f"Max: {int(max_val)}")
            self.textbox.append("Standard Deviation: {:.2f}".format(std))
            self.textbox.append("Variance: {:.2f}".format(var))
            self.textbox.append("25th Percentile (Q1): {:.2f}".format(q25))
            self.textbox.append("75th Percentile (Q3): {:.2f}".format(q75))
            self.textbox.append("Skewness: {:.2f}".format(skew))
            self.textbox.append("Kurtosis: {:.2f}".format(kurtosis))
            self.textbox.append("Percentage above threshold: {:.2%}".format(pct_abv))
            self.textbox.append("Percentage below threshold: {:.2%}".format(pct_blw))
            self.textbox.append("Number of peaks above threshold: {}".format(peaks))
            self.textbox.append("Number of drops below threshold: {}".format(drops))
            self.textbox.append("RMS error: {:.2f}\n".format(rms))

        # Separate positive and negative errors
        positive_errors = np.array([e if e > 0 else np.nan for e in self.error])
        negative_errors = np.array([e if e < 0 else np.nan for e in self.error])

        # Calculate and display positive error statistics
        positive_stats = calculate_stats(positive_errors)
        display_stats("Positive Error Statistics:", positive_stats)

        # Calculate and display negative error statistics
        negative_stats = calculate_stats(negative_errors)
        display_stats("Negative Error Statistics:", negative_stats)
