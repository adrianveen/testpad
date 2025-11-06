"""RFB Tab View.

This module provides the user interface for the RFB Tab.
"""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QWidget,
)

from testpad.core.rfb.rfb_figures import CreateRFBGraph


class RFBTab(QWidget):
    """RFB Tab View."""

    def __init__(self, parent: QWidget | None) -> None:
        """Initialize the tab view."""
        super().__init__(parent)

        self.selected_data_files, self.selected_save_folder = [], ""

        # Controls group
        controls_group = QGroupBox("Selections")
        # Column 0
        file_label = QLabel("File: ")
        save_label = QLabel("Save graphs?")
        save_folder_label = QLabel("Save folder: ")
        controls_list_col_0 = [file_label, save_label, save_folder_label]
        # print graph button
        self.print_graph_button = QPushButton("PRINT GRAPHS")
        self.print_graph_button.setStyleSheet(
            "background-color: #66A366; color: black;"
        )
        self.print_graph_button.clicked.connect(lambda: self._create_graphs())
        # Text display
        self.text_display = QTextBrowser()
        # Column 1
        self.file_button = QPushButton("Choose Files")
        self.file_button.clicked.connect(lambda: self._open_file_dialog("data"))
        self.save_box = QCheckBox()
        self.save_folder = QPushButton("Choose Folder")
        self.save_folder.clicked.connect(lambda: self._open_file_dialog("save"))
        controls_list_col_1 = [self.file_button, self.save_box, self.save_folder]
        # layout
        controls_layout = QGridLayout()
        for i in range(len(controls_list_col_0)):
            controls_layout.addWidget(controls_list_col_0[i], i, 0)
        for i in range(len(controls_list_col_1)):
            if i == 1:
                controls_layout.addWidget(
                    controls_list_col_1[i], i, 1, Qt.AlignmentFlag.AlignCenter
                )
            else:
                controls_layout.addWidget(controls_list_col_1[i], i, 1)
        controls_layout.addWidget(self.print_graph_button, 3, 0, 1, 2)
        controls_layout.addWidget(self.text_display, 4, 0, 1, 2)
        controls_group.setLayout(controls_layout)

        # Graph display
        self.graph_display = QTabWidget()
        self.graph_display.setTabsClosable(True)
        self.graph_display.tabCloseRequested.connect(
            lambda index: self.graph_display.removeTab(index)
        )

        # main layout
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.addWidget(controls_group, 0, 0)
        main_layout.addWidget(self.graph_display, 0, 1)

        self.setLayout(main_layout)

    @Slot()
    def _open_file_dialog(self, dialog_type: str) -> None:
        if dialog_type == "data":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Data Files")
            self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFiles)
            if self.dialog1.exec():
                self.text_display.append("Data Files: ")
                self.selected_data_files = self.dialog1.selectedFiles()
            for i in self.selected_data_files:
                if i == self.selected_data_files[-1]:
                    self.text_display.append(i + "\n")
                else:
                    self.text_display.append(i)
        elif dialog_type == "save":
            self.dialog2 = QFileDialog(self)
            self.dialog2.setWindowTitle("Save Folder")
            self.dialog2.setFileMode(QFileDialog.FileMode.Directory)
            if self.dialog2.exec():
                self.selected_save_folder = self.dialog2.selectedFiles()[0]
                self.text_display.append(
                    "Save Folder: " + str(self.selected_save_folder) + "\n"
                )

    @Slot()
    def _create_graphs(self) -> None:
        self.graph_display.clear()  # clear previous tabs
        graphs_list = CreateRFBGraph(
            self.selected_data_files,
            self.selected_save_folder,
            self.save_box.isChecked(),
            self.text_display,
        ).graphs_list

        for i in graphs_list:
            self.graph_display.addTab(i[0], i[1])
