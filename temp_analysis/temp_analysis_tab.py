
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from temp_analysis.temperature_graph import TemperatureGraph


class TempAnalysisTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.temperature_data_files = None
        self.file_save_location = None
        self.temperature_object = None
        self.image_ax = None
        self.img = []

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # compare checkbox
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setChecked(False)
        # select file button
        self.select_file_btn = QPushButton("SELECT TEMPERATURE CSV FILE(S)")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("csv"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #66A366; color: black;")
        self.print_graph_btn.clicked.connect(lambda: self.create_graph())

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.compare_label, 0, 0)
        selections_layout.addWidget(self.compare_box, 0, 1)
        selections_layout.addWidget(self.select_file_btn, 1, 0, 1, 2)
        selections_layout.addWidget(self.print_graph_btn, 2, 0, 1, 2)
        buttons_groupbox.setLayout(selections_layout)

        # TEXT CONSOLE
        self.text_display = QTextBrowser()

        # GRAPH DISPLAY 
        self.graph_tab = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_tab, 0, 1, 2, 1)
        self.setLayout(main_layout)
    
    def resizeEvent(self, event):
        """Recalculate the position of the image when the window is resized."""
        super().resizeEvent(event)
        self.update_image_position()

    def update_image_position(self):
        """Update the image's position and size based on the legend's height and direction."""
        if self.temperature_object is None:
            return
        
        self.img = self.temperature_object.image

        if self.image_ax:
            self.image_ax.remove()

        if self.temperature_object.legend is not None:
            # Get the legend's position and size
            legend_bbox = self.temperature_object.legend.get_window_extent()
            fig_bbox = self.temperature_object.fig.transFigure.inverted().transform(legend_bbox)

            # Get the position and size in figure coordinates
            x_position, y_position = fig_bbox[0][0], fig_bbox[0][1]

            # Use the height of the legend for the image's height
            legend_height = legend_bbox.height  # In pixels
            image_width = legend_height  # Make image width proportional to legend height
            image_height = legend_height  # Fixed size based on the legend height

            # Determine whether the legend is on the left or right side of the figure
            shift_x = (legend_bbox.width/self.temperature_object.fig.bbox.width) * 1.1
            if x_position > 0.5:
                # Move the image to the left side if the legend is on the right
                shift_x = - (legend_bbox.width/self.temperature_object.fig.bbox.width) * 0.80 # A small offset to the left

            # Add new axes for the image (positioned relative to the legend)
            self.image_ax = self.temperature_object.fig.add_axes([x_position + shift_x, y_position, image_width / self.temperature_object.fig.bbox.width,
                                                image_height / self.temperature_object.fig.bbox.height])
        else:
            # display image in top right corner
            self.image_ax = self.temperature_object.fig.add_axes([0.855, 0.8, 0.08, 0.08])
        # Display the image
        self.image_ax.imshow(self.img)
        self.image_ax.axis('off')  # Hide the axes

        # self.temperature_object.draw()

    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "csv": # open temperature csv
            self.dialog1 = QFileDialog(self)
            
            if self.compare_box.isChecked():
                self.dialog1.setFileMode(QFileDialog.ExistingFiles)
                self.dialog1.setWindowTitle("Temperature Data CSV Files")
            else:
                self.dialog1.setFileMode(QFileDialog.ExistingFile)
                self.dialog1.setWindowTitle("Temperature Data CSV File")

            self.dialog1.setNameFilter("*.csv")
            self.dialog1.setDefaultSuffix("csv") # default suffix of csv
            
            if self.dialog1.exec(): 
                self.text_display.append("Temperature Data File(s): ")
                self.temperature_data_files = self.dialog1.selectedFiles()
                for file in self.temperature_data_files:
                    self.text_display.append(file +"\n")
        
        # NOT IMPLEMENTED YET
        elif d_type == "save": # save graph SVG location 
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            # self.dialog.setDefaultSuffix("*.txt")
            self.dialog.setFileMode(QFileDialog.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location+"\n")
    
    @Slot()
    def create_graph(self):
        if self.temperature_data_files is not None:
            self.graph_tab.clear()

            self.temperature_object = TemperatureGraph(self.temperature_data_files)
            self.graph = self.temperature_object.get_graphs(self.compare_box.isChecked())
            
            nav_tool = NavigationToolbar(self.graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(self.graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Temperature Graph")

            # Debugging statements
            # print(f"save_box is checked: {self.save_box.isChecked()}")
            # if self.file_save_location is not None:
            #   print(f"file_save_location: {self.file_save_location}")
            self.update_image_position()
        else:
            self.text_display.append("Error: No temperature .csv file found.\n")
