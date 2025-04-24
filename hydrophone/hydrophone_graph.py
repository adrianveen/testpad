import numpy as np
import os
import sys

from PIL import Image
from io import StringIO
import pandas as pd

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

    def _process_files(self, file_paths):
        """
        Process one or more CSV files and extract relevant data.

        Args:
            file_paths (str or list of str): Single file path or a list of file paths.

        Returns:
            list: A list of tuples, where each tuple contains (frequency, sensitivity)
                if the STD column is missing or (frequency, sensitivity, std) if present.
        """

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
    
    # returns canvas of mpl graph to UI
    def get_graphs(self, mode: str = "single"):
        """
        Generate and return a line plot of the temperature over time.

        Args:
            overlaid (bool, optional): If True, multiple line plots will be overlaid. Default is False.
        Returns:
            FigureCanvas: The canvas containing the generated plot.
        """
        """mode: 'single', 'overlaid', or 'append'"""
        self._prepare_figure()        # pull out your fig/ax setup
        if mode == "append":
            self._plot_appended()
        elif mode == "overlaid":
            self._plot_overlaid()
        elif mode == "single":
            self._plot_single()
        else:
            raise ValueError(f"Unknown mode {mode!r}")
        return self.canvas
        # Initialize the figure and canvas
    def _prepare_figure(self):
            # common figure/canvas setup
            self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(10, 6))
            self.canvas = FigureCanvas(self.fig)
            # load logo
            img = Image.open(self.resource_path("images/fus_icon_transparent.png"))
            self.fus_icon = np.array(img)
            # styling
            self.ax.xaxis.set_major_locator(MultipleLocator(0.2))
            self.ax.xaxis.set_major_formatter(ScalarFormatter())
            self.ax.ticklabel_format(style="plain", axis="x")
            self.ax.grid(True, color="#dddddd")

            self.fig.subplots_adjust(top=0.88, right=0.94, left=0.08, bottom=0.10)

    def _finalize_plot(self, title: str):
        self.ax.set_title(title)
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("Sensitivity (V/MPa)")
        # insert logo
        ax_image = self.fig.add_axes([0.85, 0.75, 0.12, 0.12])
        ax_image.imshow(self.fus_icon)
        ax_image.axis("off")

    def _plot_single(self):
        freq, sens, *rest = self.raw_data[0]
        self.ax.plot(
            freq, sens / 1000,
            linestyle='-', marker='o',
            color='black',
            markerfacecolor='#73A89E',
            markeredgecolor='black',
            linewidth=2, markersize=8,
            label="Dataset"
        )
        half = max(sens) / 2 / 1000
        line = self.ax.axhline(y=half, linestyle='--', color='#3b5e58')
        line.set_dashes([10, 5])
        self._finalize_plot("Hydrophone Sensitivity")

    def _plot_overlaid(self):
        colors = self.generate_color_palette('#73A89E', len(self.raw_data))
        for i, data in enumerate(self.raw_data):
            freq, sens, *rest = data
            self.ax.plot(
                freq, sens / 1000,
                linestyle='-', marker='o',
                color='black',
                markerfacecolor=colors[i],
                markeredgecolor='black',
                alpha=0.7,
                label=f"Dataset {i+1}",
                linewidth=1, markersize=8
            )
        self.ax.legend()
        self._finalize_plot("Hydrophone Sensitivity (Overlaid)")

    def _plot_appended(self):
        # build one big DF
        dfs = []
        for freq, sens, *rest in self.raw_data:
            df = pd.DataFrame({'freq': freq, 'sens': sens})
            dfs.append(df)
        big = pd.concat(dfs, ignore_index=True).sort_values('freq')
        self.ax.plot(
            big['freq'], big['sens']/1000,
            linestyle='-', marker='o',
            color='black',
            markerfacecolor='#73A89E',
            markeredgecolor='black',
            linewidth=2, markersize=8,
            label="Combined"
        )
        half = big['sens'].max() / 2 / 1000
        line = self.ax.axhline(y=half, linestyle='--', color='#3b5e58')
        line.set_dashes([10, 5])
        self._finalize_plot("Hydrophone Sensitivity (Combined)")

        # Generate a color palette based on the base color provided
    def generate_color_palette(self, base_color, num_colors):
        base_rgb = to_rgb(base_color)
        palette = [to_hex((base_rgb[0] * (1 - i / num_colors), 
                           base_rgb[1] * (1 - i / num_colors), 
                           base_rgb[2] * (1 - i / num_colors))) for i in range(num_colors)]
        return palette
    
    def resource_path(self, relative_path):
        """Get the absolute path to a resource"""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)
    
    # function to load fus_icon_transparent.ico file
    def load_icon(self, path):
        image = Image.open(path)
        image_array = np.array(image)
        return image_array


if __name__ == "__main__":
    n = HydrophoneGraph(r"G:\Shared drives\FUS_Team\Hydrophone Characterization\2025-02-24-13-39-10_613-T550H825_transducer_hydrophone_calibration.csv")
    n.get_graphs()
    plt.show()