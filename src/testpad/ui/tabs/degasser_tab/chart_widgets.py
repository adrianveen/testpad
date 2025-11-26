from collections.abc import Sequence
from typing import TYPE_CHECKING

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QResizeEvent

from testpad.ui.tabs.degasser_tab.plotting import plot_time_series_on_axis


class TimeSeriesChartWidget(QWidget):
    """A QWidget that contains a Matplotlib time series plot."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the time series chart widget."""
        super().__init__(parent)

        # Create Matplotlib components
        self._figure = Figure(figsize=(5, 3), layout="constrained")
        self._ax = self._figure.add_subplot(111)
        self._canvas = FigureCanvas(self._figure)
        # Set default x axis limit to 0-10 minutes
        self._ax.set_xlim(left=0, right=10)

        # Timer for debouncing resize events
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(100)  # 100ms debounce
        self._resize_timer.timeout.connect(self._on_resize_timeout)

        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas)

    def resizeEvent(self, event: "QResizeEvent") -> None:
        """Handle resize events with debouncing for performance.

        Disables the expensive 'constrained' layout engine during active resizing
        and re-enables it after the user stops resizing.
        """
        # Disable constrained layout during active resizing
        self._figure.set_layout_engine("none")

        # Restart the timer (debounce)
        self._resize_timer.start()

        super().resizeEvent(event)

    def _on_resize_timeout(self) -> None:
        """Re-enable constrained layout and redraw after resizing stops."""
        self._figure.set_layout_engine("constrained")
        self._canvas.draw()

    def update_plot(
        self, measurements: Sequence[tuple[int, float]], temperature_c: float | None
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
        self._canvas.draw()
