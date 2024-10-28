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
            return mean_error, median_error, std_error, var_error, max_error, min_error, q25_error, q75_error, skew_error, kurtosis_error, pct_above_thresh, pct_below_thresh, num_peaks, num_drops

        def display_stats(title, stats):
            """Display the calculated statistics in the textbox."""
            mean, median, std, var, max_val, min_val, q25, q75, skew, kurtosis, pct_abv, pct_blw, peaks, drops = stats
            self.textbox.append(f"<b><u>{title}</u></b>")
            # self.textbox.append(f"Mean: {int(mean)}")
            # self.textbox.append(f"Median: {int(median)}")
            # self.textbox.append(f"Min: {int(min_val)}")
            # self.textbox.append(f"Max: {int(max_val)}")
            # self.textbox.append("Standard Deviation: {:.2f}".format(std))
            # self.textbox.append("Variance: {:.2f}".format(var))
            # self.textbox.append(f"25th Percentile (Q1): {int(q25)}")
            # self.textbox.append(f"75th Percentile (Q3): {int(q75)}")
            # self.textbox.append("Skewness: {:.2f}".format(skew))
            # self.textbox.append("Kurtosis: {:.2f}".format(kurtosis))
            # self.textbox.append("Percentage above threshold: {:.2%}".format(pct_abv))
            # self.textbox.append("Percentage below threshold: {:.2%}".format(pct_blw))
            # self.textbox.append("Number of peaks above threshold: {}".format(peaks))
            # self.textbox.append("Number of drops below threshold: {}".format(drops))
            # self.textbox.append("RMS error: {:.2f}\n".format(rms))
            stats_list = [["Mean", int(mean)],
                    ["Median", int(median)],
                    ["Min", int(min_val)],
                    ["Max", int(max_val)],
                    ["Standard Deviation", f"{std:.2f}"],
                    ["Variance", f"{var:.2f}"],
                    ["25th Percentile (Q1)", int(q25)],
                    ["75th Percentile (Q3)", int(q75)],
                    ["Skewness", f"{skew:.2f}"],
                    ["Kurtosis", f"{kurtosis:.2f}"],
                    ["Percentage above threshold", f"{pct_abv:.2%}"],
                    ["Percentage below threshold", f"{pct_blw:.2%}"],
                    ["Number of peaks above threshold", peaks],
                    ["Number of drops below threshold", drops],
                ]
            
            return stats_list
        
        def display_table(data, add_gap=True):
            # if add_gap:
            #     self.textbox.append("<br><br>")
            
            #create basic HTML table structure
            table_html = "<table border='1'> cellpadding='4' cellspacing='0' width='100%'>"
            #create table header
            table_html += "<tr><th> Statistic </th><th> Value </th></tr>"

            #add rows to the table based on the data
            for stat, value in data:
                table_html += f"<tr><td> {stat} </td><td> {value} </td></tr>"

            table_html += "</table>"

            self.textbox.append(table_html)
            self.textbox.append("<div style='line-height:0.5;'><br></div>")
        # Separate positive and negative errors
        positive_errors = np.array([e if e > 0 else np.nan for e in self.error])
        negative_errors = np.array([e if e < 0 else np.nan for e in self.error])

        # Calculate and display positive error statistics
        positive_stats = calculate_stats(positive_errors)
        pos_listof_stats = display_stats("Positive Error Statistics:", positive_stats)
        display_table(pos_listof_stats)
        # Calculate and display negative error statistics
        negative_stats = calculate_stats(negative_errors)
        neg_listof_stats = display_stats("\nNegative Error Statistics:\n", negative_stats)
        display_table(neg_listof_stats)
