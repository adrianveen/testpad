"""
Script for generating radiation force balance figures. 
"""

# import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.ticker import FormatStrFormatter
# from tkinter.filedialog import askopenfilenames, askdirectory
import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QTextBrowser

# from PySide6.QtCore import QObject, Slot
# from PySide6.QtWidgets import QApplication
# # from PySide6.QtGui import QGuiApplication DO NOT USE BECAUSE CLOSING THE GRAPH WILL CLOSE THE PROGRAM
# from PySide6.QtQml import QQmlApplicationEngine, QmlElement

# QML_IMPORT_NAME = "rfb_figures"
# QML_IMPORT_MAJOR_VERSION = 1

# class for creating the RFB graphs 
class create_rfb_graph():
    def __init__(self, filenames:list, save_folder:str=None, save:bool=False, textbox: QTextBrowser=None) -> None:
        plt.close("all")
        self.filenames = filenames
        self.graphs_list = []
        self.save_folder = save_folder
        # print(self.filenames)
        self.save = save
        self.textbox = textbox
        self.data_mtx = np.zeros((len(self.filenames), 4)) # np array where all the average data will be stored 
        self.textbox.append("********************GENERATING GRAPHS********************")

        # open the filename, read the lines 
        # print(self.filenames)
        for filename in self.filenames:
            with open(filename, "r") as f:
                self.lines = f.readlines()

            # get the indices of the data summary heading and the header row 
            self.heading = self.lines.index("DATA SUMMARY\n") # data summary row begins
            self.header_row = self.lines.index("Time (s),Forward power (W),Reflected power (W),Balance reading (g),Acoustic power (W)\n") # header row to start finding data 
            # print(self.filenames.index(filename))
            self.get_data_summary()
            self.averages_mtx(self.filenames.index(filename))
            self.get_raw_data()
            self.graph()
            # self.fig.show()
        
        # sort the array by fwd pwr
        self.data_mtx = self.data_mtx[self.data_mtx[:, 0].argsort()]
        # print(self.data_mtx)
        average_average_efficiency = np.average(self.data_mtx[:, 3]) # average of the average efficiencies
        self.textbox.append(f"\nAverage of all average efficiencies: {average_average_efficiency:.1f}%")
        
        # save the array of average information to a txt
        if self.save:
            self.textbox.append("[+] creating txt file...")
            header = f"Average of average efficiences (%): {average_average_efficiency:.1f}\n\nAverage forward power (W), Average reflected power (W), Average acoustic power (W), Average efficiency (%)"
            filename = os.path.join(self.save_folder, "average_data.txt")
            # self.save_folder+"\\"+"average_data.txt"
            np.savetxt(filename, self.data_mtx, fmt="%.1f", delimiter=",", header=header, comments='')
            self.textbox.append("[+] finished creating txt")

        self.textbox.append("********************FINISHED EXECUTING*******************\n")

    # gets the raw data lines 
    def get_raw_data(self):
        # RAW DATA 
        # textbox.append(header_row)
        self.raw_data = []

        for line in self.lines[(self.header_row+1):-1]: # lines from header row until last line 'END OF FILE'  
            line = np.array(line.split(',')[:-1], dtype=float) # formats a line as a np array, chopping off the \n at the end
            # print(line)
            self.raw_data.append(line) # add the data to raw_data
            # raw_data = np.vstack([raw_data, line])

        self.raw_data = np.array(self.raw_data) # convert raw_data to a np array

        self.time = self.raw_data[:,0] # (s) 
        self.fwd_pwr = self.raw_data[:,1] # forward power (W)
        self.refl_pwr = self.raw_data[:,2] # reflected power (W) 
        self.bal_read = self.raw_data[:,3] # balance reading (g)
        self.aco_pwr = self.raw_data[:,4] # acoustic power (W) 

    # gets the data summary lines 
    def get_data_summary(self):
        # DATA SUMMARY 
        self.data_summary = {}
        for line in self.lines[(self.heading+1):(self.header_row-2)]: # goes to header_row - 2 because of the line of whitespace between DATA SUMMARY and RAW DATA
            line = line.split(',')
            # print(line)
            self.data_summary[line[0]] = float(line[1])
        
        # relevant average values 
        self.average_fwd_power = self.data_summary["Average forward power (W)"]
        self.average_refl_power = self.data_summary["Average reflected power (W)"]
        self.average_aco_power = self.data_summary["Average acoustic power (W)"]
        self.average_efficiency = self.data_summary["Average efficiency (%)"]

    # creates an array of all the average values from the data summary 
    def averages_mtx(self, rownum:int):
        # store the data summary in matrix 
        # print(rownum)
        
        self.data_mtx[rownum, 0] = self.average_fwd_power
        self.data_mtx[rownum, 1] = self.average_refl_power
        self.data_mtx[rownum, 2] = self.average_aco_power
        self.data_mtx[rownum, 3] = self.average_efficiency

        
        # print(self.data_mtx)

    # used to find the nearest number in an array (NOT CURRENTLY BEING USED ANY LONGER)
    # def find_nearest(self, array, value):
    #     array = np.asarray(array)
    #     idx = (np.abs(array - value)).argmin()
    #     return array[idx]
    
    # makes the power vs balance reading graphs
    def graph(self):
        
        
        self.fig, self.ax = plt.subplots(1, 1)
        # plt.style.use('seaborn-v0_8-whitegrid')
        canvas = FigureCanvas(self.fig)
        # self.fig.suptitle("Radiation Force Balance Measurements") # title 

        # find nearest power, use as graph heading 
        # list_of_power = [0.5, 1.0, 1.5, 2.0, 2.5]
        # graph_heading = str(self.find_nearest(list_of_power, max(self.fwd_pwr)))+"W" # to find the nearest power heading for the graph 

        # use max power rounded to 2 dp as graph heading 
        graph_heading = f"{max(self.fwd_pwr):.2f}W" # to find the heading for the graph 
        self.ax.set_title("Maximum forward power: "+graph_heading)

        self.textbox.append(f"[+] creating {graph_heading} graph...")

        color = 'black'
        self.ax.plot(self.time, self.fwd_pwr, label="Forward Electrical Power (W)", color=color)
        # ax1.plot(self.time, self.refl_pwr, label = "Reflected power (W)")
        # ax1.plot(self.time, self.aco_pwr, label="Acoustic power")
        self.ax.set_ylabel("Forward Electrical Power (W)", color=color)
        self.ax.set_xlabel("Time (s)")
        # ax[0].set_title("Radiation Force Balance Measurements")
        self.ax.tick_params(axis='y', labelcolor=color)
        # set bounds to align grid with axis 2 
        first_bound = self.ax.get_ybound()[0]
        second_bound = self.ax.get_ybound()[1]
        self.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        self.ax.set_yticks(np.linspace(first_bound, second_bound, 5))
        # ax.set_ylim(0, None)        
        self.ax.grid()

        ax2 = self.ax.twinx()

        color = '#6bb097'
        ax2.set_ylabel("Balance Reading (g)", color=color)
        ax2.plot(self.time, self.bal_read, label="Balance reading (g)", color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        average_efficiency = self.data_summary["Average efficiency (%)"]/100
        # print(average_efficiency)
        ax2.set_ylim(None, max(self.bal_read)/average_efficiency) # setting the peak of the balance reading graphs to be at the average efficiency level 
        # set bounds to align grid with axis 1
        first_bound = ax2.get_ybound()[0]
        second_bound = ax2.get_ybound()[1]
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax2.set_yticks(np.linspace(first_bound, second_bound, 5))

        # color = '#6bb097'
        # ax2.set_ylabel("Acoustic Power (W)", color=color)
        # ax2.plot(self.time, self.aco_pwr, label="Acoustic Power (W)", color=color)
        # ax2.tick_params(axis='y', labelcolor=color)
        # ax2.set_ylim(self.ax.get_ylim())

        # self.ax.grid()

        # print average efficiency per graph
        printed_average_efficiency = self.data_summary["Average efficiency (%)"]
        self.textbox.append(f"[+] average efficiency: {printed_average_efficiency:.1f}%")
        # print(average_efficiency)
        # ax2.set_ylim(None, max(self.bal_read)/average_efficiency) # setting the peak of the acoustic power graphs to be at the average efficiency level 

        self.fig.tight_layout()

        if self.save:
            self.textbox.append("[+] saving graphs...")
            filename = os.path.join(self.save_folder, "rfb_measurments_"+graph_heading+".svg") 
            self.fig.savefig(filename, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
        
        self.textbox.append(f"[+] finished making {graph_heading} graph")
        self.fig.set_canvas(canvas)

        self.graphs_list.append([canvas, graph_heading])
        
        # fig.show()