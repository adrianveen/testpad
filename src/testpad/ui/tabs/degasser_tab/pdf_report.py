
from pathlib import Path
from PySide6.QtGui import QPdfWriter, QPainter, QFont, QPageSize, QGuiApplication
from PySide6.QtCore import QMarginsF, QRectF
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from typing import List
# from .config import (
#         DEFAULT_TEST_DESCRIPTIONS,
#         DS50_SPEC_RANGES,
#         DS50_SPEC_UNITS
# )


class GenerateReport:
    def __init__(
            self,
            metadata: dict,
            test_data: dict,
            time_series: List,
            figure: FigureCanvas,
            output_dir: Path
    ):

        self.metadata = metadata
        self.test_data = test_data
        self.time_series = time_series
        self.figure = figure
        self.output_dir = output_dir
        # self.serial_num = metadata['serial']
        self.pdf_writer = None
        self.painter = None
        

    def generate_report(self):
        """Call the draw functions and exports the report.

        Args:

        Returns:
            pdf object
        """
        filename = Path(self.output_dir) / 'report-pdf.pdf'
        filename = str(filename)
        self.pdf_writer = QPdfWriter(filename)
        self.draw_report_base(margins=5)
        self.painter = QPainter(self.pdf_writer)
        
        # Define starting position, and track with each drawing helper
        y = self.mm_to_pixels(10) # Start 20 mm from the top
        # Call remaining draw methods
        y = self.draw_header(y)
        y = self.draw_metadata(y)
        y = self.draw_test_table([], y)

        # Save PDF to the output path

        self.painter.end()
        
    def draw_report_base(self, margins: float):
        """Initializes the report object and draws the report skeleton such as margins.

        Args:
            margin(float): Margin values specified by the config.
        """
        self.pdf_writer.setPageSize(QPageSize(QPageSize.A4))
        self.pdf_writer.setPageMargins(QMarginsF(margins, margins, margins, margins))

    def draw_header(self, y_start: int = 0):
        """Draws the header for the report 
        which includes company name and logo
        
        Args:
            logo: image attribute used for the logo. 

        """
        self.painter.drawText(self.mm_to_pixels(10), y_start, "FUS Instruments")
        
        # Calculate height used
        header_height = self.mm_to_pixels(10) # 30 mm tall
        spacing = self.mm_to_pixels(5)        # 5 mm gap after
        
        return y_start + header_height + spacing
        
    def draw_metadata(self, y_start, metadata: dict | None = None):
        """Draws the 2 x 2 meta data table and the report title.
        
        Args:
            metadata(dict): Metadata dictionary containing test name, location, date and degasser serial # 

        Returns:
            New y location for drawing next report section.
        """
        if metadata is not None:
            tester = metadata['tester']
            date = metadata['date']
            location = metadata['location']
            serial_num = metadata['serial']
        # Draw the report title
        title_y = y_start
        first_row = title_y + self.mm_to_pixels(10)
        second_row = first_row + self.mm_to_pixels(5)
        first_col = self.mm_to_pixels(10)
        second_col = self.mm_to_pixels(135)
        self.painter.drawText(self.mm_to_pixels(75), title_y, "FUS DS-50 Test Report version 2025.0.5")
        self.painter.drawText(first_col, first_row, "Tester:")
        self.painter.drawText(first_col, second_row, "DS-50 Serial Number:")
        self.painter.drawText(second_col, first_row, "Date:")
        self.painter.drawText(second_col, second_row, "Location:")
        
        spacing = self.mm_to_pixels(5)
        return second_row + spacing

    def draw_test_table(self, test_data: list = [], y_start: float = 0) -> float:
        """Draws the 8 row x 5 col table for the test results and default values.

        Args:
            test_data: Dictionary of the measured data as well as all pass/fail inputs
            y_start: Y location to start drawing the table.
        Returns:
            New y location for drawing next report section.
        """
        table_top = y_start
        table_top_offset = self.mm_to_pixels(10)
        cell_width = self.mm_to_pixels(30)
        cell_height = self.mm_to_pixels(10)

        headers = ["Test Procedure/Description", "Pass/Fail", "Spec_Min", "Spec_Max", "Data Measured"]

        for i, header in enumerate(headers):
            x = table_top_offset + i * cell_width
            if i == 0:
                cell_width = self.mm_to_pixels(40)
            self.draw_cell(x, table_top, cell_width, cell_height, header)
        # self.painter.drawRect(table_top_offset, table_top, cell_width, cell_height)
        # self.painter.drawText(table_top_offset + 5, table_top + cell_height/2, headers[0])

        # self.painter.drawRect(table_top_offset + cell_width, table_top, 0.8 * cell_width, cell_height)
        # self.painter.drawText(table_top_offset + cell_width + 10, table_top + cell_height/2, headers[1])

        # self.painter.drawRect(table_top_offset + (cell_width + 0.8 * cell_width), table_top, cell_width, cell_height)
        # self.painter.drawText(table_top_offset + (cell_width + 0.8 * cell_width) + 10, table_top + cell_height/2, headers[2])

        # self.painter.drawRect(table_top_offset + (cell_width * 2 + 0.8 * cell_width), table_top, cell_width, cell_height)
        # self.painter.drawText(table_top_offset + (cell_width * 2 + 0.8 * cell_width) + 10, table_top + cell_height/2, headers[3])

        # self.painter.drawRect(table_top_offset + (cell_width * 3 + 0.8 * cell_width), table_top, cell_width, cell_height)
        # self.painter.drawText(table_top_offset + (cell_width * 3 + 0.8 * cell_width) + 10, table_top + cell_height/2, headers[4])

        spacing = self.mm_to_pixels(5)
        return table_top + (cell_height * 8) + spacing

    def draw_cell(
            self,
            x: float,
            y: float,
            width: float,
            height: float,
            text: str) -> None:
        """Draws a cell in the test results table.

        Args:
            x (float): X position of the cell.
            y (float): Y position of the cell.
            width (float): Width of the cell.
            height (float): Height of the cell.
            text (str): Text to display in the cell.
        """
        self.painter.drawRect(x, y, width, height)
        self.painter.drawText(x + 5, y + height / 2, text)

    def draw_time_series_table(self) -> None:
        """Draws the 2 x 11 time series table with a title above it.

        Args:
            data: 2D array of time series data
        """


    def draw_figure(self):
        """Adds the matplot lib figure to the PDF report.
        """

    def mm_to_pixels(self, mm: int):
        """Converts mm to pixels for more intutitive placement.
        Args:
            mm (float): function call passes a float of mm

        Returns:
            pixels (int): Returns a pixel value as an int
        """
        # Assuming 1200 DPI for QPdfwriter resolution
        dpi = self.pdf_writer.resolution()
        # 1 inch = 25.4 mm
        pixels = int((mm / 25.4) * dpi)
        return pixels

if __name__ == "__main__":
    home = Path.home()
    output_dir = Path(f"{home}/Documents/FUS Instruments/Testpad/")
    print(output_dir)
    if not output_dir.is_dir():
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir)
    app = QGuiApplication()
    report = GenerateReport({0:0}, {0:0}, [], None, output_dir)

    report.generate_report()
