import matplotlib.pyplot as plt
import numpy as np
import os
import decimal
from PySide6.QtWidgets import QTextBrowser
from matplotlib.backends.backend_qtagg import FigureCanvas

class sweep_graph():
    def __init__(self, data_mtx, transducer, freq, save_folder, markersize, textbox: QTextBrowser):
        self.data_mtx = data_mtx
        self.save_folder = save_folder
        self.transducer = transducer
        self.freq = freq
        self.markersize = markersize
        self.textbox = textbox
        # self.sweep_tab = sweep_tab
        # self.save = save
        # self.graph = self.generate_graph()
        # if self.save:
        #     self.save_graph()

    def generate_graph(self):
        # By default rounding setting in python is decimal.ROUND_HALF_EVEN
        decimal.getcontext().rounding = decimal.ROUND_DOWN

        # Applied function generator voltage in mVpp
        x = self.data_mtx[:, 1]
        x_last = self.data_mtx[-1][1] # last x point
        x_first = self.data_mtx[0][1] # first x point

        # Peak pressure within the focus of the transducer in MPa
        y = self.data_mtx[:, 0]

        # Preparation matrix to solve y=m*x + b
        # Force the y-intercept to go through the origin, i.e. b=0
        A = np.vstack([x]).T

        self.m = np.linalg.lstsq(A, y, rcond=None)[0][0]
        self.textbox.append('[+] m value: {}'.format(self.m))

        correlation_matrix = np.corrcoef(x, y)
        correlation_xy = correlation_matrix[0, 1]
        r_squared = correlation_xy**2
        self.textbox.append('[+] r squared: {}'.format(r_squared))

        # Truncate the r squared value to four decimal places
        r_trunc = decimal.Decimal(r_squared)
        self.r_trunc_out = float(round(r_trunc, 4))
        self.textbox.append(f"[+] truncated r squared: {self.r_trunc_out}")

        y_calc = self.m * x
        r2 = 1 - np.sum((y - y_calc) ** 2.0) / np.sum((y - np.mean(y)) ** 2.0)
        r2_trunc = decimal.Decimal(r2)
        self.r2_trunc_out = float(round(r2_trunc, 4))
        self.textbox.append(f"matlab r squared: {self.r2_trunc_out}\n")

        # create dummy arrays to populate our line of best fit for display
        x_fit = np.array([0, x_last+(x_first)]) # changes x-fit to last point + the difference between the first x and 0 
        y_fit = self.m * x_fit + 0

        # temporarily change plot style
        with plt.rc_context({
                'figure.figsize': [6.50, 3.25],
                'font.family': 'calibri',
                'font.weight': 'medium',
                'axes.labelweight': 'medium',
                'axes.titleweight': 'medium',
            }):

            # plt.style.use('dark_background')
            # plt.style.use('seaborn-whitegrid') # NOW DEPRECATED
            plt.style.use('seaborn-v0_8-whitegrid')

            # plot the results
            # self.fig = Figure()
            self.fig, self.ax = plt.subplots(1, 1)
            # self.fig.style.use
            self.fig.set_size_inches(6.5, 3.5, forward=True)
            self.canvas = FigureCanvas(self.fig)

            self.ax.set_xlabel('Voltage Across the Transducer, Vpp')
            self.ax.set_ylabel('Peak Negative Pressure, MPa')
            self.ax.set_title(f"Frequency: {self.freq}, R squared: {self.r2_trunc_out:0.4f}")
            # plt.title('Frequency: {freq:0.3f}MHz, R squared: {r2:0.4f}'.format(
            # freq=1.487, r2=r_trunc_out))
            self.ax.plot(x_fit, y_fit, 'k-', linewidth=1.5, label='Fitted calibration')
            self.ax.plot(x, y, 'o', color='#74BEA3', mec='k',
                    label='Measured data', markersize=self.markersize)  # Old color was 6DA4BF
            self.ax.legend()

            # groupbox = QGroupBox("Placeholder")

            # self.tab_layout = QVBoxLayout()
            # self.tab_layout.addWidget(self.canvas)
            # self.tab_layout.addWidget(groupbox)
            # self.sweep_tab.setLayout(self.tab_layout)
            self.fig.set_canvas(self.canvas)

        return(self.canvas)

    def save_graph(self):
        save_filename = "calibration_"+self.transducer+"_f0.svg"
        self.fig.savefig(os.path.join(self.save_folder, save_filename), dpi=96, bbox_inches='tight', format='svg', pad_inches = 0, transparent=True)


# # THESE VARIABLES NEED TO BE CHANGED
# folder = r"C:\Users\RKPC\Documents\transducer_calibrations\534-T550H750\1650kHz\report"
# filename = r"sweep_534-T550H750_1650kHz_DATA_1.txt"
# save_folder = r"C:\Users\RKPC\Documents\transducer_calibrations\534-T550H750\1650kHz\report"
# freq = 1.65 # MHz
# save_filename = "calibration_534-T550H750_f0.svg"

# graph = sweep_graph(r"C:\Users\RKPC\Documents\transducer_calibrations\534-T550H750\1650kHz\report\sweep_534-T550H750_1650kHz_DATA_1.txt", "534-T550H750", 1.65, r"C:\Users\RKPC\Documents\transducer_calibrations\534-T550H750\1650kHz\report")
# graph.generate_graph()
# graph.save_graph()

# plt.show()