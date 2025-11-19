from pathlib import Path

from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from testpad.core.nanobubbles.nanobubbles_graph import NanobubblesGraph


class NanobubblesTab(QWidget):
    """NanobubblesTab class."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the NanobubblesTab class."""
        super().__init__(parent)

        self.nanobubbles_files = None
        self.file_save_location = None
        self.selected_data_type = None
        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox()
        # select file button
        self.select_file_btn = QPushButton("SELECT NANOBUBBLE .TXT FILE")
        self.select_file_btn.clicked.connect(lambda: self._open_file_dialog("txt"))
        # log checkbox and label
        self.log_label = QLabel("Logarithmic Scale:")
        self.log_box = QCheckBox()
        self.log_box.setChecked(True)

        self.convolution_label = QLabel("Apply Convolution Filter:")
        self.convolution_box = QCheckBox()
        self.convolution_box.setChecked(True)
        self.convolution_spinbox = QSpinBox()
        self.convolution_spinbox.setMaximum(20)
        self.convolution_spinbox.setMinimum(2)
        self.convolution_spinbox.setValue(3)

        # bin count spin box
        self.bin_count_label = QLabel("Bin Count (log scale):")
        self.bin_count_spinbox = QSpinBox()
        self.bin_count_label.setEnabled(False)
        self.bin_count_spinbox.setEnabled(False)
        # set spinbox min/max value
        self.bin_count_spinbox.setMaximum(10000)
        self.bin_count_spinbox.setMinimum(10)
        # set increments to 10
        self.bin_count_spinbox.setSingleStep(10)
        # set spinbox default value
        self.bin_count_spinbox.setValue(200)

        # bin width label and field
        self.bin_width_label = QLabel("Bin Width (linear scale):")
        self.bin_width_field = QLineEdit()
        self.bin_width_field.setEnabled(False)
        self.bin_width_label.setEnabled(False)
        self.bin_width_field.setText("30")

        # dropdown for data selection
        self.data_selection_label = QLabel("Select Data to Plot:")
        self.data_selection = QComboBox()
        self.data_selection.addItems(["Concentration Per mL", "Size Distribution"])

        # option to compare multiple datasets.
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setChecked(False)

        # save file checkbox and save location button
        self.save_label = QLabel("Save graph as svg file:")
        self.save_box = QCheckBox()
        self.save_box.setChecked(False)
        self.save_folder_btn = QPushButton("SAVE LOCATION")
        self.save_folder_btn.clicked.connect(lambda: self._open_file_dialog("save"))

        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH")
        self.print_graph_btn.setStyleSheet("background-color: #66A366; color: black;")
        self.print_graph_btn.clicked.connect(lambda: self._create_graph())

        # Layout for user interaction area
        selections_layout = QGridLayout()
        selections_layout.addWidget(self.select_file_btn, 0, 0, 1, 2)
        # add log scale label and checkbox
        selections_layout.addWidget(self.log_label, 1, 0)
        selections_layout.addWidget(self.log_box, 1, 1, Qt.AlignmentFlag.AlignCenter)

        selections_layout.addWidget(self.convolution_label, 2, 0)

        self.convolution_settings_hbox = QHBoxLayout()
        self.convolution_settings_hbox.addWidget(self.convolution_box)
        self.convolution_settings_hbox.addWidget(self.convolution_spinbox)
        selections_layout.addLayout(
            self.convolution_settings_hbox, 2, 1, Qt.AlignmentFlag.AlignCenter
        )

        # add bin count label and spinbox
        selections_layout.addWidget(self.bin_count_label, 3, 0)
        selections_layout.addWidget(self.bin_count_spinbox, 3, 1)
        # add bin width label and field
        selections_layout.addWidget(self.bin_width_label, 4, 0)
        selections_layout.addWidget(self.bin_width_field, 4, 1)
        # add data selection label and dropdown
        selections_layout.addWidget(self.data_selection_label, 5, 0)
        selections_layout.addWidget(self.data_selection, 5, 1)
        # add compare label and checkbox
        selections_layout.addWidget(self.compare_label, 6, 0)
        selections_layout.addWidget(
            self.compare_box, 6, 1, Qt.AlignmentFlag.AlignCenter
        )

        # add save label and checkbox
        selections_layout.addWidget(self.save_label, 7, 0)
        selections_layout.addWidget(self.save_box, 7, 1, Qt.AlignmentFlag.AlignCenter)
        selections_layout.addWidget(self.save_folder_btn, 8, 0, 1, 2)
        # add print graph button
        selections_layout.addWidget(self.print_graph_btn, 9, 0, 1, 2)
        buttons_groupbox.setLayout(selections_layout)

        # TEXT CONSOLE
        self.text_display = QTextBrowser()

        # GRAPH DISPLAY
        self.graph_tab = QTabWidget()

        # MAIN LAYOUT
        main_layout = QGridLayout()

        # Add the buttons_groupbox to the layout
        main_layout.addWidget(buttons_groupbox, 0, 0)
        main_layout.setColumnStretch(0, 1)  # Stretch factor for buttons_groupbox

        # Add the graph_tab to the layout
        main_layout.addWidget(self.graph_tab, 0, 1, 2, 1)  # Spans 2 rows, 1 column
        main_layout.setColumnStretch(1, 3)  # Stretch factor for graph_tab

        # Add the text_display to the layout
        main_layout.addWidget(self.text_display, 1, 0)
        main_layout.setRowStretch(1, 1)  # Uniform stretching for the text_display

        # Set the layout
        self.setLayout(main_layout)

    # opens txt file for reading
    @Slot()
    def _open_file_dialog(self, d_type: str) -> None:
        if d_type == "txt":  # open nanobubble txt
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Nanobubble TXT File(s)")

            if self.compare_box.isChecked():
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFiles)
            else:
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)

            self.dialog1.setNameFilter("*.txt")
            self.dialog1.setDefaultSuffix("txt")  # default suffix of yaml

            if self.dialog1.exec():
                self.text_display.append("Nanobubble File(s): ")
                self.nanobubbles_files = self.dialog1.selectedFiles()
                for file in self.nanobubbles_files:
                    self.text_display.append(file + "\n")

        elif d_type == "save":  # save graph SVG location
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")

            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
            if self.dialog.exec():
                self.text_display.append("Save Location: ")
                self.file_save_location = self.dialog.selectedFiles()[0]
                self.text_display.append(self.file_save_location + "\n")

    # add graph + navtoolbar to graph display
    @Slot()
    def _create_graph(self) -> None:
        if self.nanobubbles_files is not None:
            self.graph_tab.clear()
            self.selected_data_type = self.data_selection.currentText()
            print(f"Selected data type: {self.selected_data_type}")
            # check that bin width is a number
            try:
                _bin_width = float(self.bin_width_field.text())
            except ValueError:
                error_message = "Error: Bin width must be a valid number."
                print(error_message)
                self.text_display.append(error_message)
                return

            if not self.log_box.isChecked():
                nanobubbles_object = NanobubblesGraph(
                    self.nanobubbles_files, self.selected_data_type
                )
                graph = nanobubbles_object.get_graphs(
                    bins=int(float(self.bin_width_field.text())),
                    scale=False,
                    overlaid=self.compare_box.isChecked(),
                    data_selection=self.selected_data_type,
                    apply_convolution_filter=self.convolution_box.isChecked(),
                    convolution_size=self.convolution_spinbox.value(),
                )
            else:  # log scale
                nanobubbles_object = NanobubblesGraph(
                    self.nanobubbles_files, self.selected_data_type
                )
                graph = nanobubbles_object.get_graphs(
                    bins=int(self.bin_count_spinbox.value()),
                    scale=True,
                    overlaid=self.compare_box.isChecked(),
                    data_selection=self.selected_data_type,
                    apply_convolution_filter=self.convolution_box.isChecked(),
                    convolution_size=self.convolution_spinbox.value(),
                )

            nav_tool = NavigationToolbar(graph)

            graph_widget = QWidget()
            burn_layout = QVBoxLayout()
            burn_layout.addWidget(nav_tool)
            burn_layout.addWidget(graph)
            graph_widget.setLayout(burn_layout)

            self.graph_tab.addTab(graph_widget, "Nanobubbles Graph")

            # Debugging statements
            # print(f"save_box is checked: {self.save_box.isChecked()}")
            # if self.file_save_location is not None:
            #   print(f"file_save_location: {self.file_save_location}")
            if self.compare_box.isChecked() and len(nanobubbles_object.raw_data) == 1:
                self.text_display.append(
                    "Warning: Only one dataset selected for comparison. \
                        Please select multiple datasets.\n"
                )

            if self.save_box.isChecked():
                if (
                    self.file_save_location is None
                    or not Path(self.file_save_location).exists()
                ):
                    error_message = (
                        "Error: Save location was not specified or does not exist.\n"
                    )
                    self.text_display.append(error_message)
                    return

                save_loc = nanobubbles_object.save_graph(
                    self.file_save_location, self.compare_box.isChecked()
                )
                self.text_display.append(f"Saved to {save_loc}\n")
        else:
            self.text_display.append("Error: No nanobubble .txt file found.\n")

    # toggle bin width field based on log scale checkbox
    @Slot()
    def _toggle_log_scale(self) -> None:
        if self.log_box.isChecked():
            self.bin_width_field.setEnabled(False)
            self.bin_width_label.setEnabled(False)
        else:
            self.bin_width_field.setEnabled(True)
            self.bin_width_label.setEnabled(True)
            self.bin_count_spinbox.setEnabled(False)
            self.bin_count_label.setEnabled(False)
