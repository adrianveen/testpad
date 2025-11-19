from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class CSVGraph:
    """CSV Graph class."""

    def __init__(
        self,
        frequency: float,
        unit: str,
        filename: str,
        save: bool,
        save_folder: str = "",
    ) -> None:
        """Initialize CsvGraph object.

        Args:
            frequency (float): Frequency at which to plot the graph
            unit (str): Unit of the frequency (either "kHz" or "MHz")
            filename (str): Path to the CSV file
            save (bool): Whether to save the graph or not
            save_folder (str): Folder to which to save the graph
                (default is empty string)

        Returns:
            None

        """
        plt.close("all")
        self.selected_freq = float(frequency)
        if unit == "kHz":
            self.selected_freq *= 1e3
        elif unit == "MHz":
            self.selected_freq *= 1e6

        self.filename = filename

        self.save = save

        self.save_folder = save_folder

        # fetch data from csv file
        try:
            lines = np.array(
                pd.read_csv(
                    self.filename, header=0, sep=",", usecols=[1, 7, 9], skiprows=20
                )
            )
        except (FileNotFoundError, pd.errors.ParserError, ValueError) as e:
            print(
                str(e) + "\nWARNING: Unable to open file. Did you select a CSV file?\n"
            )
            return

        self.frequencies = lines[:, 0]
        self.impedances = lines[:, 1]
        self.phases = lines[:, 2]

        # graph impedance
        self.impedance_graph = self.graph(
            self.frequencies,
            self.impedances,
            xlabel="Frequencies (Hz)",
            ylabel="Impedance (Ohms)",
            title="Impedance Magnitude |Z|",
            box_type="Z",
        )

        # graph phase
        self.phase_graph = self.graph(
            self.frequencies,
            self.phases,
            xlabel="Frequencies (Hz)",
            ylabel="Phase Shift (degrees)",
            title="Phase",
            box_type="THETAZ",
        )

        # plt.draw()

    # graphing function
    def graph(
        self,
        x: np.ndarray,
        y: np.ndarray,
        xlabel: str = "",
        ylabel: str = "",
        title: str = "",
        box_type: str = "",
    ) -> FigureCanvas:
        """Graphing function.

        Args:
            x (numpy array): x values for the graph
            y (numpy array): y values for the graph
            xlabel (str): x axis label (default is empty string)
            ylabel (str): y axis label (default is empty string)
            title (str): title of the graph (default is empty string)
            box_type (str): type of box to plot (default is empty string)

        Returns:
            FigureCanvas: canvas object for the graph

        """
        fig, ax = plt.subplots(1, 1)
        canvas = FigureCanvas(fig)

        ax.plot(x, y, "o-", alpha=0.3)

        intersection = np.interp(self.selected_freq, x, y)
        ax.plot(self.selected_freq, intersection, "ro")
        ax.annotate(
            f"[{self.selected_freq / 1e6:0.3f}, {intersection:0.3f}]",
            (self.selected_freq, intersection),
        )

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        if self.save:
            graph_type = (self.filename.split("/")[-1]).split(".")[0]

            save_filename = Path(self.save_folder) / f"{graph_type}_{box_type}.svg"
            print(f"Saving {title} graph to {save_filename}...")
            try:
                fig.savefig(
                    save_filename,
                    bbox_inches="tight",
                    format="svg",
                    pad_inches=0,
                    transparent=True,
                )  # pad_inches = 0 removes need to shrink image in Inkscape
            except OSError as e:
                print(
                    str(e)
                    + "\nWARNING: Unable to save. Did you select a save location?\n"
                )

        fig.set_canvas(canvas)
        return canvas

    # return graphs to UI
    def return_graphs(self) -> tuple[FigureCanvas, FigureCanvas]:
        """Return the impedance and phase graphs as a tuple of FigureCanvas objects.

        Returns:
            tuple[FigureCanvas, FigureCanvas]: impedance graph and phase graph

        """
        return (self.impedance_graph, self.phase_graph)
