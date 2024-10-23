from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import h5py

class BurninGraph():
    def __init__(self, burnin_file, separate_errors_flags=None) -> None:
        self.burnin_file = burnin_file

        # check if any of the checkboxes that require the error
        ## values to be separated have been checked
        self.separate_errors = (
            any(separate_errors_flags) if separate_errors_flags else False
        )

        # open burn-in file and extract error/time 
        with h5py.File(self.burnin_file) as file:
            self.error = list(file['Error (counts)'])
            self.time = list(file['Time (s)'])

        # conditionally separate error values
        if self.separate_errors:
            self.positive_errors = [
                e if e > 0 else np.nan for e in self.error
            ]
            self.negative_errors = [
                e if e < 0 else np.nan for e in self.error
            ]
        else:
            self.positive_errors = None
            self.negative_errors = None

    # graphs error vs time 
    def getGraph(self):
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)

        self.ax.plot(self.time, self.error)

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Error (counts)")

        # Determine title based on filename
        if "_axis_A_" in self.burnin_file:
            self.ax.set_title("Axis A Error")
        elif "_axis_B_" in self.burnin_file:
            self.ax.set_title("Axis B Error")
        else:
            self.ax.set_title("Unknown Axis")  # Fallback title in case of unexpected filename

        self.fig.set_canvas(self.canvas)
        return(self.canvas)
    
    #graph error vs time with 0 values remove
    def getGraphs_separated(self):

        # generate the figure and axis
        self.fig, self.ax = plt.subplots(1, 1)

        # Plotting
        plt.plot(self.time, self.positive_errors, label='Positive Error (counts)')
        plt.plot(self.time, self.negative_errors, label='Negative Error (counts)', color='#73A89E')

        # Labels and title
        self.ax.set_xlabel("Time (ms)")
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
        self.ax.legend(loc='best')

        self.canvas = FigureCanvas(self.fig)

        return self.canvas
    
    # calculate moving average of error values and produce graph for positive and negative error separately
    def movingAvg(self):
        
        error_df_pos = pd.DataFrame({
            'time': self.time,
            'pos_error':self.positive_errors
        })
        
        # apply moving average with a window of ratio 1:17 (len(x)/10000)
        error_df_pos['pos_moving_avg'] = error_df_pos[
            'pos_error'].rolling(window=17/int(len(error_df_pos.iloc[:,1])),
                                          min_periods=1).mean()
        
        error_df_neg = pd.DataFrame({
            'time': self.time,
            'neg_error':self.negative_errors
        })

        # apply moving average with a window of ratio 1:17 (len(x)/10000) - Negative error
        error_df_neg['neg_moving_avg'] = error_df_neg[
            'neg_moving_avg_raw'].rolling(window=17/int(len(error_df_neg.iloc[:,1])),
                                          min_periods=1).mean()
        
        # generate figure for positive error values
        self.fig_pos, self.ax_pos = plt.subplots(1, 1)

        # plotting positive values
        self.ax_pos.plot(error_df_pos['time'], error_df_pos['pos_error'],
                         label='Positive Error Data', color='#73A89E')
        self.ax_pos.plot(error_df_pos['time'], error_df_pos['pos_moving_avg'],
                         label='Positive Moving Average', color='#B84548')
        
        # Labels and title
        self.ax_pos.set_xlabel("Time (ms)")
        self.ax_pos.set_ylabel("Error (counts)")
        self.ax_pos.set_title("Error in Positive Direction")
        self.ax_pos.legend()

        self.pos_canvas = FigureCanvas(self.fig_pos) # assign positive error figure to canvas var

        # generate figure for negative error values
        self.fig_neg, self.ax_neg = plt.subplots(1, 1)

        # plotting negative values
        self.ax_neg.plot(error_df_neg['time'], error_df_neg['neg_error'],
                         label='Negative Error Data', color='#73A89E')
        self.ax_neg.plot(error_df_neg['time'], error_df_neg['neg_moving_avg'],
                            label='Negative Moving Average', color='#B84548')
        
        # Labels and title
        self.ax_neg.set_xlabel("Time (ms)")
        self.ax_neg.set_ylabel("Error (counts)")
        self.ax_neg.set_title("Error in Negative Direction")
        self.ax_neg.legend()

        self.neg_canvas = FigureCanvas(self.fig_neg) # assign negative error figure to canvas var

        return self.neg_canvas, self.pos_canvas