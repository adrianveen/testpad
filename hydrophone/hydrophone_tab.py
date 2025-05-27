from hydrophone.hydrophone_graph import HydrophoneGraph

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QPushButton, QGridLayout, QGroupBox, 
                                QLabel, QLineEdit, QTabWidget, QTextBrowser,
                               QVBoxLayout, QWidget)
import numpy as np
import os
import re
from datetime import datetime
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import MultipleLocator

class HydrophoneAnalysisTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.hydrophone_scan_data = None
        self.file_save_location = None
        self.graph = None
        self.hydrophone_object = None
        self.mode = None
        self.serials = None

        # USER INTERACTION AREA
        buttons_groupbox = QGroupBox("File Selection")
        # combo box for single CSV or multiple CSV per transducer
        self.combo_label = QLabel("Select CSV Format:")
        self.combo_box = QComboBox()
        self.combo_box.setToolTip("Select the type of hydrophone scan data file.")
        self.combo_box.addItem("Multiple CSV files per transducer")
        self.combo_box.addItem("Single CSV file per transducer (legacy CSV format)")
        self.combo_box.setEditable(True)
        le: QLineEdit = self.combo_box.lineEdit()
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setReadOnly(True)

        # 3) Set the placeholder *after* it’s editable
        self.combo_box.setPlaceholderText("Select CSV Format")
        le.setPlaceholderText("Select CSV Format")   # ensure the edit itself knows
        self.combo_box.setCurrentIndex(-1)
        # compare checkbox
        self.compare_label = QLabel("Compare multiple datasets:")
        self.compare_box = QCheckBox()
        self.compare_box.setToolTip("Select to compare multiple datasets if legacy data set is being used.")
        self.compare_box.setEnabled(False) # disable for now
        self.compare_box.setChecked(False)
        self.combo_box.currentIndexChanged.connect(self.onFormatChanged)
        self.onFormatChanged(self.combo_box.currentIndex())
        # select file button
        self.select_file_btn = QPushButton("SELECT HYDROPHONE CSV FILE(S)")
        self.select_file_btn.clicked.connect(lambda: self.openFileDialog("csv"))
        # print graph button
        self.print_graph_btn = QPushButton("PRINT GRAPH(S)")
        self.print_graph_btn.setStyleSheet("background-color: #74BEA3")
        self.print_graph_btn.clicked.connect(lambda: self.print_graphs_clicked())
        # save graphs as SVG button
        self.save_as_svg_btn = QPushButton("SAVE GRAPH AS SVG")
        self.save_as_svg_btn.setEnabled(False)
        self.save_as_svg_btn.clicked.connect(lambda: self.openFileDialog("save"))

        # Layout for user interaction area
        selections_layout = QGridLayout()

        rows = [
            (self.combo_label, self.combo_box),  # 2-cell row
            (self.compare_label, self.compare_box),  # 2-cell row
            (self.select_file_btn,),                 # 1-widget, spans 2 columns
            (self.print_graph_btn,),
            (self.save_as_svg_btn,),
        ]

        for r, cells in enumerate(rows):
            if len(cells) == 1:
                selections_layout.addWidget(cells[0], r, 0, 1, 2)
            else:                   # exactly two widgets: left + right
                selections_layout.addWidget(cells[0], r, 0)
                selections_layout.addWidget(cells[1], r, 1)
        selections_layout.setAlignment(self.compare_box, Qt.AlignmentFlag.AlignCenter)
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
    
    @Slot()
    def openFileDialog(self, d_type):
        if d_type == "csv": # open hydrophone csv 
            self.dialog1 = QFileDialog(self)
            
            if self.compare_box.isChecked() or self.combo_box.currentText() == "Multiple CSV files per transducer":
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFiles)
                self.dialog1.setWindowTitle("Hydrophone Scan CSV Files")
            else:
                self.dialog1.setFileMode(QFileDialog.FileMode.ExistingFile)
                self.dialog1.setWindowTitle("Hydrophone Scan CSV File")

            self.dialog1.setNameFilter("*.csv")
            self.dialog1.setDefaultSuffix("csv") # default suffix of csv
            
            if self.dialog1.exec(): 
                self.text_display.append("Hydrophone Scan Data Files: ")
                self.hydrophone_scan_data = self.dialog1.selectedFiles()
                for file in self.hydrophone_scan_data:
                    self.text_display.append(file +"\n")
        
        elif d_type == "save":
            # 1) Show folder picker
            self.dialog = QFileDialog(self)
            self.dialog.setWindowTitle("Graph Save Location")
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
            if not self.dialog.exec():
                return
            self.file_save_location = self.dialog.selectedFiles()[0]
            self.text_display.append(f"Save Location: {self.file_save_location}\n")

            # 2) Prepare file names
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Always pick first unique serial number for file name
            serials = list(dict.fromkeys(self.hydrophone_object.transducer_serials))
            serial = serials[0] if serials else "unknown"
            svg_name = f"{serial}_sensitivity_vs_frequency_{timestamp}.svg"
            hydrophone_svg_path = os.path.join(self.file_save_location, svg_name)

            # 3) Stash original state
            fig      = self.graph.figure
            axes     = fig.get_axes()          # all axes (first one is your main plot)
            ax_main  = axes[0]                 # <-- grab the real plotting axes
            orig_locator = ax_main.xaxis.get_major_locator()
            orig_size    = fig.get_size_inches().copy()

            orig_marker_sizes      = {}
            orig_marker_edge_width = {}
            orig_line_widths       = {}
            for ax in axes:
                for line in ax.get_lines():
                    orig_marker_sizes[line]      = line.get_markersize()
                    orig_marker_edge_width[line] = line.get_markeredgewidth()
                    orig_line_widths[line]       = line.get_linewidth()

            # 4) Apply export tweaks
            dpi        = 96
            fig_width  = 6.5
            fig_height = 3.5
            fig.set_size_inches(fig_width, fig_height)

            for ax in axes:
                for line in ax.get_lines():
                    line.set_markersize(orig_marker_sizes[line] * 0.7)
                    line.set_markeredgewidth(orig_marker_edge_width[line] * 0.7)
                    line.set_linewidth(orig_line_widths[line] * 0.7)

            # adjust tick spacing if max freq > 3 MHz
            overall_max = max(ds[0].max() for ds in self.hydrophone_object.raw_data)
            if overall_max > 3.0:
                ax_main.xaxis.set_major_locator(MultipleLocator(0.4))
                fig.canvas.draw()

            # 5) Save SVG
            fig.savefig(
                hydrophone_svg_path,
                format="svg",
                dpi=dpi,
                bbox_inches="tight",
                pad_inches=0
            )

            # 6) Restore original state
            ax_main.xaxis.set_major_locator(orig_locator)
            fig.set_size_inches(orig_size)
            for ax in axes:
                for line in ax.get_lines():
                    line.set_markersize(orig_marker_sizes[line])
                    line.set_markeredgewidth(orig_marker_edge_width[line])
                    line.set_linewidth(orig_line_widths[line])
            fig.canvas.draw()

            # 7) Save TXT data files
            serials = self.hydrophone_object.transducer_serials
            unique_serials = list(dict.fromkeys(serials))

            if len(unique_serials) == 1:
                # Aggregate all datasets into one array
                all_arr = np.vstack([np.array(d).T for d in self.hydrophone_object.raw_data])
                # sort by frequency
                all_arr = all_arr[np.argsort(all_arr[:, 0])]
                # If STD column exists but is all NaN, drop it
                if all_arr.shape[1] == 3 and np.all(np.isnan(all_arr[:, 2])):
                    all_arr = all_arr[:, :2]
                    fmt = ('%s', '%.5f')
                elif all_arr.shape[1] == 3:
                    fmt = ('%s', '%.5f', '%.5f')
                else:
                    fmt = ('%s', '%.5f')

                txt_name = f"{unique_serials[0]}_sensitivity_vs_frequency_{timestamp}.txt"
                txt_path = os.path.join(self.file_save_location, txt_name)
                np.savetxt(txt_path, all_arr, delimiter=',', fmt=fmt)

            else:
                # One file per distinct serial
                for i, data in enumerate(self.hydrophone_object.raw_data):
                    serial_i = serials[i]
                    txt_name = f"{serial_i}_sensitivity_vs_frequency_{timestamp}.txt"
                    txt_path = os.path.join(self.file_save_location, txt_name)

                    arr = np.array(data).T
                    # sort by frequency
                    arr = arr[arr[:, 0].argsort()]
                    if arr.shape[1] == 3 and not np.all(np.isnan(arr[:, 2])):
                        fmt = ('%s', '%.5f', '%.5f')
                    else:
                        arr = arr[:, :2]
                        fmt = ('%s', '%.5f')

                    np.savetxt(txt_path, arr, delimiter=',', fmt=fmt)

            # 8) Notify user
            self.text_display.append("The following files were saved:\n")
            self.text_display.append(f"• SVG: {hydrophone_svg_path}")
            if len(unique_serials) == 1:
                self.text_display.append(f"• DATA: {txt_path}")
            else:
                for i in range(len(self.hydrophone_object.raw_data)):
                    serial_i = serials[i]
                    txt_name = f"{serial_i}_sensitivity_vs_frequency_{timestamp}.txt"
                    txt_path = os.path.join(self.file_save_location, txt_name)
                    self.text_display.append(f"• DATA: {txt_path}")
            self.text_display.append("")  # extra newline


    @Slot()
    def print_graphs_clicked(self):
        # ensure we actually have data
        if not self.hydrophone_scan_data:
            self.text_display.append("Error: No hydrophone CSV file(s) selected.\n")
            return

        # 1. create the object from whatever files the user picked
        self.hydrophone_object = HydrophoneGraph(self.hydrophone_scan_data)

        # 2. pick the plotting mode based on combo + checkbox
        text = self.combo_box.currentText()
        if text == "Multiple CSV files per transducer":
            mode = "append"      # all files mashed into one dataset
        elif self.compare_box.isChecked():
            mode = "overlaid"    # each file its own series, overlaid
        else:
            mode = "single"      # first (and only) file as a single series

        # 3. generate & show the graph
        canvas = self.hydrophone_object.get_graphs(mode=mode)
        self.create_graph(canvas)

        # 4. show serial numbers (deduplicated)
        serials = self.hydrophone_object.transducer_serials
        # preserve order, remove duplicates
        unique_serials = list(dict.fromkeys(serials))

        if len(unique_serials) == 1:
            # only one unique serial across all files
            self.text_display.append(
                f"Transducer Serial Number: {unique_serials[0]}\n"
            )
        else:
            # multiple distinct serials
            self.text_display.append("Transducer Serial Numbers:")
            for i, serial in enumerate(unique_serials, start=1):
                self.text_display.append(f"{i}. {serial}")
            self.text_display.append("")  # blank line

        self.print_sensitivities()

        # 5. append bandwidth value(s)
        if mode == "overlaid":
            for i, bw in enumerate(self.hydrophone_object.bandwidths, start=1):
                self.text_display.append(f"Dataset {i} bandwidth @½-max: {bw:.2f} MHz\n")
            self.text_display.append("")  # blank line
        else:
            # for both 'single' and 'append' modes
            bw = self.hydrophone_object.bandwidth
            self.text_display.append(f"Bandwidth @½-max: {bw:.2f} MHz\n")
   
    @Slot(int)
    def onFormatChanged(self, index: int):
        """Enable compare_box only when the second combo-item is chosen."""
        # index 0 → “Multiple CSV files…”
        # index 1 → “Single CSV file…”
        self.compare_box.setEnabled(index == 1)

    def print_sensitivities(self):
        if not (self.hydrophone_scan_data and self.hydrophone_object.raw_data):
            return

        # 1) gather & convert all datasets
        serials = self.hydrophone_object.transducer_serials
        unique_serials = list(dict.fromkeys(serials))  # preserve order, remove dupes
        converted = []   # each entry: [freq (MHz), sens (V/MPa), (std V/MPa if present)]
        for data in self.hydrophone_object.raw_data:
            arr = np.array(data).T  # shape (n_points, n_cols)
            converted.append(arr)

        # 2) single‐transducer? aggregate
        if len(unique_serials) == 1:
            serial = unique_serials[0]
            # stack only freq & sens columns
            all_data = np.vstack([a[:, :2] for a in converted])
            freq = all_data[:, 0]
            sens = all_data[:, 1]

            # compute max sensitivity
            idx_max = np.argmax(sens)
            max_sens = sens[idx_max]
            max_freq = freq[idx_max]

            # parse resonances from serial, e.g. “343-T1650H825”
            m = re.search(r'T(\d+)H(\d+)', serial)
            if m:
                tx_res = int(m.group(1)) / 1000.0   # MHz
                hp_res = int(m.group(2)) / 1000.0   # MHz
                # find nearest points
                idx_tx = np.argmin(np.abs(freq - tx_res))
                idx_hp = np.argmin(np.abs(freq - hp_res))
                sens_tx = sens[idx_tx]
                sens_hp = sens[idx_hp]
            else:
                tx_res = hp_res = sens_tx = sens_hp = None

            # build & print
            out = [
                f"Transducer Serial: {serial} (aggregated over {len(converted)} files)",
                f"Max Sensitivity: {max_sens:.3f} V/MPa at {max_freq:.3f} MHz"
            ]
            if tx_res is not None:
                out.append(f"Sensitivity at transducer resonance ({tx_res:.3f} MHz): {sens_tx:.3f} V/MPa")
            if hp_res is not None:
                out.append(f"Sensitivity at hydrophone resonance ({hp_res:.3f} MHz): {sens_hp:.3f} V/MPa")

            self.text_display.append("\n".join(out) + "\n")

        # 3) multiple‐transducer case: per‐dataset
        else:
            for i, arr in enumerate(converted):
                serial = serials[i] or "Unknown"
                freq = arr[:, 0]
                sens = arr[:, 1]

                idx_max = np.argmax(sens)
                max_sens = sens[idx_max]
                max_freq = freq[idx_max]

                m = re.search(r'T(\d+)H(\d+)', serial)
                if m:
                    tx_res = int(m.group(1)) / 1000.0
                    hp_res = int(m.group(2)) / 1000.0
                    idx_tx = np.argmin(np.abs(freq - tx_res))
                    idx_hp = np.argmin(np.abs(freq - hp_res))
                    sens_tx = sens[idx_tx]
                    sens_hp = sens[idx_hp]
                else:
                    tx_res = hp_res = sens_tx = sens_hp = None

                out = [
                    f"Transducer Serial: {serial}",
                    f"Max Sensitivity: {max_sens:.3f} V/MPa at {max_freq:.3f} MHz"
                ]
                if tx_res is not None:
                    out.append(f"Sensitivity at transducer resonance ({tx_res:.3f} MHz): {sens_tx:.3f} V/MPa")
                if hp_res is not None:
                    out.append(f"Sensitivity at hydrophone resonance ({hp_res:.3f} MHz): {sens_hp:.3f} V/MPa")

                self.text_display.append("\n".join(out) + "\n")


    def create_graph(self, canvas):
        # ensure we actually have data
        if not getattr(self, "hydrophone_scan_data", None):
            self.text_display.append("Error: No hydrophone data .csv file found.\n")
            return

        # 1) clear out the old plot tab
        self.graph_tab.clear()
        self.save_as_svg_btn.setEnabled(True)

        # 2) adopt the passed‐in canvas as our active graph
        self.graph = canvas

        # 3) build a toolbar for that canvas
        #    parent can be self or canvas.parent(), depending on your layout
        nav_tool = NavigationToolbar(self.graph, self)

        # 4) pack toolbar + canvas into a container widget
        graph_widget = QWidget()
        layout = QVBoxLayout(graph_widget)
        layout.addWidget(nav_tool)
        layout.addWidget(self.graph)

        # 5) add the new tab
        self.graph_tab.addTab(graph_widget, "Hydrophone Scan Data")