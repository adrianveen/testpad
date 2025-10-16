from typing import Sequence, Optional
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from testpad.utils.plot_config import (
    PRIMARY_COLOR, 
    GRID_ENABLED, 
    GRID_ALPHA,
    GRID_LINE_STYLE,
    GRID_LINE_WIDTH,
    DEFAULT_MARKER,
    DEFAULT_MARKER_SIZE
) 
from PySide6.QtWidgets import QWidget, QVBoxLayout

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
        ) -> Figure:
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

        if self._canvas:
            self._canvas.draw()

