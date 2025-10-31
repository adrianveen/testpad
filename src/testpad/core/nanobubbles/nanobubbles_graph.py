import os
import sys
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import to_hex, to_rgb
from matplotlib.ticker import ScalarFormatter
from numpy.typing import NDArray
from PIL import Image


def gaussian_kernel(size, sigma=1.0) -> float:
    """Generate a gaussian kernal for convolution filtering."""
    kernel = np.exp(-(np.linspace(-sigma, sigma, size) ** 2))
    return kernel / kernel.sum()  # Normalize the kernel so the sum is 1


class NanobubblesGraph:
    """NanobubblesGraph class."""

    def __init__(self, nanobubble_txt, data_selection: str) -> None:
        """Initialize the NanobubblesGraph class."""
        self.nanobubble_txt = nanobubble_txt
        self.raw_data = []
        self.data_selection = data_selection
        # initiate empty dataframe
        self.data = pd.DataFrame()
        # Check if nanobubble_txt is None
        if nanobubble_txt is None:
            msg = "No file selected"
            raise ValueError(msg)  # nanobubble_txt cannot be none

        # Process each file if nanobubble_txt is a list
        if isinstance(nanobubble_txt, list):
            for file in nanobubble_txt:
                self._process_file(file, data_selection)
        else:
            self._process_file(nanobubble_txt, data_selection)

    def resource_path(self, relative_path: str) -> str:
        """Get the absolute path to a resource."""
        base_path = getattr(sys, "_MEIPASS", Path.cwd())
        return str(Path(base_path) / relative_path)

    # function to load fus_icon_transparent.ico file
    def load_icon(self, path: str) -> NDArray:
        """Load an icon from the given path and return it as a numpy array.

        Args:
            path (str): The path to the icon file.

        Returns:
            NDArray: A numpy array representing the icon image.

        """
        image = Image.open(path)
        return np.array(image)

    def _process_file(self, file, data_selection) -> None:
        if file is None:
            msg = "No file selected"
            raise ValueError(msg)  # File cannot be None

        # OLD APPROACH
        # try:
        #     # Read the file, setting row 89 as the header and skipping rows 90 to 290
        #     data = pd.read_csv(
        #         file,
        #         delimiter="\t",
        #         encoding="utf-8",
        #         header=88  # Row 89 is the header; 0-indexed
        #     )
        # except UnicodeDecodeError:
        #     # Fallback to latin1 encoding if utf-8 fails
        #     data = pd.read_csv(
        #         file,
        #         delimiter="\t",
        #         encoding="latin1",
        #         header=88
        #     )
        with open(file, "r") as f:
            lines = f.readlines()

        drop_lines_index = 0

        for i, line in enumerate(lines):
            if line.lstrip().startswith("-1"):
                drop_lines_index = i + 1
                break

        remaining_lines = lines[drop_lines_index:]

        # OLD APPROACH
        # Identify the first row index where "Size / nm" is negative
        # negative_index = data[data["Size / nm"] < 0].index.min()

        # If a negative value exists, drop all rows up to and including that row
        # if not np.isnan(negative_index):  # Check if a negative value was found
        # data = data.iloc[negative_index + 1:]  # Remove rows up to and including the negative value row

        # DEBUGGING
        # print statements to confirm array matches data
        # print(f"First row of data: {data.iloc[0]}")
        # print(f"Last row of data: {data.iloc[-1]}")

        # OLD APPROACH
        # Ensure we have the required columns
        # required_columns = ["Size / nm", "Number"]
        # if not all(col in data.columns for col in required_columns):
        #     raise ValueError(f"Missing required columns: {required_columns}")
        # data = data[required_columns]
        col_names = [
            "Size / nm",
            "Number",
            "Concentration / cm-3",
            "Volume / nm^3",
            "Area / nm^2",
        ]

        data_str = "".join(remaining_lines)

        data_io = StringIO(data_str)

        self.data = pd.read_csv(data_io, sep="\t", header=None, names=col_names)
        # self.set_data_selection(data_selection, self.data)
        # self.raw_data.append(self.data)

    # def set_data_selection(self, data_selection, data):
    #     self.raw_data = []
    #     if data_selection == "Size Distribution":
    #         # Filter rows based on conditions
    #         filtered = data[(data["Size / nm"] >= 0) & (data["Number"] >= 0)]
    #         # Select the first (index 0) and second (index 1) columns
    #         data = filtered.iloc[:, [0, 1]]
    #         data_array = data.to_numpy()

    #     elif data_selection == "Concentration Per mL":
    #         filtered = data[(data["Size / nm"] >= 0) & (data["Concentration / cm-3"] >= 0)]
    #         # Select the first (index 0) and third (index 2) columns
    #         data = filtered.iloc[:, [0, 2]]
    #         data_array = data.to_numpy()

    #     if data_array.size == 0:
    #         raise ValueError("Filtered data is empty. Ensure the input file has valid values.")

    #     self.raw_data.append(data_array)

    # Generate a color palette based on the base color provided
    def _generate_color_palette(self, base_color: str, num_colors: int) -> list[str]:
        base_rgb = to_rgb(base_color)
        palette = [
            to_hex(
                (
                    base_rgb[0] * (1 - i / num_colors),
                    base_rgb[1] * (1 - i / num_colors),
                    base_rgb[2] * (1 - i / num_colors),
                )
            )
            for i in range(num_colors)
        ]
        return palette

    # returns canvas of mpl graph to UIapply_convolution_filter

    def get_graphs(
        self,
        bins,
        scale,
        normalize=False,
        overlaid=False,
        data_selection=None,
        apply_convolution_filter=False,
        convolution_size=3,
    ) -> FigureCanvas:
        """Generate and return a histogram plot of nanobubble size distributions.

        Args:
            bin_width (int): The width of each bin in the histogram. If log scale is
                selected, this will determine the number of bins.
            scale (bool): If True, the x-axis will be in log scale; otherwise,
                it will be in linear scale.
            normalize (bool, optional): If True, the histogram will be normalized.
                Default is False.
            overlaid (bool, optional): If True, multiple histograms will be overlaid.
                Default is False.

        Returns:
            FigureCanvas: The canvas containing the generated plot.

        """
        # clear plot
        plt.close("all")
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)
        # Generate a color palette based on the base color (FUS Green)
        colors = self._generate_color_palette("#73A89E", len(self.raw_data))
        # load fus_icon png and conver to np array
        image_path = self.resource_path("resources\\fus_icon_transparent.png")
        image = self.load_icon(image_path)

        # if scale = log, set x-axis to log scale from 1-1000
        if scale:
            self.ax.set_xscale("log")
            self.ax.set_xlim(1, 10000)
            bins = np.logspace(np.log10(1), np.log10(10000), num=int(bins))
        else:
            # Linear scale: use linear bins
            bins = np.arange(0, 1000 + bins, bins)

        if not overlaid or len(self.data) == 1:
            # Retrieve the first dataset
            data = self.data  # self.raw_data[0]
            np_data = self.data.to_numpy()
            if data_selection == "Size Distribution":
                x = np_data[:, 0]  # first column
                y = np_data[:, 1]  # second column
            elif data_selection == "Concentration Per mL":
                x = np_data[:, 0]  # first column
                y = np_data[:, 2]  # third column

            if apply_convolution_filter:
                y = np.convolve(
                    y, gaussian_kernel(convolution_size, sigma=1.0), mode="same"
                )

            # print middle rows of y
            # print(y[100:110])

            # Validate that `data` is a 2D array with two columns
            # if data.ndim != 2 or data.shape[1] != 2:
            #     raise ValueError(f"`self.raw_data[0]` is not a valid 2D array. Current shape: {data.shape}")
            # Create a giant array where each size is repeated 'count' times
            # sizes = np.repeat(data[:, 0], data[:, 1].astype(int))

            bar_widths = np.diff(np_data[:, 0])

            # Append an extrapolated width at the end.
            bar_widths = np.append(
                bar_widths, bar_widths[-1] * bar_widths[-1] / bar_widths[-2]
            )
            # Plot the histogram
            self.ax.bar(x, y, width=bar_widths, align="edge", color="#73A89E")

        elif overlaid:
            # Plot multiple overlaid and translucent histograms
            for i, data in enumerate(self.data):
                data = self.data
                np_data = data.to_numpy()

                if data_selection == "Size Distribution":
                    # sizes = np.repeat(data[:, 0], data[:, 1].astype(int))
                    x = np_data[:, 0]
                    y = np_data[:, 1]
                    print(y[100:110])
                elif data_selection == "Concentration Per mL":
                    x = np_data[:, 0]
                    y = np_data[:, 2]
                    print(y[100:110])
                bar_widths = np.diff(np_data[:, 0])
                bar_widths = np.append(
                    bar_widths, bar_widths[-1] * bar_widths[-1] / bar_widths[-2]
                )
                self.ax.bar(
                    x,
                    y,
                    width=bar_widths,
                    align="edge",
                    alpha=0.5,
                    label=f"Batch {i + 1}",
                )
            self.ax.legend(fontsize=14)

        # single histogram
        # self.ax.hist(self.raw_data[0], bins=bins, color='#73A89E', rwidth=0.95)

        # graph labels
        if data_selection == "Size Distribution":
            self.ax.set_xlabel("Diameter [nm]", fontsize=16)
            self.ax.set_ylabel("Count", fontsize=16)  # optional y axis label
            self.ax.set_title("Nanobubble Size Distribution", fontsize=18)
            self.ax.tick_params(axis="both", which="major", labelsize=14)
        elif data_selection == "Concentration Per mL":
            self.ax.set_xlabel("Diameter [nm]", fontsize=16)
            self.ax.set_ylabel("Particles / mL", fontsize=16)
            self.ax.set_title("Nanobubble Concentration", fontsize=18)
            self.ax.tick_params(axis="both", which="major", labelsize=14)
        # formatting x-axis to not be in scientific notation
        self.ax.xaxis.set_major_formatter(ScalarFormatter())
        self.ax.ticklabel_format(style="plain", axis="x")

        if not overlaid or len(self.raw_data) == 1:
            # Define the position and size parameters
            image_xaxis = 0.835
            image_yaxis = 0.82
        else:
            image_xaxis = 0.1
            image_yaxis = 0.82

        image_width = 0.12
        image_height = 0.12  # Same as width since our logo is a square

        # Define the position for the image axes
        ax_image = self.fig.add_axes(
            (image_xaxis, image_yaxis, image_width, image_height)
        )

        # Display the image
        ax_image.imshow(image)
        ax_image.axis("off")  # Remove axis of the image

        # Adjust padding to reduce white space
        self.fig.subplots_adjust(left=0.11, right=0.95, top=0.95, bottom=0.08)

        self.fig.set_canvas(self.canvas)
        return self.canvas

    # save the canvas graph as a SVG
    def save_graph(self, folder, overlaid: bool = False):
        # Check if nanobubble_txt is a list and get the first file path
        if overlaid:
            nanobubble_svg_filename = "multi_batch_histogram"
        else:
            nanobubble_svg_filename = (Path(self.nanobubble_txt[0]).name).split(".")[0]

        # full_save_name = os.path.join(folder, str(nanobubble_svg_filename) + ".svg")  # noqa: ERA001
        full_save_name = Path(folder) / str(nanobubble_svg_filename) / ".svg"

        # Debugging statement
        print(f"Saving graph to: {full_save_name}")

        self.fig.savefig(
            full_save_name,
            format="svg",
            bbox_inches="tight",
            pad_inches=0,
            transparent=True,
        )
        return full_save_name


if __name__ == "__main__":
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt")
    # n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt")
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt", "")
    n.get_graphs(bins=100, overlaid=True)
    plt.show()
