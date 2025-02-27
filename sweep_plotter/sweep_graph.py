import h5py
import numpy as np
import os
import sys
import re
from pathlib import Path
from numpy import fft as fft
from pprint import pprint
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import to_rgb, to_hex
from matplotlib.backends.backend_qtagg import FigureCanvas

class SweepGraph():
    def __init__(self, hdf5_file, time_delta=16e-9):
        
        self.hdf5_file = hdf5_file
        self.scan_data = []
        self.time_delta = time_delta
        self.harmonic_folder = ''
        self.serial_no = ''
        # check if hdf5_file is None
        if hdf5_file is None:
            raise ValueError("No file selected")
        
        # process the file and store the data
        self.raw_data = self._process_files(hdf5_file)

    def resource_path(self, relative_path):
        """Get the absolute path to a resource"""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        full_path = os.path.join(base_path, relative_path)
        return full_path
    
    def load_icon(self, path):
        image = Image.open(path)
        image_array = np.array(image)
        return image_array
    # Generate a color palette based on the base color provided
    def generate_color_palette(self, base_color, num_colors):
        base_rgb = to_rgb(base_color)
        palette = [to_hex((base_rgb[0] * (1 - i / num_colors), 
                           base_rgb[1] * (1 - i / num_colors), 
                           base_rgb[2] * (1 - i / num_colors))) for i in range(num_colors)]
        return palette
    
    def _process_files(self, file_paths):
        """
        Process one or more HDF5 files and extract relevant data. Currently only supports one HDF5 file at a time
        
        Args:
            file_paths (str or list of str): Single file path or a list of file paths.
            
        Returns:
            list: A list of pandas DataFrames, where each DataFrame contains the raw pressure waveform data.
        """
        # Ensure file_paths is always a list
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # The harmonic folder is one level up from the file's directory
        # print(file_paths)
        first_path = Path(file_paths[0])
        harmonic_folder = first_path.parent.parent.name
        pattern = r'^\d+(?:st|nd|rd|th) Harmonic$'
        if re.match(pattern, harmonic_folder, re.IGNORECASE):
            self.harmonic_folder = harmonic_folder
        else:
            raise ValueError(
                f"Unexpected harmonic folder name: '{harmonic_folder}'. "
                "Expected format like '1st Harmonic', '2nd Harmonic', etc."
            )
        
        filename = first_path.name
        # extract serial number from file name - all text up to second underscore
        #replace the first underscore with a hyphen
        first_path_modified = filename.replace('_', '-', 1)
        self.serial_no, _ = first_path_modified.split("_", 1)
        # print(f"Transducer serial number: {self.serial_no}")

        for file_path in file_paths:
            try:
                with h5py.File(file_path, 'r') as f:
                    # Access the Scan group
                    scan_group = f['Scan']
                    # Extract the raw pressure waveform data
                    raw_pressure_waveforms = scan_group['Raw pressure waveforms (Pa)'][:]
                    # Convert the data into a pandas DataFrame
                    df = pd.DataFrame(raw_pressure_waveforms)
                    # Append the DataFrame to raw_data
                    self.scan_data.append(df)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        return self.scan_data
    
    def get_graphs(self, trace_index, graph_type='time'):
        """
        Generate a graph based on the selected trace for both the time domain and frequency domain.
        
        Args:
            trace_no (int): The trace number to plot.
            graph_type (str): The type of graph to plot. Options are 'time' or 'fft'.
            
        Returns:
            tuple: A tuple containing the time domain and frequency domain graphs as FigureCanvas objects.
        """
        # load FUS icon
        image_path = self.resource_path("images\\fus_icon_transparent.png")
        image = self.load_icon(image_path)

        selected_trace = str(trace_index + 1) # convert trace selection into string
        num_data_pts = self.scan_data[0].shape[1] # extract number of samples taken
        time = np.arange(0, 16*num_data_pts, 16) # time in ns
        time_ms = time / 1e6 # convert to ms

        raw_pressure_waveform = self.scan_data[0]

        # generate canvases for time domain and fft
        self.fig_time, self.ax_time = plt.subplots(figsize=(10, 6))
        self.canvas_time = FigureCanvas(self.fig_time)
        self.fig_fft, self.ax_fft = plt.subplots(figsize=(10, 6))
        self.canvas_fft = FigureCanvas(self.fig_fft)

        # extract the waveform selected by the user
        selected_waveform = raw_pressure_waveform.iloc[trace_index] / 1e6

        # time domain trace
        self.ax_time.plot(
            time_ms,
            selected_waveform,
            label=f"{self.harmonic_folder} - Trace #{selected_trace}",
            color='#73A89E'
            )
        self.ax_time.set_xlabel("Time (ms)")
        self.ax_time.set_ylabel("Pressure (MPa)")
        self.ax_time.set_title(f"Pressure Waveform in the Time Domain - {self.serial_no}")
        self.ax_time.legend(handlelength=0, handletextpad=1, loc='upper left')
        self.ax_time.grid(True)

        # FFT
        # apply hanning window to the selected waveform
        window_fft = np.hanning(num_data_pts)

        real_fft_magnitude = np.fft.rfft(selected_waveform * window_fft, axis=0)

        fft_wf = np.abs(2 * 2 * real_fft_magnitude / num_data_pts) / 1e6 # MPa
        fft_freq_mhz = np.fft.rfftfreq(n=num_data_pts, d=self.time_delta) / 1e6 # MHz
        # remove all values greater than 5 MHz
        fft_freq_mhz = fft_freq_mhz[fft_freq_mhz <= 5]
        # limit fft_wf to the same size as fft_freq_mhz
        fft_wf = fft_wf[:len(fft_freq_mhz)]

        # normalize fft_wf to the maximum value
        fft_wf = fft_wf / np.max(fft_wf)

        # fft plot
        self.ax_fft.plot(
            fft_freq_mhz,
            fft_wf,
            label=f"{self.harmonic_folder} - Trace #{selected_trace}",
            color='#73A89E'
            )
        self.ax_fft.set_xlabel("Frequency (MHz)")
        self.ax_fft.set_ylabel("Normalized Pressure Amplitude")
        self.ax_fft.set_title(f"Frequency Spectrum of the Pressure Waveform - {self.serial_no}")
        self.ax_fft.legend(handlelength=0, handletextpad=1, loc='upper left')
        self.ax_fft.grid(True)

        # add image to plot area for both time domain and fft
        image_xaxis, image_yaxis = 0.82, 0.77
        image_width, image_height = 0.09, 0.09

        ax_image_fft = self.fig_fft.add_axes([image_xaxis, image_yaxis, image_width, image_height])
        ax_image_time = self.fig_time.add_axes([image_xaxis, image_yaxis, image_width, image_height])
        ax_image_fft.imshow(image)
        ax_image_time.imshow(image)
        ax_image_fft.axis('off')
        ax_image_time.axis('off')

        return self.canvas_time, self.canvas_fft