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


def gaussian_kernel(size: int, sigma: float = 1.0) -> NDArray[np.float64]:
    """Generate a gaussian kernal for convolution filtering."""
    kernel = np.exp(-(np.linspace(-sigma, sigma, size) ** 2))
    return kernel / kernel.sum()  # Normalize the kernel so the sum is 1


class NanobubblesGraph:
    """NanobubblesGraph class."""

    def __init__(self, nanobubble_txt: str | list[str], data_selection: str) -> None:
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
                self._process_file(file)
        else:
            self._process_file(nanobubble_txt)

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

    def _process_file(self, file: str) -> None:
        if file is None:
            msg = "No file selected"
            raise ValueError(msg)  # File cannot be None

        with Path(file).open() as f:
            lines = f.readlines()

        drop_lines_index = 0

        for i, line in enumerate(lines):
            if line.lstrip().startswith("-1"):
                drop_lines_index = i + 1
                break

        remaining_lines = lines[drop_lines_index:]

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

    # Generate a color palette based on the base color provided
    def _generate_color_palette(self, base_color: str, num_colors: int) -> list[str]:
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
        ]  # Returns a palette of colors

    # returns canvas of mpl graph to UIapply_convolution_filter

    def get_graphs(
        self,
        bins: int | NDArray[np.int_],
        scale: bool,
        overlaid: bool = False,
        data_selection: str = "",
        apply_convolution_filter: bool = False,
        convolution_size: int = 3,
    ) -> FigureCanvas:
        """Generate and return a histogram plot of nanobubble size distributions.

        Args:
            bins (int | NDArray[np.int_]): The number of bins to use for the histogram
                If scale is True, this will determine the number of bins.
            scale (bool): If True, the x-axis will be in log scale; otherwise,
                it will be in linear scale.
            overlaid (bool, optional): If True, multiple histograms will be overlaid.
                Default is False.
            data_selection (str, optional): The type of data to plot. Valid options
            apply_convolution_filter (bool, optional): If True, a Gaussian convolution
                filter will be applied to the data. Default is False.
            convolution_size (int, optional): The size of the Gaussian convolution
                filter. Default is 3.

        Returns:
            FigureCanvas: The canvas containing the generated plot.

        """
        # clear plot
        plt.close("all")
        self.fig, self.ax = plt.subplots(1, 1)
        self.canvas = FigureCanvas(self.fig)
        # Generate a color palette based on the base color (FUS Green)
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
            else:
                msg = f"Invalid data_selection: {data_selection}"
                raise ValueError(msg)

            if apply_convolution_filter:
                y = np.convolve(
                    y, gaussian_kernel(convolution_size, sigma=1.0), mode="same"
                )

            # print middle rows of y
            # print(y[100:110])

            # Validate that `data` is a 2D array with two columns
            # if data.ndim != 2 or data.shape[1] != 2:
            #     raise ValueError(
            #         f"`self.raw_data[0]` is not a valid 2D array. "
            #         f"Current shape: {data.shape}"
            #     )
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
            for i, data in enumerate(self.raw_data):
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
                else:
                    msg = f"Invalid data_selection: {data_selection}"
                    raise ValueError(msg)

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
    def save_graph(self, folder: str, overlaid: bool = False) -> Path:
        # Check if nanobubble_txt is a list and get the first file path
        if overlaid:
            nanobubble_svg_filename = "multi_batch_histogram"
        else:
            nanobubble_svg_filename = (Path(self.nanobubble_txt[0]).name).split(".")[0]

        # full_save_name = os.path.join(folder, str(nanobubble_svg_filename) + ".svg")
        full_save_name = Path(folder) / f"{nanobubble_svg_filename}.svg"

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
    # Example paths:
    # n = NanobubblesGraph(
    #     r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS 2.txt", ""
    # )
    # n = NanobubblesGraph(
    #     r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-1st-FUS.txt", ""
    # )
    # n = NanobubblesGraph(
    #     r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS 2.txt", ""
    # )
    n = NanobubblesGraph(r"G:\Shared drives\FUS_Team\IY NanoBubbles\IY-2nd-FUS.txt", "")
    n.get_graphs(bins=100, overlaid=True, scale=True)
    plt.show()
