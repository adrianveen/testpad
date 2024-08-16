from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
from transducer.linear_scan_graph_generator import linear_scan

class TransducerLinearTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.selected_data_files, self.selected_save_folder = [], ""

        # Selections Group 
        selections_tab = QGroupBox("Selections") 
        # Column 0 
        files_label = QLabel("Data Files")
        save_folder_label = QLabel("Save folder")
        x_graph_label = QLabel("X Graph?")
        y_graph_label = QLabel("Y Graph?")
        z_graph_label = QLabel("Z Graph?")
        save_label = QLabel("Save file?")
        print_graph_button = QPushButton("PRINT GRAPHS")
        print_graph_button.setStyleSheet("background-color: #74BEA3")
        print_graph_button.clicked.connect(lambda: self.printGraphs())
        self.text_display = QTextBrowser()
        linear_col_0 = [files_label, save_folder_label, x_graph_label, y_graph_label, z_graph_label, save_label]
        # Column 1 
        files_button = QPushButton("Choose Files")
        files_button.clicked.connect(lambda: self.openFileDialog("data"))
        save_folder_button = QPushButton("Choose Folder")
        save_folder_button.clicked.connect(lambda: self.openFileDialog("save"))
        self.x_graph_box = QCheckBox()
        self.y_graph_box = QCheckBox()
        self.z_graph_box = QCheckBox()
        self.save_graph = QCheckBox()
        linear_col_1 = [files_button, save_folder_button, self.x_graph_box, self.y_graph_box, self.z_graph_box, self.save_graph]

        # add to selections_layout
        selections_layout = QGridLayout()
        # column 0 
        for i in range(len(linear_col_0)):
            selections_layout.addWidget(linear_col_0[i], i, 0)
        # column 1 
        for i in range(len(linear_col_1)):
            if i >= 2:
                selections_layout.addWidget(linear_col_1[i], i, 1, Qt.AlignCenter)
            else: 
                selections_layout.addWidget(linear_col_1[i], i, 1) 
        selections_layout.addWidget(print_graph_button, 6, 0, 1, 2)
        selections_layout.addWidget(self.text_display, 7, 0, 1, 2)

        selections_tab.setLayout(selections_layout)

        # text/graph display 
        text_graph_layout = QVBoxLayout()
        
        self.graph_display = QTabWidget()

        # text_graph_layout.addWidget(text_display)
        text_graph_layout.addWidget(self.graph_display)

        # main layout 
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.addWidget(selections_tab, 0, 0)
        main_layout.addLayout(text_graph_layout, 0, 1)
        self.setLayout(main_layout)

    @Slot()
    def openFileDialog(self, type):
        if type == "data":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("Data Files")
            self.dialog1.setFileMode(QFileDialog.ExistingFiles)
            if self.dialog1.exec(): 
                self.text_display.append("Data Files: ")
                self.selected_data_files = self.dialog1.selectedFiles()
            for i in self.selected_data_files:
                if i == self.selected_data_files[-1]:
                    self.text_display.append(i+"\n")
                else: 
                    self.text_display.append(i)
        elif type == "save":
            self.dialog2 = QFileDialog(self)
            self.dialog2.setWindowTitle("Save Folder")
            self.dialog2.setFileMode(QFileDialog.Directory)
            if self.dialog2.exec():
                self.selected_save_folder = self.dialog2.selectedFiles()[0]
                self.text_display.append("Save Folder: "+str(self.selected_save_folder)+"\n")
    @Slot()
    def printGraphs(self):
        # self.text_display.clear()
        self.graph_display.clear()
        # print(self.selected_data_files, self.selected_save_folder)
        variables_dict = [self.selected_data_files, self.save_graph.isChecked(), self.selected_save_folder, self.x_graph_box.isChecked(), self.y_graph_box.isChecked(), self.z_graph_box.isChecked()]
        x_graph, y_graph, z_graph = linear_scan(variables_dict, self.text_display).getGraphs()

        if x_graph is not None: 
            self.graph_display.addTab(x_graph, "X Linear")
        if y_graph is not None: 
            self.graph_display.addTab(y_graph, "Y Linear")
        if z_graph is not None: 
            self.graph_display.addTab(z_graph, "Z Linear")