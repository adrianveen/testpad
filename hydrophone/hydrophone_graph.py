import numpy as np
import os
import sys
from PIL import Image
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, MultipleLocator
from matplotlib.colors import to_rgb, to_hex
from matplotlib.backends.backend_qtagg import FigureCanvas

class HydrophoneGraph:
    def __init__(self, hydrophone_csv) -> None:
        self.hydrophone_csv = hydrophone_csv
        if not hydrophone_csv:
            raise ValueError("No file(s) provided")
        # Initialize storage
        self.raw_data = []
        self.transducer_serials = []  # per-file serial numbers
        self.bandwidths = []  # per-file bandwidths
        self.bandwidth = None  # combined bandwidth (single/append modes)
        # Process files and store raw_data
        self.raw_data = self._process_files(hydrophone_csv)
        # Pre-compute bandwidths @ half-max for each dataset
        self.bandwidths = [self._compute_bandwidth(freq, sens)
                           for freq, sens, *rest in self.raw_data]
        # Placeholder for combined bandwidth (single/append modes)
        self.bandwidth = None
    
    @property
    def tx_serial_no(self):
        """
        Returns the transducer serial number.
        """
        return self.transducer_serials[0] if self.transducer_serials else None
    
    def _process_files(self, file_paths):
        """
        Process one or more CSV files and extract relevant data.
        Returns:
            list of tuples: (freq_series, sens_series) or (freq_series, sens_series, std_series)
        Also populates self.transducer_serials.
        """
        datasets = []
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        for path in file_paths:
            with open(path, 'r') as f:
                lines = f.read().splitlines()
            # Extract serial from second line
            if len(lines) < 2:
                raise ValueError(f"File {path} missing header lines")
            tx_serial_line = lines[1]
            cells = tx_serial_line.strip().split(',')
            if len(cells) < 2:
                raise ValueError(f"Serial extraction failed in {path}")
            serial = cells[1]
            self.transducer_serials.append(serial)
            # Locate header row
            header_idx = next((i for i, L in enumerate(lines) if "Frequency (MHz)" in L), None)
            if header_idx is None:
                raise ValueError(f"Header not found in {path}")
            csv_str = "\n".join(lines[header_idx:])
            df = pd.read_csv(StringIO(csv_str))
            # Required columns
            freq = df["Frequency (MHz)"]
            sens = df["Sensitivity (mV/MPa)"]
            if "Standard deviation (mV/MPa)" in df:
                std = df["Standard deviation (mV/MPa)"]
                datasets.append((freq, sens, std))
            else:
                datasets.append((freq, sens))

        return datasets

    def _compute_bandwidth(self, freq, sens):
        """
        Compute FWHM (full-width at half-maximum) of the *fundamental* sens(freq) peak.
        Returns bandwidth in same units as freq (MHz), ignoring higher harmonics.
        """
        f = np.asarray(freq, dtype=float)
        y = np.asarray(sens, dtype=float) / 1000.0

        # 1) Sort by frequency
        order = np.argsort(f)
        f, y = f[order], y[order]

        # 2) Find all local-maxima indices
        peaks = np.where((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:]))[0] + 1
        if peaks.size == 0:
            return np.nan

        # 3) Filter out any peaks above half the max frequency (to drop harmonics)
        freq_cut = f.max() / 2.0
        low_peaks = peaks[f[peaks] <= freq_cut]
        if low_peaks.size:
            # pick the one with the largest amplitude
            peak_idx = low_peaks[np.argmax(y[low_peaks])]
        else:
            # fallback to the very first peak
            peak_idx = peaks[0]

        peak_val = y[peak_idx]
        half_val = peak_val / 2.0

        # 4) Find left half-max crossing
        left = np.where(y[:peak_idx] <= half_val)[0]
        if left.size:
            i = left[-1]
            f_low = np.interp(half_val, [y[i], y[i+1]], [f[i], f[i+1]])
        else:
            f_low = f[0]

        # 5) Find right half-max crossing
        right = np.where(y[peak_idx:] <= half_val)[0]
        if right.size:
            j = peak_idx + right[0] - 1
            f_high = np.interp(half_val, [y[j], y[j+1]], [f[j], f[j+1]])
        else:
            f_high = f[-1]

        return f_high - f_low

    def get_graphs(self, mode: str = "single") -> FigureCanvas:
        """
        Generate and return a FigureCanvas for modes:
            'single', 'overlaid', or 'append'.
        Also sets self.bandwidth or retains self.bandwidths.
        """
        self._prepare_figure()
        if mode == "append":
            self._plot_appended()
            # Compute combined bandwidth
            import pandas as pd
            dfs = [pd.DataFrame({'freq': f, 'sens': s}) for f, s, *rest in self.raw_data]
            big = pd.concat(dfs, ignore_index=True).sort_values('freq')
            self.bandwidth = self._compute_bandwidth(big['freq'], big['sens'])
        elif mode == "overlaid":
            self._plot_overlaid()
            # self.bandwidths already set
        elif mode == "single":
            self._plot_single()
            self.bandwidth = self.bandwidths[0]
        else:
            raise ValueError(f"Unknown mode {mode!r}")
        return self.canvas

    def _prepare_figure(self):
        # Use constrained layout for proper insets
        self.fig, self.ax = plt.subplots(constrained_layout=True, figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)
        # Load logo
        img = Image.open(self.resource_path("images/fus_icon_transparent.png"))
        self.fus_icon = np.array(img)
        # Axis styling
        self.ax.xaxis.set_major_locator(MultipleLocator(0.2))
        self.ax.xaxis.set_major_formatter(ScalarFormatter())
        self.ax.ticklabel_format(style="plain", axis="x")
        self.ax.grid(True, color="#dddddd")

    def _finalize_plot(self, title: str):
        self.ax.set_title(title)
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("Sensitivity (V/MPa)")
        ax_img = self.fig.add_axes([0.85, 0.75, 0.12, 0.12])
        ax_img.imshow(self.fus_icon)
        ax_img.axis("off")

    def _plot_single(self):
        freq, sens, *rest = self.raw_data[0]
        self.ax.plot(freq, sens/1000,
                     marker='o', linestyle='-', color='black',
                     markerfacecolor='#73A89E', markeredgecolor='black',
                     linewidth=2, markersize=8)
        half = max(sens)/2/1000
        hl = self.ax.axhline(y=half, linestyle='--', color='#3b5e58')
        hl.set_dashes([10,5])
        self._finalize_plot("Hydrophone Sensitivity")

    def _plot_overlaid(self):
        cols = self.generate_color_palette('#73A89E', len(self.raw_data))
        for i, (freq, sens, *rest) in enumerate(self.raw_data):
            self.ax.plot(freq, sens/1000,
                         marker='o', linestyle='-', color='black',
                         markerfacecolor=cols[i], markeredgecolor='black',
                         alpha=0.7, linewidth=1, markersize=8,
                         label=f"{self.transducer_serials[i]}" if self.transducer_serials else f"Dataset {i+1}")
        self.ax.legend()
        self._finalize_plot("Hydrophone Sensitivity (Overlaid)")

    def _plot_appended(self):
        dfs = [pd.DataFrame({'freq': f, 'sens': s}) for f, s, *rest in self.raw_data]
        big = pd.concat(dfs, ignore_index=True).sort_values('freq')
        self.ax.plot(big['freq'], big['sens']/1000,
                     marker='o', linestyle='-', color='black',
                     markerfacecolor='#73A89E', markeredgecolor='black',
                     linewidth=2, markersize=8
                     )
        half = big['sens'].max()/2/1000
        hl = self.ax.axhline(y=half, linestyle='--', color='#3b5e58')
        hl.set_dashes([10,5])
        self._finalize_plot("Hydrophone Sensitivity (Combined)")

    def generate_color_palette(self, base_color, num_colors):
        brgb = to_rgb(base_color)
        return [to_hex((brgb[0]*(1 - i/num_colors),
                        brgb[1]*(1 - i/num_colors),
                        brgb[2]*(1 - i/num_colors)))
                for i in range(num_colors)]

    def resource_path(self, relative_path):
        base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        return os.path.join(base, relative_path)

# UI usage remains as before; ensure print_graphs_clicked references self.hydrophone_object.transducer_serials, .bandwidths, and .bandwidth correctly.
