import decimal
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QMessageBox, QTextBrowser

from testpad.utils.vpp_stats import check_new_vpp, classify_vpp


class sweep_graph:
    def __init__(
        self,
        data_mtx,
        transducer,
        freq: str,
        save_folder: str,
        markersize: int,
        textbox: QTextBrowser,
        generate_figure: bool = True,
        show_feedback: bool = True,
    ) -> None:
        self.data_mtx = data_mtx
        self.generate_figure = generate_figure
        self.save_folder = save_folder
        self.transducer = transducer
        self.freq = freq
        self.markersize = markersize
        self.textbox = textbox
        self.canvas = None
        self.fig = None
        self.ax = None
        self.show_feedback = show_feedback

    def _show_feedback(self, text: str) -> None:
        if not self.show_feedback:
            return

        if self.textbox is not None:
            self.textbox.append(text)
        else:
            print(text)

    def generate_graph(self) -> FigureCanvas | None:
        # By default rounding setting in python is decimal.ROUND_HALF_EVEN
        decimal.getcontext().rounding = decimal.ROUND_DOWN

        # Applied voltage in mVpp (Voltage across the transducer)
        x = self.data_mtx[:, 1]
        x_last = self.data_mtx[-1][1]  # last x point
        x_first = self.data_mtx[0][1]  # first x point

        # Peak pressure within the focus of the transducer in MPa
        y = self.data_mtx[:, 0]

        # Preparation matrix to solve y=m*x + b
        # Force the y-intercept to go through the origin, i.e. b=0
        A = np.vstack([x]).T

        self._show_feedback("Full m and r square values:")

        self.m = np.linalg.lstsq(A, y, rcond=None)[0][0]

        self._show_feedback(f"[+] m value: {self.m}")

        correlation_matrix = np.corrcoef(x, y)
        correlation_xy = correlation_matrix[0, 1]
        r_squared = correlation_xy**2
        self._show_feedback(f"[+] r squared: {r_squared}")

        # Safely parse frequency in MHz for numeric comparisons/formatting
        freq_mhz_val = None
        try:
            if isinstance(self.freq, str):
                # Expect formats like "1.65 MHz" or "1.65"
                freq_mhz_val = float(self.freq.partition(" ")[0])
            else:
                freq_mhz_val = float(self.freq)
        except Exception:
            freq_mhz_val = None
        freq_label = (
            f"{freq_mhz_val:.3f} MHz" if freq_mhz_val is not None else str(self.freq)
        )

        # Calculate and show voltage at 1 MPa
        if self.m != 0:
            voltage_at_1mpa = 1 / self.m
            self._show_feedback(f"[+] Voltage at 1 MPa: {voltage_at_1mpa:.2f} Vpp")

        # for 1.65 MHz transducers, check if voltage at 1 MPa is within acceptable range

        # Basic STD calculations if we want to revert to simpler method
        # v_range_min = 13.8 - 0.9
        # v_range_max = 13.8 + 0.9
        # is_ok_std = v_range_min <= voltage_at_1mpa <= v_range_max

        ####
        # Hampel median/MAD outlier screen: compute robust z=|x-median|/MAD* and flag OK (<=3.0)
        # SUSPECT (3.0-4.5), OUTLIER (>4.5)
        # Thresholds in Vpp for 1.65 MHz transducer:
        #   OK band: ± (3 * 0.7413) = ± 2.2239 → 11.4761 to 15.9238 Vpp
        #   SUSPECT band: 11.4761 > value ≥ 10.3642 OR 15.9239 ≤ value < 17.0359 Vpp
        #   OUTLIER band: value < 10.3642 OR value > 17.0358 Vpp
        #   where 0.7413 is the MAD scaled value
        ####
        # voltage_at_1mpa = 17.0358  # test value only -- see above for expected ranges

        # 1. Classify the voltage at 1 MPa using the Hampel method
        # 2. classification is taken from dict{} returned by classify_vpp()
        # 3. check_new_vpp returns a boolean if dict['classification'] == 'OK'
        vpp_info = classify_vpp(voltage_at_1mpa)
        is_ok = check_new_vpp(voltage_at_1mpa)

        if (freq_mhz_val is not None) and abs(freq_mhz_val - 1.65) < 1e-6 and not is_ok:
            self._show_feedback(
                f"[ ! ] Voltage at 1 MPa is outside of the expected range. \
                    Classification: '{vpp_info['classification']}'"
            )
            QMessageBox.warning(
                None,
                "Warning",
                f"Voltage at 1 MPa ({voltage_at_1mpa:.2f} Vpp) is outside of the \
                    expected range for {freq_label} transducer. \
                        Classification: '{vpp_info['classification']}'\n\n"
                "Ensure that the transducer has been properly aligned.\n\n"
                "If this warning persists, please contact Marc Santos or Rajiv \
                    Chopra for guidance on how to proceed.",
            )
        elif (freq_mhz_val is not None) and abs(freq_mhz_val - 1.65) < 1e-6 and is_ok:
            self._show_feedback(
                f"[+] Voltage at 1 MPa is within the expected range for {freq_label} \
                    transducer. Classification: '{vpp_info['classification']}'"
            )

        # Truncate the m value and r squared value to 6 decimal places
        self._show_feedback("\nTruncated m and r squared values:")
        self._show_feedback(f"[+] truncated m value: {self.m:.6f}")
        r_trunc = decimal.Decimal(r_squared)
        self.r_trunc_out = float(round(r_trunc, 6))
        self._show_feedback(f"[+] truncated r squared: {self.r_trunc_out}")

        y_calc = self.m * x
        r2 = 1 - np.sum((y - y_calc) ** 2.0) / np.sum((y - np.mean(y)) ** 2.0)
        r2_trunc = decimal.Decimal(r2)
        self.r2_trunc_out = float(round(r2_trunc, 4))
        self._show_feedback(f"\nMATLAB r squared: {self.r2_trunc_out}\n")

        # create dummy arrays to populate our line of best fit for display
        x_fit = np.array(
            [0, x_last + (x_first)]
        )  # changes x-fit to last point + the difference between the first x and 0
        y_fit = self.m * x_fit + 0

        # temporarily change plot style
        if self.generate_figure:
            with plt.rc_context(
                {
                    # 'figure.figsize': [6.50, 3.25],
                    "font.family": "calibri",
                    "font.weight": "medium",
                    "axes.labelweight": "medium",
                    "axes.titleweight": "medium",
                }
            ):
                plt.style.use("seaborn-v0_8-whitegrid")

                self.fig, self.ax = plt.subplots(1, 1)
                self.fig.set_size_inches(6.5, 3.5, forward=True)
                self.canvas = FigureCanvas(self.fig)

                self.ax.set_xlabel("Voltage Across the Transducer, Vpp")
                self.ax.set_ylabel("Peak Negative Pressure, MPa")
                self.ax.set_title(
                    f"Frequency: {self.freq}, R squared: {self.r2_trunc_out:0.4f}"
                )
                self.ax.plot(
                    x_fit, y_fit, "k-", linewidth=1.5, label="Fitted calibration"
                )
                self.ax.plot(
                    x,
                    y,
                    "o",
                    color="#74BEA3",
                    mec="k",
                    label="Measured data",
                    markersize=self.markersize,
                )  # Old color was 6DA4BF
                self.ax.legend()

                self.fig.set_canvas(self.canvas)

        # Note this will be none if generate_figure is false
        return self.canvas

    def save_graph(self) -> None:
        save_filename = "calibration_" + self.transducer + "_f0.svg"
        if self.fig is not None:
            self.fig.savefig(
                Path(self.save_folder) / save_filename,
                dpi=96,
                bbox_inches="tight",
                format="svg",
                pad_inches=0,
                transparent=True,
            )
