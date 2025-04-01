import numpy as np
import os
import sys

from PIL import Image
from io import StringIO

import matplotlib.pyplot as plt 
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.colors import to_rgb, to_hex
from matplotlib.backends.backend_qtagg import FigureCanvas
import matplotlib.transforms as transforms
import pandas as pd


class HydrophoneGraph():
    def __init__(self, hydrophone_csv) -> None:
        
        self.hydrophone_csv = hydrophone_csv
        self.raw_data = []
        self.transducer_serials = []
        
        # Check if hydrophone_csv is None
        if hydrophone_csv is None:
            raise ValueError("No file selected") # hydrophone_csv cannot be none

        # Process the file(s) and store the data
        self.raw_data = self._process_files(hydrophone_csv)
    
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
            list: A list of tuples, where each tuple contains (frequency, sensitivity)
                if the STD column is missing or (frequency, sensitivity, std) if present.
        """
        import pandas as pd
        from io import StringIO

        self.raw_data = []  # Reset raw_data for new files
        self.transducer_serials = []

        # Ensure file_paths is always a list
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        for file_path in file_paths:
            try:
                # Open the file and read all lines at once
                with open(file_path, 'r') as f:
                    lines = f.read().splitlines()
                
                # Validate that the file contains at least two lines for header extraction
                if len(lines) < 2:
                    raise ValueError("File does not contain enough header lines.")
                
                # The first two lines: first_line and tx_serial_line (for serial extraction)
                first_line = lines[0]
                tx_serial_line = lines[1]
                
                # Extract the serial number from the second line
                cells = tx_serial_line.strip().split(',')
                if len(cells) < 2:
                    raise ValueError("Serial number extraction failed: insufficient data in line.")
                tx_serial_no = cells[1]
                self.tx_serial_no = tx_serial_no  # Optionally store as an attribute
                self.transducer_serials.append(tx_serial_no)
                
                # Locate the header row using a generator expression
                header_index = next((i for i, line in enumerate(lines) if "Frequency (MHz)" in line), None)
                if header_index is None:
                    raise ValueError("Could not find 'Frequency (MHz)' in the file.")
                
                # Build the CSV string starting at the header row
                csv_string = "\n".join(lines[header_index:])
                
                # Read CSV data; only consider the expected columns
                data = pd.read_csv(StringIO(csv_string),
                                usecols=lambda col: col in ["Frequency (MHz)", 
                                                            "Sensitivity (mV/MPa)", 
                                                            "Standard deviation (mV/MPa)"])
                
                # Extract columns
                frequency = data["Frequency (MHz)"]
                sensitivity = data["Sensitivity (mV/MPa)"]
                
                # Append the data based on whether the STD column is present
                if "Standard deviation (mV/MPa)" not in data.columns:
                    self.raw_data.append((frequency, sensitivity))
                else:
                    std = data["Standard deviation (mV/MPa)"]
                    self.raw_data.append((frequency, sensitivity, std))
            
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

        blended_transform = transforms.blended_transform_factory(self.ax.transAxes,
                                                self.ax.transData)

        # print(f"Raw data shape: {len(self.raw_data)}")
        # find the max sensitivity value
        max_sensitivity = 0
        for dataset in self.raw_data:
            if len(dataset) == 2:
                freq, sensitivity = dataset
            else:
                freq, sensitivity, sens_std = dataset
            max_sensitivity = max(max_sensitivity, max(sensitivity))

        half_max_sensitivity = max_sensitivity / 2

        if overlaid == False or len(self.raw_data) == 1:
            # Single dataset
            dataset = self.raw_data[0]
            if len(dataset) == 2:
                freq, sensitivity = dataset
            else:
                freq, sensitivity, sens_std = dataset
            # print(f"Frequency: {freq}")
            # print(f"Sensitivity: {sensitivity}")
            self.ax.plot(
                freq, sensitivity / 1000,
                linestyle='-', marker='o',
                color='black',               # Line color (black)
                markerfacecolor='#73A89E',    # Marker fill color
                markeredgecolor='black',      # Marker border (edge) color
                label="Dataset 1", linewidth=2,
                markersize=8
            )
            self.ax.set_title(f"Hydrophone Sensitivity as a Function of Frequency")
            line_y = half_max_sensitivity /1000
            line = self.ax.axhline(y=line_y, color='#3b5e58', linestyle='--')
            line.set_dashes([10, 5])
        else:
            # Overlaid datasets
            for i, dataset in enumerate(self.raw_data):
                if len(dataset) == 2:
                    freq, sensitivity = dataset
                    sens_std = None
                else:
                    freq, sensitivity, sens_std = dataset

                self.ax.plot(
                    freq, sensitivity / 1000,
                    linestyle='-', marker='o',
                    color='black',              # Line color (black)
                    markerfacecolor=colors[i],   # Dataset-specific marker fill
                    markeredgecolor='black',     # Marker border color
                    alpha=0.7, 
                    label=self.transducer_serials[i],
                    linewidth=1, markersize=8
                )
                self.ax.set_title(f"Hydrophone Sensitivity as a Function of Frequency")
                # dashed horizontal line at half max sensitivity
            self.ax.legend()

        # Graph labels
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("Sensitivity (V/MPa)")
        self.ax.tick_params(axis='both', which='major')
        self.ax.xaxis.set_major_locator(MultipleLocator(0.2))
        self.fig.set_size_inches(6.5, 3.5, forward=True)

        # Format x-axis to not use scientific notation
        self.ax.xaxis.set_major_formatter(ScalarFormatter())
        self.ax.ticklabel_format(style='plain', axis='x')
        self.ax.plot(0, 0, alpha=0, label='_nolegend_')
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.grid(True, color='#dddddd')
        
        # Position for the FUS logo
        if overlaid == False or len(self.raw_data) == 1:
            image_xaxis, image_yaxis = 0.84, 0.77
        else:
            image_xaxis, image_yaxis = 0.11, 0.77

        image_width, image_height = 0.12, 0.12

        # Add the FUS logo to the figure
        ax_image = self.fig.add_axes([image_xaxis, image_yaxis, image_width, image_height])
        ax_image.imshow(image)
        ax_image.axis('off')

        # Adjust padding to reduce white space
        self.fig.tight_layout()
        # Set the canvas to the figure
        self.fig.set_canvas(self.canvas)
        return self.canvas

if __name__ == "__main__":
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = TemperatureGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = HydrophoneGraph(r"G:\Shared drives\FUS_Team\Hydrophone Characterization\2025-02-24-13-39-10_613-T550H825_transducer_hydrophone_calibration.csv")
    n.get_graphs()
    plt.show()