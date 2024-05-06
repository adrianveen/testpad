from PySide6.QtCore import Slot, Qt
# from PySide6.QtGui import QPixmap
# from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QComboBox, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser, QVBoxLayout,
                               QWidget)
from rfb.rfb_figures import create_rfb_graph

class RFBTab(QWidget):
    def __init__(self, parent: QWidget):
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
        self.print_graph_button.setStyleSheet("background-color: #74BEA3")
        self.print_graph_button.clicked.connect(lambda: self.createGraphs())
        # Text display 
        self.text_display = QTextBrowser()
        # Column 1
        self.file_button = QPushButton("Choose Files")
        self.file_button.clicked.connect(lambda: self.openFileDialog("data"))
        self.save_box = QCheckBox()
        self.save_folder = QPushButton("Choose Folder")
        self.save_folder.clicked.connect(lambda: self.openFileDialog("save"))
        controls_list_col_1 = [self.file_button, self.save_box, self.save_folder]
        # layout 
        controls_layout = QGridLayout()
        for i in range(len(controls_list_col_0)):
            controls_layout.addWidget(controls_list_col_0[i], i, 0)
        for i in range(len(controls_list_col_1)):
            controls_layout.addWidget(controls_list_col_1[i], i, 1)
        controls_layout.addWidget(self.print_graph_button, 3, 0, 1, 2)
        controls_layout.addWidget(self.text_display, 4, 0, 1, 2)
        controls_group.setLayout(controls_layout)
        
        # Graph display 
        self.graph_display = QTabWidget()
        self.graph_display.setTabsClosable(True)
        self.graph_display.tabCloseRequested.connect(lambda index: self.graph_display.removeTab(index))

        # main layout 
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.addWidget(controls_group, 0, 0)
        # main_layout.addWidget(self.text_display, 1, 0)
        main_layout.addWidget(self.graph_display, 0, 1)

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
    def createGraphs(self):
        self.graph_display.clear() # clear previous tabs
        graphs_list = create_rfb_graph(self.selected_data_files, self.selected_save_folder, self.save_box.isChecked(), self.text_display).graphs_list

        for i in graphs_list:
            self.graph_display.addTab(i[0], i[1])
        