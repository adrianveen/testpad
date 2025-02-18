import numpy as np
import os
import sys
import math
import yaml
import decimal
from pathlib import Path

from definitions import SRC_DIR
from PIL import Image
from io import BytesIO

import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter, FuncFormatter, MultipleLocator, MaxNLocator
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
                # Identify columns to drop: those after index 3 whose header doesn't include "Temp"
                cols_to_drop = [col for col in data.columns[4:] if "Temp" not in str(col)]

                # Drop the selected columns
                data = data.drop(columns=cols_to_drop)
                # convert to hh:mm:ss format
                # data['time_str'] = data.iloc[:, 2].apply(
                #     lambda s: f"{s // 3600:02}:{(s % 3600) // 60:02}:{s % 60:02}"
                # )
                # Append processed data to raw_data
                #divide elapsed time by 60 to convert to minutes
                # helper function that tests if a value can be converted to float
                def is_numeric(val):
                    try:
                        float(val)
                        return True
                    except Exception:
                        return False

                # Check numeric validity for the elapsed column
                elapsed_valid = data.iloc[:, 2].apply(is_numeric)
                
                # Check numeric validity for temperature columns (assumed to be index 3 onward)
                temp_valid = data.iloc[:, 3:].applymap(is_numeric)
                # For each row, if any temp column is invalid, mark the row as invalid
                temp_rows_valid = temp_valid.all(axis=1)
                
                # Combine the validity masks for elapsed and temperature columns.
                valid_rows = elapsed_valid & temp_rows_valid
                
                if not valid_rows.all():
                    # Find the first row that is invalid
                    first_invalid_idx = valid_rows.idxmin()  # idxmin returns the first index with False
                    # Drop this row and all rows that follow.
                    data = data.loc[:first_invalid_idx - 1]

                
                elapsed = data.iloc[:, 2] / 60
                # print header for elapsed as f string
                print(f"Elapsed header: {elapsed.head()}")
                temps = data.iloc[:, 3:]
                # print(f"Elapsed: {elapsed}")
                # print(f"Temperature: {temp1}")
                
                self.raw_data.append((elapsed, temps))
                # print(f"Raw data: {self.raw_data}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # print(f"raw data Header: {self.raw_data[0][0].head()}")
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
        # colors = self.generate_color_palette('#73A89E', len(self.raw_data[0][1]))

        # Load the FUS icon
        image_path = self.resource_path('images\\fus_icon_transparent.png')
        image = self.load_icon(image_path)

        if overlaid == False or len(self.raw_data) == 1:
            # Single dataset
            data = self.raw_data[0]
            elapsed = data[0]
            temperatures = data[1]
            # print(f"Elapsed: {elapsed}")
            # print(f"Temperature: {temperature}")
            colors = self.generate_color_palette('#73A89E', len(temperatures.columns))
            for i, sensor in enumerate(temperatures.columns):
                if len(temperatures.columns) == 1:
                    linewidth = 2
                else:
                    linewidth = 1
                self.ax.plot(elapsed, temperatures[sensor], linewidth=linewidth, label=f"Sensor {i+1}", color=colors[i])
            if len(temperatures.columns) > 1:
                legend = self.ax.legend(fontsize=12)
                for line in legend.get_lines():
                    line.set_linewidth(6)
            #self.ax.plot(elapsed, temperature, color='#73A89E', label="Dataset 1", linewidth=2)
        else:
            colors = self.generate_color_palette('#73A89E', len(self.raw_data))
            # Overlaid datasets
            for i, (elapsed, temperature) in enumerate(self.raw_data):
                self.ax.plot(elapsed, temperature, alpha=0.7, label=f'Dataset {i+1}',linewidth=1, color=colors[i]) #  color=colors[i], 
            # legend = self.ax.legend(fontsize=12)
            # for line in legend.get_lines():
            #     line.set_linewidth(6)

        # Graph labels
        self.ax.set_xlabel("Elapsed Time (min)", fontsize=14)
        self.ax.set_ylabel("Temperature (°C)", fontsize=14)
        self.ax.set_title("Temperature vs. Elapsed Time", fontsize=16)
        self.ax.tick_params(axis='both', which='major', labelsize=12)

        # Format x-axis to not use scientific notation
        # self.ax.xaxis.set_major_formatter(ScalarFormatter())
        # self.ax.ticklabel_format(style='plain', axis='x')

        # Replaces the default x-axis formatter with a custom formatter that converts seconds to hh:mm:ss
        # def format_time(x, pos):
        #     # x is in seconds; convert to hh:mm:ss
        #     hours = int(x // 3600)
        #     minutes = int((x % 3600) // 60)
        #     seconds = int(x % 60)
        #     return f"{hours:02}:{minutes:02}:{seconds:02}"

        # self.ax.xaxis.set_major_formatter(FuncFormatter(format_time))
        # After plotting your data and before drawing the canvas:
        x_min, x_max = self.ax.get_xlim()

        n_ticks = math.floor((x_max - x_min) / 5) + 1
        if n_ticks < 6:
            # If there would be fewer than 6 ticks,
            # generate 6 evenly spaced tick locations over the x-range.
            ticks = np.linspace(x_min, x_max, 6)
            self.ax.set_xticks(ticks)
        elif elapsed.max() - elapsed.min() > 60:
            self.ax.xaxis.set_major_locator(MaxNLocator(12))
        else:
            # Otherwise, set ticks every 5 minutes.
            self.ax.xaxis.set_major_locator(MultipleLocator(5))
        # self.ax.tick_params(axis='x', labelrotation=45)

        image_width, image_height = 0.07, 0.07

        # Position for the FUS logo
        if overlaid == False and len(temperatures.columns) == 1:
            image_xaxis, image_yaxis = 0.87, 0.82
                    # Add the image to the figure
            ax_image = self.fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])
            ax_image.imshow(image)
            ax_image.axis('off')

            # legend = self.ax.legend(
            # loc='upper left', 
            # bbox_to_anchor=(image_xaxis, image_yaxis), 
            # fontsize=12
            # )

        else:
            image_xaxis, image_yaxis = 0.10, 0.82
            # set the legend to be below the image
            self.ax.legend(loc='upper right', fontsize=12)
            # Add the image to the figure
            ax_image = self.fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])
            ax_image.imshow(image)
            ax_image.axis('off')
            legend = self.ax.legend(fontsize=12)
            for line in legend.get_lines():
                line.set_linewidth(6)

        
        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)

        # Set the canvas to the figure
        self.fig.set_canvas(self.canvas)
        return self.canvas

    
    # NOT YET IMPLEMENTED
    # def save_graph(self, folder, overlaid=False):
    #     # Check if temperature_csv is a list and get the first file path
    #     if overlaid == True:
    #         temperature_svg_filename = "multi_batch_histogram"#(Path(self.temperature_csv[0]).name).split(".")[0]
    #     else:
    #         temperature_svg_filename = (Path(self.temperature_csv[0]).name).split(".")[0]
        
    #     full_save_name = os.path.join(folder, str(temperature_svg_filename) + ".svg")

    #     # Debugging statement
    #     print(f"Saving graph to: {full_save_name}")
        
    #     self.fig.savefig(full_save_name, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
    #     return full_save_name

if __name__ == "__main__":
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = TemperatureGraph(r"G:\Shared drives\FUS_Team\Bed Temperature Data\RK50_MRIg_temp_test_01_phantom_bed_2025-01-16_T08-55-44.802 (1).csv")
    n.get_graphs()
    plt.show()