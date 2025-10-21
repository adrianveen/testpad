from pathlib import Path
from typing import List

from fpdf import FPDF, Align
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import pyplot as plt

from testpad.config.defaults import DEFAULT_EXPORT_DIR
from testpad.ui.tabs.degasser_tab.config import (
         DEFAULT_TEST_DESCRIPTIONS,
         DS50_SPEC_RANGES,
         DS50_SPEC_UNITS
)
from testpad.ui.tabs.degasser_tab.model import DegasserModel


class GenerateReport:
    def __init__(
            self,
            metadata: dict,
            test_data: dict,
            time_series: List,
            figure: FigureCanvas,
            temperature: float,
            output_dir: Path
    ) -> None:

        self.metadata = metadata
        self.test_data = test_data
        self.time_series = time_series
        self.figure = figure
        self.temperature = temperature
        self.output_dir = output_dir   

    def generate_report(self):
        """Call the draw functions and exports the report.

        Args:

        Returns:
            pdf object
        """
        filename = Path(self.output_dir) / 'report-pdf.pdf'
        filename = str(filename)

        # Call remaining draw methods
        self.build_report_base(15)
        self.build_header()
        self.build_title_block(self.metadata)
        self.build_test_table([])
        self.build_time_series_table()
        self.add_figure()

        # Save PDF to the output path
        # Make the directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.pdf.output(filename)

    def build_report_base(self, margins: float):
        """Initializes the report object and draws the report skeleton such as margins.

        Args:
            margin(float): Margin values specified by the config.
        """
        self.pdf = FPDF(orientation="P", unit="mm", format="letter")
        self.pdf.add_page()
        self.pdf.set_margins(left=margins, top=margins, right=margins)
        self.pdf.set_font("helvetica", size=12)     

    def build_header(self):
        """Draws the header for the report 
        which includes company name and logo
        
        Args:
            logo: image attribute used for the logo. 

        """
        self.pdf.set_font(style="B", size=16)
        self.pdf.cell(
            text="FUS Instruments",
            align="L",
            new_x="RIGHT",
            new_y="NEXT"
        )


    def build_title_block(self, metadata: dict | None = None):
        """Draws the 2 x 2 meta data table and the report title.
        
        Args:
            metadata(dict): Metadata dictionary containing test name, location, date and degasser serial # 

        Returns:
            New y location for drawing next report section.
        """
        # DEBUG SHOW METADATA
        print(f"[DEBUG] Metadata for report title block:{metadata}")
        # Convert keys to more user-friendly labels
        metadata = {
            'Tester': metadata.get('tester_name', ''),
            'Date': metadata.get('test_date', ''),
            'DS-50 Serial Number': metadata.get('ds50_serial', ''),
            'Location': metadata.get('location', '')
        }

        self.pdf.set_font(style="B", size=16)
        # Draw the report title
        self.pdf.ln(5) # Add spacing after header
        self.pdf.cell(
            text="FUS DS-50 Test Report version 2025.0.4",
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT"
        )
        # Add spacing in mm
        self.pdf.ln(5)

        values = list(metadata.items())
        rows = [values[i:i+2] for i in range(0, len(values), 2)]

        self.pdf.set_font(style="B", size=10)

        with self.pdf.table(col_widths=(90), align="L") as table:
            for pair in rows:
                row = table.row()
                for label, value in pair:
                    cell_text = f"{label}: {value}"
                    row.cell(cell_text, border=False)
                # If odd number of fields, pad the last line
                if len(pair) < 2:
                    row.cell("")

    def build_test_table(self, test_data: list = []):
        """Draws the 8 row x 5 col table for the test results and default values.

        Args:
            test_data: Dictionary of the measured data as well as all pass/fail inputs
            y_start: Y location to start drawing the table.
        Returns:
            New y location for drawing next report section.
        """
        headers = ["Test Procedure/Description", "Pass/Fail", "Spec_Min", "Spec_Max", "Data Measured"]
        descriptions = DEFAULT_TEST_DESCRIPTIONS
        self.pdf.ln(5) # Add a spacer before the data table
        len(headers)
        

        with self.pdf.table(col_widths=(40, 25, 25, 25, 25)) as table:
            header_row = table.row()
            for header in headers:
                header_row.cell(header, Align.C)
            # Descriptions
            for descr in descriptions:
                row = table.row()
                row.cell(descr, align="L")
                row.cell("")
                row.cell("")
                row.cell("")
                row.cell("")

    def build_time_series_table(self) -> None:
        """Draws the 2 x 11 time series table with a title above it.

        Args:
            data: 2D array of time series data
        """
        example_data = {
            0: '10',
            1: '8.5',
            2: '7.2',
            3: '6.8',
            4: '6.5',
            5: '6.2',
            6: '6.0',
            7: '5.8',
            8: '5.6',
            9: '5.5',
            10: '5.4'
        }
        self.pdf.ln(10)
        title = "Dissolved Oxygen Re-circulation Test (1000 mL)"
        self.pdf.cell(
            text=title,
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT"
        )
        self.pdf.ln()

        col_names = ['Time (min)', 'Dissolved Oxygen (mg/L)']
        with self.pdf.table(col_widths=(30), align="L") as table:
            header_row = table.row()
            for col_name in col_names:
                header_row.cell(col_name)

            for time, do_value in example_data.items():
                row = table.row()
                row.cell(str(time), align="C")
                row.cell(do_value, align="C")
        self.pdf.ln(5)
        self.pdf.cell(text=f"Temperature: {self.temperature} °C", align="L")

    def add_figure(self) -> None:
        """Adds the matplot lib figure to the PDF report.
        """
        left_margin = self.pdf.l_margin
        current_y = self.pdf.get_y()

        # Draw the existing time-series table on the left side.
        # self.pdf.set_xy(left_margin, current_y)
        table_top_y = current_y + 10  # build_time_series_table lns down before drawing
        # self.build_time_series_table()
        table_bottom_y = self.pdf.get_y()

        # create dummy figure
        fig, figure_path = self.dummy_figure()

        # Determine placement for the figure to the right of the table.
        fig_width_in, fig_height_in = fig.get_size_inches()
        base_figure_width = 90  # mm
        available_width = (self.pdf.w - self.pdf.r_margin) - (left_margin + 70)
        figure_width = min(base_figure_width, max(30, available_width))
        figure_height = figure_width * (fig_height_in / fig_width_in)

        figure_x = left_margin + 70  # table width plus gap
        figure_y = table_top_y
        self.pdf.image(
            str(figure_path),
            x=figure_x,
            y=figure_y,
            w=figure_width,
            h=figure_height
        )

        plt.close(fig)
        try:
            figure_path.unlink()
        except OSError:
            pass

        figure_bottom_y = figure_y + figure_height
        self.pdf.set_y(max(table_bottom_y, figure_bottom_y) + 8)
        self.pdf.set_font(style="B", size=10)

    def dummy_figure(self) -> FigureCanvas:
        """Generates a dummy matplotlib figure for testing purposes.

        Returns:
            FigureCanvas: A simple matplotlib figure.
        """
        # Generate dummy data for the figure.
        minutes = list(range(0, 11))
        oxygen = [10 - (0.45 * idx) for idx in minutes]

        fig, ax = plt.subplots(figsize=(4.5, 3.0))
        ax.plot(minutes, oxygen, marker="o", color="#1f77b4")
        ax.set_title("Dissolved Oxygen Over Time")
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Dissolved Oxygen (mg/L)")
        ax.grid(True, linestyle="--", linewidth=0.5)

        figure_path = Path(self.output_dir) / "temp_figure.png"
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(figure_path, dpi=150)
        return fig, figure_path


if __name__ == "__main__":
    # Example Usage
    # Create a DegasserModel instance with sample data
    _model = DegasserModel()
    # Get the data from the model
    data_dict = _model.to_dict()
    # Extract relevant data
    metadata = data_dict['metadata']
    time_series = data_dict['time_series']
    test_data = data_dict['test_table']
    temp = data_dict['temperature_c']
    # Create default output directory
    output_dir = DEFAULT_EXPORT_DIR
    # Generate the report
    report = GenerateReport(metadata, time_series, test_data, None, temp, output_dir)
    report.generate_report()
