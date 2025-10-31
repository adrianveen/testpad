import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import to_hex, to_rgb
from matplotlib.ticker import FormatStrFormatter, MaxNLocator, MultipleLocator
from numpy.typing import NDArray
from PIL import Image


class TemperatureGraph:
    """This class is used to generate graphs of the temperature data."""

    def __init__(self, temperature_csv: str) -> None:
        """Initialize a TemperatureGraph object with a given CSV file.

        Args:
            temperature_csv (str): The path to the temperature CSV file.

        Raises:
            ValueError: If no file is selected (i.e., temperature_csv is None).

        """
        self.temperature_csv = temperature_csv
        self.legend = None
        self.raw_data = []

        # Check if temperature_csv is None
        if temperature_csv is None:
            msg = "No file selected"
            raise ValueError(msg)  # temperature_csv cannot be none
        self.temperature_csv = temperature_csv
        self.raw_data = []

        # Process the file(s) and store the data
        self.raw_data = self._process_files(temperature_csv)

        self.image_path = self._resource_path("resources\\fus_icon_transparent.png")
        self.image = self._load_icon(self.image_path)

    def _resource_path(self, relative_path: str) -> Path:
        """Get the absolute path to a resource."""
        base_path = getattr(sys, "_MEIPASS", Path.cwd())
        return Path(base_path) / relative_path

    # function to load fus_icon_transparent.ico file
    def _load_icon(self, path: Path) -> NDArray:
        image = Image.open(path)
        return np.array(image)

    def _process_files(self, file_paths: list[str]) -> list:
        """Process one or more CSV files and extract relevant data.

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
                cols_to_drop = [
                    col for col in data.columns[4:] if "Temp" not in str(col)
                ]

                # Drop the selected columns
                data = data.drop(columns=cols_to_drop)

                # helper function to check if a value can be converted to float.
                def can_convert_to_float(x) -> bool | None:
                    try:
                        float(x)
                        return True
                    except:
                        return False

                # Combine the relevant columns into one DataFrame for the check.
                relevant_columns = data.columns[2:]
                # Apply the helper function to each cell; this returns a DataFrame of booleans.
                numeric_mask = (
                    data[relevant_columns].map(can_convert_to_float).all(axis=1)
                )

                # If there's any row that isn't fully numeric, drop that row and all rows that follow.
                if not numeric_mask.all():
                    # Find the first row (by index) that is invalid.
                    first_invalid_index = (
                        numeric_mask.idxmin()
                    )  # idxmin returns the index of the first False.
                    # Keep only rows before the first invalid row.
                    data = data.loc[: first_invalid_index - 1]

                # Convert the elapsed column (index 2) to numeric and convert seconds to minutes.
                elapsed = pd.to_numeric(data.iloc[:, 2], errors="coerce") / 60
                # Convert temperature columns (index 3 onward) to numeric.
                temps = data.iloc[:, 3:].apply(pd.to_numeric, errors="coerce")

                self.raw_data.append((elapsed, temps))
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        return self.raw_data

    # Generate a color palette based on the base color provided
    def _generate_color_palette(self, base_color, num_colors: int) -> list[str]:
        """Return a palette."""
        base_rgb = to_rgb(base_color)
        return [
            to_hex(
                (
                    base_rgb[0] * (1 - i / num_colors),
                    base_rgb[1] * (1 - i / num_colors),
                    base_rgb[2] * (1 - i / num_colors),
                )
            )
            for i in range(num_colors)
        ]

    # returns canvas of mpl graph to UI

    def get_graphs(self, overlaid=False):
        """Generate and return a line plot of the temperature over time.

        Args:
            overlaid (bool, optional): If True, multiple line plots will be overlaid.
                Default is False.

        Returns:
            FigureCanvas: The canvas containing the generated plot.

        """
        # Initialize the figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)

        # Generate a color palette based on the number of datasets
        # colors = self.generate_color_palette('#73A89E', len(self.raw_data[0][1]))

        if not overlaid or len(self.raw_data) == 1:
            # Single dataset
            data = self.raw_data[0]
            elapsed = data[0]
            temperatures = data[1]

            colors = self._generate_color_palette("#73A89E", len(temperatures.columns))
            for i, sensor in enumerate(temperatures.columns):
                linewidth = 2 if len(temperatures.columns) == 1 else 1
                self.ax.plot(
                    elapsed,
                    temperatures[sensor],
                    linewidth=linewidth,
                    label=f"Sensor {i + 1}",
                    color=colors[i],
                )

        else:
            colors = self._generate_color_palette("#73A89E", len(self.raw_data))
            # Overlaid datasets
            for i, (elapsed, temperature) in enumerate(self.raw_data):
                self.ax.plot(
                    elapsed,
                    temperature,
                    alpha=0.7,
                    label=f"Dataset {i + 1}",
                    linewidth=1,
                    color=colors[i],
                )  #  color=colors[i],

        # Graph labels
        self.ax.set_xlabel("Elapsed Time (min)", fontsize=14)
        self.ax.set_ylabel("Temperature (°C)", fontsize=14)
        self.ax.set_title("Temperature vs. Elapsed Time", fontsize=16)
        self.ax.tick_params(axis="both", which="major", labelsize=12)

        # After plotting your data and before drawing the canvas:
        _x_min, x_max = self.ax.get_xlim()

        n_ticks = math.floor((x_max - 0) / 5) + 1
        if n_ticks < 6:
            # If there would be fewer than 6 ticks,
            # generate 6 evenly spaced tick locations over the x-range.
            ticks = np.arange(0, 7)
            self.ax.set_xticks(ticks)
        elif elapsed.max() - elapsed.min() > 60:
            self.ax.xaxis.set_major_locator(MaxNLocator(12))
        else:
            # Otherwise, set ticks every 5 minutes.
            self.ax.xaxis.set_major_locator(MultipleLocator(5))

        self.ax.xaxis.set_major_formatter(FormatStrFormatter("%d"))

        if overlaid or len(temperatures.columns) > 1:
            self.legend = self.ax.legend(loc="best", fontsize=12)
            for line in self.legend.get_lines():
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
    n = TemperatureGraph(
        r"G:\Shared drives\FUS_Team\Bed Temperature Data\RK50_MRIg_temp_test_01_phantom\
            _bed_2025-01-16_T08-55-44.802 (1).csv"
    )
    n.get_graphs()
    plt.show()
