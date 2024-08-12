from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import yaml
import decimal
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qtagg import FigureCanvas

# x values: input mV (get average from 5 sweeps [SHOULD BE THE SAME FOR ALL OF THEM, THOUGH])
# y values: neg pressure (get average from 5 sweeps)

# average gain from closest frequency of both EB-50 YAML files 
# get the difference of both 

# scale x values by gain difference 
# linear regression between x values and y values 

class Vol2Press():
    def __init__(self, cal_eb50_file, sys_eb50_file, sweep_txt) -> None:
        self.freq = sweep_txt.split("_")[-2]
        # print(self.freq)
        self.closest_cal_freq, self.cal_eb50_dict = self.closest_frequency(self.freq, cal_eb50_file)
        # print(self.closest_cal_freq)
        self.closest_sys_freq, self.sys_eb50_dict = self.closest_frequency(self.freq, sys_eb50_file)
        # print(self.closest_sys_freq)
        self.sweep_array = np.loadtxt(sweep_txt, delimiter=",", skiprows=5)
        self.input_mV = self.sweep_array[:, 3]
        self.neg_pressure = self.sweep_array[:, 0]
        self.cal_avg_gain = np.mean(self.cal_eb50_dict['gain'])
        self.sys_avg_gain = np.mean(self.sys_eb50_dict['gain'])
        # print(self.cal_avg_gain)
        # print(self.sys_avg_gain)

        self.gain_diff = self.cal_avg_gain - self.sys_avg_gain

        self.x_values = self.input_mV * (10**(self.gain_diff/20))
        self.y_values = self.neg_pressure

    def return_B_value(self):
        A = np.vstack([self.x_values]).T
        self.m = np.linalg.lstsq(A, self.y_values, rcond=None)[0][0]
        return(self.m)
    
    def getGraphs(self):
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)

        self.ax.plot(self.input_mV, self.neg_pressure, label="With calibration EB-50", ls='None', marker='o')
        self.ax.plot(self.x_values, self.y_values, label="With customer EB-50", ls='None', marker='o')
        self.ax.axline((0, 0), slope=self.m, label="Regression line", color='g')

        self.ax.set_xlabel("Input voltage (Vpp)")
        self.ax.set_ylabel("Pressure (MPa)")

        self.ax.legend()

        self.fig.set_canvas(self.canvas)
        return(self.canvas)

    # convert Hz to kHz, MHz 
    def fmt(self, freq):
        SI_Frequency = [(1000, "kHz"), (1000000, "MHz")]
        useFactor, useName = SI_Frequency[0]
        for factor, name in SI_Frequency:
            if freq >= factor:
                useFactor, useName = factor, name 
        return (freq/useFactor, useName)
    
    # convert kHz to MHz 
    def fmt_kHz_to_MHz(self, freq):
        new_freq = float(freq[:-3])/1000
        return(new_freq, "MHz")

    # find the closest frequency to the requested frequency (parsing YAML file)
    def closest_frequency(self, frequency, filename):
        # requested frequency 
        frequency, ending = self.fmt_kHz_to_MHz(frequency)
        # print("Requested frequency:", str(frequency)+ending)
        
        # opens the eb50 file to get the frequencies
        with open(filename) as file: 
            lines = yaml.safe_load(file)

        # find closest frequency (can later be changed into interpolation of two frequencies)
        frequencies = list(lines["frequencies"].keys()) # for all the frequencies in the eb50 file 
        for i in range(len(frequencies)):
            frequencies[i] = float(frequencies[i][:-3]) # gets rid of the kHz/MHz attachment (might have problems with Hz! come up with a fix)

        closest_frequency = str(self.find_nearest(frequencies, float(frequency)))+ending # closest frequency to requested frequency
        # print("Closest frequency in EB-50 file:", closest_frequency)

        eb50_dict = lines["frequencies"][closest_frequency] # fetch the eb-50 data for the closest frequency 

        return(closest_frequency, eb50_dict)

    # used to find the nearest number in an array 
    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
    

if __name__ == "__main__":
    a = Vol2Press(r"C:\Users\RKPC\Downloads\2183-eb50_1.yaml", r"C:\Users\RKPC\Downloads\BRNO-eb50_1.yaml", r"C:\Users\RKPC\Downloads\336-T1200H600\336-T1200H600\1st_harmonic\Report\sweep_336-T1200H600_1200kHz_1.txt")
    print(a.return_B_value())