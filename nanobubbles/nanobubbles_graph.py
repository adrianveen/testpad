from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import yaml
import decimal
from pathlib import Path

from definitions import SRC_DIR
import requests
from PIL import Image
from io import BytesIO

import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter
from matplotlib.colors import to_rgb, to_hex
from matplotlib.backends.backend_qtagg import FigureCanvas


class NanobubblesGraph():
    def __init__(self, nanobubble_txt) -> None:
        # self.aggregate_representation = np.array([])
        self.nanobubble_txt = nanobubble_txt
        self.raw_data = []
        
        # Check if nanobubble_txt is None
        if nanobubble_txt is None:
            raise ValueError("No file selected") # nanobubble_txt cannot be none
        
        # Process each file if nanobubble_txt is a list
        if isinstance(nanobubble_txt, list):
            for file in nanobubble_txt:
                self._process_file(file)
        else:
            self._process_file(nanobubble_txt)
    
    # function to load fus_icon_transparent.ico file
    def load_icon(self, path):
        image = Image.open(path)
        image_array = np.array(image)
        return image_array

    def _process_file(self, file):
        if file is None:
            raise ValueError("No file selected") # file cannot be none
         
        with open(file, "r") as f:
            data = np.array(np.loadtxt(f, skiprows=89, delimiter="\t")) # SKIPS 89 ROWS (assumed to be metadata)

        # create a giant array where every size is represented count number of times 
        # ex. if there are 80 120nm nanobubbles, add 120nm to this array 80 times 
        
        # removes negative value from dataset -> TODO can remove all negative values instead of -1
        data = data[data[:, 0] >= 0]
        
        # adds processed data to the raw_data list
        self.raw_data.append(data)

    # Generate a color palette based on the base color provided
    def generate_color_palette(self, base_color, num_colors):
        base_rgb = to_rgb(base_color)
        palette = [to_hex((base_rgb[0] * (1 - i / num_colors), 
                           base_rgb[1] * (1 - i / num_colors), 
                           base_rgb[2] * (1 - i / num_colors))) for i in range(num_colors)]
        return palette
    
    # returns canvas of mpl graph to UI

    def get_graphs(self, bin_width, scale, normalize=False, overlaid=False):
        """
        Generate and return a histogram plot of nanobubble size distributions.
        Parameters:
        bin_width (int): The width of each bin in the histogram. If log scale is selected, this will determine the number of bins.
        scale (bool): If True, the x-axis will be in log scale; otherwise, it will be in linear scale.
        normalize (bool, optional): If True, the histogram will be normalized. Default is False.
        overlaid (bool, optional): If True, multiple histograms will be overlaid. Default is False.
        Returns:
        FigureCanvas: The canvas containing the generated plot.
        """
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)
        
        # Generate a color palette based on the base color (FUS Green)
        colors = self.generate_color_palette('#73A89E', len(self.raw_data))
        # load fus_icon png and conver to np array
        image_path = os.path.join(SRC_DIR, "images", "fus_icon_transparent.png")
        image = self.load_icon(image_path)

        # if scale = log, set x-axis to log scale from 1-1000
        if scale:
            self.ax.set_xscale('log')
            self.ax.set_xlim(1, 10000)
            bins = np.logspace(np.log10(1), np.log10(10000), num=int(bin_width))
        else:
            # Linear scale: use linear bins
            bins = np.arange(0, 1000 + bin_width, bin_width)

        if overlaid == False or len(self.raw_data) == 1:
            data = self.raw_data[0]
            sizes = np.repeat(data[:, 0], data[:, 1].astype(int))
            self.ax.hist(sizes, bins=bins, color='#73A89E', edgecolor='black')   
        
        elif overlaid == True:

            # Plot multiple overlaid and translucent histograms
            for i, data in enumerate(self.raw_data):
                sizes = np.repeat(data[:, 0], data[:, 1].astype(int))
                self.ax.hist(sizes, bins=bins, alpha=0.5, density=normalize, label=f'Batch {i+1}')
            self.ax.legend(fontsize=14)
        
        # single histogram
        # self.ax.hist(self.raw_data[0], bins=bins, color='#73A89E', rwidth=0.95) 
        
        # graph labels
        self.ax.set_xlabel("Diameter [nm]", fontsize=16)
        self.ax.set_ylabel("Count", fontsize=16) # optional y axis label
        self.ax.set_title("Nanobubble Size Distribution", fontsize=18)
        self.ax.tick_params(axis='both', which='major', labelsize=14)
        # self.ax.tick_params(axis='both', which='minor', labelsize=12)

        # formatting x-axis to not be in scientific notation
        self.ax.xaxis.set_major_formatter(ScalarFormatter())
        self.ax.ticklabel_format(style='plain', axis='x')

        if overlaid == False:
            # Define the position and size parameters
            image_xaxis = 0.835
            image_yaxis = 0.82
        else: 
            image_xaxis = 0.1
            image_yaxis = 0.82
            
        image_width = 0.12
        image_height = 0.12  # Same as width since our logo is a square

        # Define the position for the image axes
        ax_image = self.fig.add_axes([image_xaxis,
                                image_yaxis,
                                image_width,
                                image_height]
                            )

        # Display the image
        ax_image.imshow(image)
        ax_image.axis('off')  # Remove axis of the image

        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.11, right=0.95, top=0.95, bottom=0.08)

        self.fig.set_canvas(self.canvas)
        return(self.canvas)
    
    # save the canvas graph as a SVG 
    def save_graph(self, folder, overlaid=False):
        # Check if nanobubble_txt is a list and get the first file path
        if overlaid == True:
            nanobubble_svg_filename = "multi_batch_histogram"#(Path(self.nanobubble_txt[0]).name).split(".")[0]
        else:
            nanobubble_svg_filename = (Path(self.nanobubble_txt[0]).name).split(".")[0]
        
        full_save_name = os.path.join(folder, str(nanobubble_svg_filename) + ".svg")

        # Debugging statement
        print(f"Saving graph to: {full_save_name}")
        
        self.fig.savefig(full_save_name, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
        return full_save_name

if __name__ == "__main__":
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt")
    n.get_graphs()
    plt.show()