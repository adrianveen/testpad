import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class MatplotlibWidget(FigureCanvas):
    def __init__(self, parent=None):
        fig, ax = plt.subplots(figsize=(8, 6))
        super().__init__(fig)
        self.ax = ax

        # Create random data for plot
        x = np.linspace(0, 10, 55000)
        y = np.sin(x)

        # Plot the data
        self.ax.plot(x, y, label='sin(x)')
        self.ax.plot(x, np.cos(x), label='cos(x)')
        self.legend = self.ax.legend(loc='best')

        # Load the image
        self.img = mpimg.imread(r'C:\Users\Adrian\Documents\fus_instruments_repos\summer_2024\testpad\images\fus_icon_transparent.png')

        # Add a widget for the image (hidden initially)
        self.image_ax = None

    def resizeEvent(self, event):
        """Recalculate the position of the image when the window is resized."""
        super().resizeEvent(event)
        self.update_image_position()

    def update_image_position(self):
        """Update the image's position and size based on the legend's height and direction."""
        if self.image_ax:
            self.image_ax.remove()

        # Get the legend's position and size
        legend_bbox = self.legend.get_window_extent()
        fig_bbox = self.figure.transFigure.inverted().transform(legend_bbox)

        # Get the position and size in figure coordinates
        x_position, y_position = fig_bbox[0][0], fig_bbox[0][1]

        # Use the height of the legend for the image's height
        legend_height = legend_bbox.height  # In pixels
        image_width = legend_height  # Make image width proportional to legend height
        image_height = legend_height  # Fixed size based on the legend height

        # Determine whether the legend is on the left or right side of the figure
        shift_x = (legend_bbox.width/self.figure.bbox.width) * 1.1
        if x_position > 0.5:
            # Move the image to the left side if the legend is on the right
            shift_x = - (legend_bbox.width/self.figure.bbox.width) * 0.6 # A small offset to the left

        # Add new axes for the image (positioned relative to the legend)
        self.image_ax = self.figure.add_axes([x_position + shift_x, y_position, image_width / self.figure.bbox.width,
                                              image_height / self.figure.bbox.height])

        # Display the image
        self.image_ax.imshow(self.img)
        self.image_ax.axis('off')  # Hide the axes

        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Matplotlib with Image and Legend')

        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        self.matplotlib_widget = MatplotlibWidget()
        self.layout.addWidget(self.matplotlib_widget)

        self.setCentralWidget(self.main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())