from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import sys
import yaml
import decimal
from pathlib import Path

from definitions import SRC_DIR
#import requests
from PIL import Image
from io import BytesIO

import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter
from matplotlib.colors import to_rgb, to_hex
from matplotlib.backends.backend_qtagg import FigureCanvas
import pandas as pd


class TemperatureGraph():
    def __init__(self, temperature_csv) -> None:
        # self.aggregate_representation = np.array([])
        self.temperature_csv = temperature_csv
        self.raw_data = []
        
        # Check if temperature_csv is None
        if temperature_csv is None:
            raise ValueError("No file selected") # temperature_csv cannot be none
        
        self.temperature_csv = temperature_csv
        self.raw_data = []

        # Process the file(s) and store the data
        self.raw_data = self._process_files(temperature_csv)
    
    def resource_path(self, relative_path):
        """Get the absolute path to a resource"""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)
    # function to load fus_icon_transparent.ico file
    def load_icon(self, path):
        image = Image.open(path)
        image_array = np.array(image)
        return image_array

    def _process_files(self, file_paths):
        """
        Process one or more CSV files and extract relevant data.
        
        Args:
            file_paths (str or list of str): Single file path or a list of file paths.
            
        Returns:
            list: A list of tuples, where each tuple contains (elapsed time, temperature).
        """
        # Ensure file_paths is always a list
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        self.raw_data = []
        for file_path in file_paths:
            try:
                # Read and process the file
                data = pd.read_csv(file_path)
                data = data.drop(data.columns[[4, 5]], axis=1)  # Remove unused columns
                
                # Append processed data to raw_data
                elapsed = data["Elapsed (s)"]
                temperature = data["244B Temp"]
                # print(f"Elapsed: {elapsed}")
                # print(f"Temperature: {temperature}")
                self.raw_data.append((elapsed, temperature))
                # print(f"Raw data: {self.raw_data}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        return self.raw_data

    # Generate a color palette based on the base color provided
    def generate_color_palette(self, base_color, num_colors):
        base_rgb = to_rgb(base_color)
        palette = [to_hex((base_rgb[0] * (1 - i / num_colors), 
                           base_rgb[1] * (1 - i / num_colors), 
                           base_rgb[2] * (1 - i / num_colors))) for i in range(num_colors)]
        return palette
    
    # returns canvas of mpl graph to UI

    def get_graphs(self, overlaid=False):
        """
        Generate and return a line plot of the temperature over time.

        Args:
            overlaid (bool, optional): If True, multiple line plots will be overlaid. Default is False.
        Returns:
            FigureCanvas: The canvas containing the generated plot.
        """

        # Initialize the figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)

        # Generate a color palette based on the number of datasets
        colors = self.generate_color_palette('#73A89E', len(self.raw_data))

        # Load the FUS icon
        image_path = self.resource_path('images\\fus_icon_transparent.png')
        image = self.load_icon(image_path)

        if overlaid == False or len(self.raw_data) == 1:
            # Single dataset
            data = self.raw_data
            elapsed = data[0][0]
            temperature = data[0][1]
            # print(f"Elapsed: {elapsed}")
            # print(f"Temperature: {temperature}")
            self.ax.plot(elapsed, temperature, color='#73A89E', label="Dataset 1", linewidth=2)
        else:
            # Overlaid datasets
            for i, (elapsed, temperature) in enumerate(self.raw_data):
                self.ax.plot(elapsed, temperature, alpha=0.7, label=f'Dataset {i+1}', color=colors[i], linewidth=1)
            self.ax.legend(fontsize=12)

        # Graph labels
        self.ax.set_xlabel("Elapsed Time (s)", fontsize=14)
        self.ax.set_ylabel("Temperature (°C)", fontsize=14)
        self.ax.set_title("Temperature vs. Elapsed Time", fontsize=16)
        self.ax.tick_params(axis='both', which='major', labelsize=12)

        # Format x-axis to not use scientific notation
        self.ax.xaxis.set_major_formatter(ScalarFormatter())
        self.ax.ticklabel_format(style='plain', axis='x')

        # Position for the FUS logo
        if overlaid == False:
            image_xaxis, image_yaxis = 0.835, 0.77
        else:
            image_xaxis, image_yaxis = 0.1, 0.77

        image_width, image_height = 0.12, 0.12

        # Add the image to the figure
        ax_image = self.fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])
        ax_image.imshow(image)
        ax_image.axis('off')

        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)

        # Set the canvas to the figure
        self.fig.set_canvas(self.canvas)
        return self.canvas

    
    # NOT YET IMPLEMENTED
    def save_graph(self, folder, overlaid=False):
        # Check if temperature_csv is a list and get the first file path
        if overlaid == True:
            temperature_svg_filename = "multi_batch_histogram"#(Path(self.temperature_csv[0]).name).split(".")[0]
        else:
            temperature_svg_filename = (Path(self.temperature_csv[0]).name).split(".")[0]
        
        full_save_name = os.path.join(folder, str(temperature_svg_filename) + ".svg")

        # Debugging statement
        print(f"Saving graph to: {full_save_name}")
        
        self.fig.savefig(full_save_name, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
        return full_save_name

if __name__ == "__main__":
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt")
    n.get_graphs()
    plt.show()