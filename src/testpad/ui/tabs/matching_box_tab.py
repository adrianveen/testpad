from PySide6.QtCore import Slot, Qt, QEvent, QPoint
from PySide6.QtGui import QPixmap, QResizeEvent, QDoubleValidator
from PySide6.QtWidgets import (QCheckBox, QFileDialog, QPushButton, QComboBox, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser, QVBoxLayout, QScrollArea,
                               QWidget)
from testpad.core.matching_box.lc_circuit_matching import Calculations
from testpad.core.matching_box.csv_graphs_hioki import csv_graph

class MatchingBoxTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # need to initialise these variables for saving to happen 
        self.selected_csv_file, self.selected_save_folder = "", ""
        self.new_match = None

        # MATCHING VALUES GROUP 
        matching_vals_group = QGroupBox("Matching Box Values")
        # Column 0
        freq_match_label = QLabel("Frequency: ")
        z_label = QLabel("Impedance: ")
        phase_label = QLabel("Phase: ")
        toroid_label = QLabel("Toroid: ")
        matching_list_col_0 = [freq_match_label, z_label, phase_label, toroid_label]
        # column 1 
        self.freq_textbox = QLineEdit()
        self.freq_textbox.setMaximumWidth(200)
        self.z_textbox = QLineEdit()
        self.z_textbox.setMaximumWidth(200)
        self.phase_textbox = QLineEdit()
        self.phase_textbox.setMaximumWidth(200)
        self.toroid_box = QComboBox()
        self.toroid_box.addItems(["200", "280", "160", "Custom"])
        self.toroid_box.setCurrentText("200")
        # adds a text box for a custom Toroid AL value and disables it by default
        self.toroid_textbox = QLineEdit()
        self.toroid_textbox.setValidator(QDoubleValidator())
        self.toroid_textbox.setMaximumWidth(100)
        self.toroid_textbox.setEnabled(False)
        # when custom value is set, enable the text box
        self.toroid_box.currentIndexChanged.connect(self.update_toroid_textbox)
        get_val = QPushButton("GET VALUES") 
        get_val.setStyleSheet("background-color: #66A366; color: black;")
        get_val.clicked.connect(lambda: self.getValues())
        matching_list_col_1 = [self.freq_textbox, self.z_textbox, self.phase_textbox, self.toroid_box]
        # column 2 
        self.affix_box = QComboBox()
        self.affix_box.addItems(["MHz", "kHz"])
        self.affix_box.setCurrentText("MHz")
        matching_list_col_2 = [self.affix_box]

        # text display + image layout 
        text_image_layout = QVBoxLayout()
        # text box which displays text 
        self.text_display = QTextBrowser() 
        # self.text_display.
        # image viewer in a scroll area so it can remain large and scroll when needed
        self.image_display = QLabel(self)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_scroll = QScrollArea(self)
        self.image_scroll.setWidget(self.image_display)
        self.image_scroll.setWidgetResizable(False)
        self.pixmap = QPixmap()
        self._source_pixmap = None
        self._scale_factor = 0.15  # default to at least 15% of original size
        self._panning = False
        self._pan_start = QPoint()
        # Enable panning and zooming via event filter on viewport
        self.image_scroll.viewport().installEventFilter(self)
        # add to layout 
        text_image_layout.addWidget(self.text_display)
        text_image_layout.addWidget(self.image_scroll)

        matching_vals_layout = QGridLayout()
        # add all widgets to grid layout 
        for i in range(len(matching_list_col_0)): 
            matching_vals_layout.addWidget(matching_list_col_0[i], i, 0)
        matching_vals_layout.addWidget(get_val, 4, 0, 1, 3)

        for i in range(len(matching_list_col_1)): 
            matching_vals_layout.addWidget(matching_list_col_1[i], i, 1)

        matching_vals_layout.addWidget(self.toroid_textbox, 3, 2)

        for i, widget in enumerate(matching_list_col_2): 
            if widget != self.toroid_textbox:
                matching_vals_layout.addWidget(widget, i, 2)
                
        matching_vals_layout.addLayout(text_image_layout, 5, 0, 1, 3)
        # matching_vals_layout.addWidget(self.text_display, 5, 0, 1, 3)
        # matching_vals_layout.addWidget(self.image_display, 6, 0, 1, 3)
        matching_vals_group.setLayout(matching_vals_layout)

        # matching values layout 
        matching_col_layout = QVBoxLayout()
        matching_col_layout.addWidget(matching_vals_group)

        # CSV GRAPHS GROUP 
        # Column 0 
        self.csv_graphs_group = QGroupBox("CSV Graphs")
        freq_csv_label = QLabel("Frequency: ")
        file_label = QLabel("File: ")
        save_label = QLabel("Save graphs?")
        save_folder_label = QLabel("Save folder: ")
        print_graphs_button = QPushButton("PRINT GRAPHS")
        print_graphs_button.setStyleSheet("background-color: #66A366; color: black;")
        print_graphs_button.clicked.connect(lambda: self.printCSVGraphs())
        csv_list_col_0 = [freq_csv_label, file_label, save_label, save_folder_label]
        # Column 1 
        self.freq_csv_field = QLineEdit()
        self.freq_csv_field.setMaximumWidth(200)
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(lambda: self.openFileDialog("file"))
        self.save_checkbox = QCheckBox()
        self.save_folder_button = QPushButton("Choose Folder")
        self.save_folder_button.clicked.connect(lambda: self.openFileDialog("save"))
        csv_list_col_1 = [self.freq_csv_field, self.file_button, self.save_checkbox, self.save_folder_button]
        # Column 2 
        self.freq_csv_combobox = QComboBox()
        self.freq_csv_combobox.addItems(["MHz", "kHz"])
        csv_list_col_2 = [self.freq_csv_combobox]

        # display graphs in tabs
        self.graph_display = QTabWidget()

        csv_graphs_layout = QGridLayout()
        for i in range(len(csv_list_col_0)): 
            csv_graphs_layout.addWidget(csv_list_col_0[i], i, 0)
        csv_graphs_layout.addWidget(print_graphs_button, 4, 0, 1, 3)
        for i in range(len(csv_list_col_1)): 
            if csv_list_col_1[i] == self.save_checkbox:
                csv_graphs_layout.addWidget(csv_list_col_1[i], i, 1, Qt.AlignCenter)
            else: 
                csv_graphs_layout.addWidget(csv_list_col_1[i], i, 1)
        for i in range(len(csv_list_col_2)): 
            csv_graphs_layout.addWidget(csv_list_col_2[i], i, 2)
        csv_graphs_layout.addWidget(self.graph_display, 7, 0, 1, 3)
        self.csv_graphs_group.setLayout(csv_graphs_layout)

        # csv graphs layout 
        csv_col_layout = QVBoxLayout()
        csv_col_layout.addWidget(self.csv_graphs_group)

        # main layout of matching box section 
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.addLayout(matching_col_layout, 0, 0)
        main_layout.addLayout(csv_col_layout, 0, 1)

        self.setLayout(main_layout)
    
    # enable custom toroid textbox when custom is selected
    def update_toroid_textbox(self):
            if self.toroid_box.currentText() == "Custom":
                self.toroid_textbox.setEnabled(True)
            else:
                self.toroid_textbox.setEnabled(False)

    # keep current image scale across resizes; scroll area handles overflow
    def resizeEvent(self, event: QResizeEvent) -> None:
        return super().resizeEvent(event)

    # execute matching box program 
    @Slot()
    def getValues(self):
        self.text_display.clear()
        freq = 0
        if self.freq_textbox.text():
            freq = float(self.freq_textbox.text())
        if self.affix_box.currentText() == "kHz": 
            freq *= 1e3
        else: 
            freq *= 1e6
        self.new_match = Calculations()

        if self.toroid_box.currentText() == "Custom":
            AL_value = float(self.toroid_textbox.text())
        else: 
            AL_value= float(self.toroid_box.currentText())

        text = self.new_match.calculations(freq, float(self.z_textbox.text()), float(self.phase_textbox.text()), AL_value)
        self.text_display.append(text)
        # Load original image and display at least 60% of original size
        self._source_pixmap = QPixmap(self.new_match.image_file)
        self._apply_scale(self._scale_factor)
        # print(new_match.image_file)
        # self.pixmap.load(new_match.image_file)
        # # self.text_display.append(QTextBrowser.searchPaths(new_match.image_file))
        # self.image_display.repaint()
        # self.image_display.adjustSize()

    # @Slot()
    # def resizeImage(self):
    #     # resize the image if the matching calculations have already been made
    #     if self.new_match is not None: 
    #         self.pixmap = QPixmap(self.new_match.image_file)
    #         self.image_display.setPixmap(self.pixmap.scaledToWidth(self.text_display.width()))

    # choose files 
    @Slot() 
    def openFileDialog(self, type):
        # self.selected_csv_file, self.selected_save_folder = None, None
        if type == "file":
            self.dialog1 = QFileDialog(self)
            self.dialog1.setWindowTitle("CSV File")
            self.dialog1.setFileMode(QFileDialog.ExistingFile)
            if self.dialog1.exec(): 
                self.selected_csv_file = self.dialog1.selectedFiles()[0]
        elif type == "save": 
            self.dialog2 = QFileDialog(self)
            self.dialog2.setFileMode(QFileDialog.Directory)
            if self.dialog2.exec(): 
                self.selected_save_folder = self.dialog2.selectedFiles()[0]
            

    # print CSV graphs to viewer 
    @Slot()
    def printCSVGraphs(self):
        self.graph_display.clear()
        # print(self.selected_csv_file)
        # print(self.selected_save_folder)
        impedance_graph, phase_graph = csv_graph(self.freq_csv_field.text(), self.freq_csv_combobox.currentText(), self.selected_csv_file, self.save_checkbox.isChecked(), self.selected_save_folder).returnGraphs()
        self.graph_display.addTab(impedance_graph, "Impedance Graph")
        self.graph_display.addTab(phase_graph, "Phase Graph")
        # self.graph_display.adjustSize()

    def _apply_scale(self, factor: float):
        """Apply scale to the original image and set it on the label.
        Ensures a minimum of 15% of the original size. Scrollbars appear if it exceeds the viewport.
        """
        if self._source_pixmap is None or self._source_pixmap.isNull():
            return
        factor = max(0.15, factor)
        w = int(self._source_pixmap.width() * factor)
        h = int(self._source_pixmap.height() * factor)
        self.pixmap = self._source_pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_display.setPixmap(self.pixmap)
        self.image_display.adjustSize()

    def eventFilter(self, obj, event):
        # Panning with left click-drag; zoom with Ctrl+scroll
        if obj is self.image_scroll.viewport():
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self._panning = True
                self._pan_start = event.pos()
                self.image_scroll.setCursor(Qt.ClosedHandCursor)
                return True
            elif event.type() == QEvent.MouseMove and self._panning:
                delta = event.pos() - self._pan_start
                self._pan_start = event.pos()
                h = self.image_scroll.horizontalScrollBar()
                v = self.image_scroll.verticalScrollBar()
                h.setValue(h.value() - delta.x())
                v.setValue(v.value() - delta.y())
                return True
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._panning = False
                self.image_scroll.setCursor(Qt.ArrowCursor)
                return True
            elif event.type() == QEvent.Wheel and (event.modifiers() & Qt.ControlModifier):
                # Zoom in/out keeping the cursor position roughly stable
                if self._source_pixmap is None or self._source_pixmap.isNull():
                    return True
                dy = event.angleDelta().y()
                if dy == 0:
                    return True
                step = 1.1 if dy > 0 else 1/1.1

                h = self.image_scroll.horizontalScrollBar()
                v = self.image_scroll.verticalScrollBar()
                posf = event.position() if hasattr(event, 'position') else event.pos()
                cx = posf.x()
                cy = posf.y()

                pre_w = max(1, self.image_display.width())
                pre_h = max(1, self.image_display.height())
                cx_ratio = (h.value() + cx) / pre_w
                cy_ratio = (v.value() + cy) / pre_h

                self._scale_factor = max(0.15, min(5.0, self._scale_factor * step))
                self._apply_scale(self._scale_factor)

                new_w = max(1, self.image_display.width())
                new_h = max(1, self.image_display.height())
                h.setValue(int(cx_ratio * new_w - cx))
                v.setValue(int(cy_ratio * new_h - cy))
                return True
        return super().eventFilter(obj, event)
