from typing import Sequence, Optional
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from testpad.config.plotting import (
    GRID_ALPHA,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH
) 
from PySide6.QtWidgets import QWidget, QVBoxLayout
from testpad.ui.tabs.degasser_tab.plotting import make_time_series_figure

class TimeSeriesChartWidget(QWidget):
    """A QWidget that contains a Matplotlib time series plot."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Matplotlib components
        self._figure = Figure(figsize=(5, 3), tight_layout=True)
        self._ax = self._figure.add_subplot(111)
        self._canvas = FigureCanvas(self._figure)

        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas)

    def update_plot(
            self,
            measurements: Sequence[tuple[int, float]],
            temperature_c: Optional[float]
        ) -> None:
        """Build a matplotlib Figure for the time series data.
        
        Args:
            measurements: Sequence of (minute, oxygen_level) tuples.
            temperature_c: Optional temperature in Celsius to display in title.
        """
        # Create figure using pure plotting function
        figure = make_time_series_figure(
            data=measurements,
            temperature_c=temperature_c,
            size_inches=(5, 3),  # UI size
            dpi=self._figure.get_dpi()
        )
        
        # Update our internal figure with the new one
        self._figure.clear()
        self._ax = self._figure.add_subplot(111)
        
        # Copy the plot from the generated figure
        new_ax = figure.get_axes()[0]
        for line in new_ax.get_lines():
            self._ax.plot(line.get_xdata(), line.get_ydata(), 
                        color=line.get_color(),
                        marker=line.get_marker(),
                        markersize=line.get_markersize(),
                        linestyle=line.get_linestyle(),
                        linewidth=line.get_linewidth(),
                        label=line.get_label())
        
        # Copy title and labels
        self._ax.set_title(new_ax.get_title())
        self._ax.set_xlabel(new_ax.get_xlabel())
        self._ax.set_ylabel(new_ax.get_ylabel())
        
        # Copy grid settings
        self._ax.grid(new_ax.grid(), alpha=GRID_ALPHA, linestyle=GRID_LINE_STYLE, linewidth=GRID_LINE_WIDTH)
        
        # Clean up the temporary figure
        import matplotlib.pyplot as plt
        plt.close(figure)
        
        self._canvas.draw()

    def get_pdf_figure(self, data, temp: Optional[float]) -> tuple[FigureCanvas, Path]:
        """Returns the Matplotlib FigureCanvas and saves a temporary PNG file.

        Returns:
            A tuple containing the FigureCanvas and the Path to the saved PNG file.
        """        
        # Convert data to the expected format
        if hasattr(data, "items"):
            # It's a dict-like object - ensure keys are integers for proper sorting
            pairs = sorted((int(k), float(v)) for k, v in data.items())
        else:
            # It's already a sequence of tuples - ensure first element is int
            pairs = sorted((int(k), float(v)) for k, v in data)
        
        # Create figure using pure plotting function
        pdf_figure = make_time_series_figure(
            data=pairs,
            temperature_c=temp,
            size_inches=(4, 4),
            dpi=300
        )
        
        # Save to temporary file
        temp_path = Path.cwd() / "temp_plot.png"
        pdf_figure.savefig(temp_path, dpi=300, bbox_inches='tight')
        
        return pdf_figure, temp_path