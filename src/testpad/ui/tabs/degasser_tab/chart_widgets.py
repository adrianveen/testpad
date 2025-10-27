from typing import Optional, Sequence

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from testpad.ui.tabs.degasser_tab.plotting import plot_time_series_on_axis


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
        self, measurements: Sequence[tuple[int, float]], temperature_c: Optional[float]
    ) -> None:
        """Update the matplotlib plot with new time series data.

        Args:
            measurements: Sequence of (minute, oxygen_level) tuples.
            temperature_c: Optional temperature in Celsius to display in title.
        """
        # Clear the existing plot
        self._ax.clear()

        # Draw directly on the widget's axis (no temporary figure needed)
        plot_time_series_on_axis(self._ax, measurements, temperature_c)

        # Apply tight layout and redraw
        self._figure.tight_layout()
        self._canvas.draw()
