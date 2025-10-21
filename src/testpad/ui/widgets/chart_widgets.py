from optparse import Option
from turtle import color
from typing import Sequence, Optional, Dict
from pathlib import Path
import time
from copy import deepcopy
from matplotlib import markers
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from testpad.config.plotting import (
    PRIMARY_COLOR, 
    GRID_ENABLED, 
    GRID_ALPHA,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE,
    DEFAULT_LINE_WIDTH,
    DEFAULT_LINE_STYLE
) 
from PySide6.QtWidgets import QWidget, QVBoxLayout

# Import the pure plotting function for consistency
try:
    from testpad.ui.tabs.degasser_tab.plotting import make_time_series_figure
except ImportError:
    # Fallback if the module doesn't exist yet
    make_time_series_figure = None

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
        # clear figure
        self._ax.clear()

        if measurements:
            time, ox_level = zip(*sorted(measurements))
            self._ax.plot(
                time, ox_level, 
                color='k', 
                marker=DEFAULT_MARKER, 
                markersize=DEFAULT_MARKER_SIZE,
                mew=1,
                mec='k',
                mfc=PRIMARY_COLOR,
                linestyle='-',
                linewidth=1.0,
                label='Oxygen Level (mg/L)'
            )
        
        if temperature_c is not None:
            self._ax.set_title(f"Dissolved Oxygen vs Time (Temp: {temperature_c:.1f} °C)")
        else:
            self._ax.set_title("Dissolved Oxygen vs Time")
        
        self._ax.set_xlabel("Time (minutes)")
        self._ax.set_ylabel("Dissolved O2 (mg/L)")

        self._ax.grid(GRID_ENABLED, alpha=GRID_ALPHA, linestyle=GRID_LINE_STYLE, linewidth=GRID_LINE_WIDTH)

        self._canvas.draw()

    def get_pdf_figure(self, data, temp: Optional[float]) -> tuple[FigureCanvas, Path]:
        """Returns the Matplotlib FigureCanvas and saves a temporary PNG file.

        Returns:
            A tuple containing the FigureCanvas and the Path to the saved PNG file.
        """        
        # Use the pure plotting function if available, otherwise fall back to old method
        if make_time_series_figure is not None:
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
        else:
            # Fallback to old method
            return self._get_pdf_figure_legacy(data, temp)
    
    def _get_pdf_figure_legacy(self, data, temp: Optional[float]) -> tuple[FigureCanvas, Path]:
        """Legacy method for creating PDF figure (fallback)."""
        # Create new figure for PDF
        pdf_figure = Figure(figsize=(5, 5), tight_layout=True)
        title = "Dissolved Oxygen vs Time"
        xlabel = "Time (minutes)"
        ylabel = "Dissolved O2 (mg/L)"
        figure = self._create_plot(
            figure=pdf_figure,
            data=data,
            temp=temp,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel
            )
        temp_path = Path.cwd() / "temp_plot.png"
        figure.savefig(temp_path, dpi=300)

        return pdf_figure, temp_path
    
    def _create_plot(
            self,
            figure: Figure,
            data: Dict[int, float],
            temp: Optional[float],
            title: str,
            xlabel: str,
            ylabel: str
            ) -> Figure:
        """Abstracted plotting logic for use by provided figure.
        
        Args:
            figure(Figure): matplotlib Figure
            data()
        """
        ax = figure.add_subplot(111)
        canvas = FigureCanvas(figure)
        ax.clear()

        pairs = sorted(data.items())
        if pairs:
            time_min, ox_level = zip(*pairs)
            ax.plot(
                time_min, ox_level,
                color='k',
                marker=DEFAULT_MARKER,
                markersize=DEFAULT_MARKER_SIZE,
                mew=1,
                mec='k',
                mfc=PRIMARY_COLOR,
                linestyle=DEFAULT_LINE_STYLE,
                linewidth=DEFAULT_LINE_WIDTH
            ) 

        if temp:
            ax.set_title(f"{title} (Temp: {temp:.1f} °C)")
        else:
            ax.set_title(f"{title}")
        
        ax.set_xlabel(f"{xlabel}")
        ax.set_ylabel(f"{ylabel}")

        ax.grid(GRID_ENABLED, alpha=GRID_ALPHA, linestyle=GRID_LINE_STYLE, linewidth=GRID_LINE_WIDTH)

        # canvas.draw()

        return figure