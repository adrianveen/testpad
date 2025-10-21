from pathlib import Path
from typing import Any, Dict
import os

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
from testpad.ui.tabs.degasser_tab.plotting import make_time_series_figure, save_figure_to_temp_file
from testpad.ui.tabs.degasser_tab.report_layout import DEFAULT_LAYOUT, DEFAULT_FIGURE_CONFIG


class GenerateReport:
    """Generates a PDF report for the Degasser Test results.
    
    Attributes:
        metadata (Dict[str, Any]): Metadata for the test report.
        test_data (dict): Test data for the report.
        time_series (Dict[int, float]): Time series data for the report.
        figure (FigureCanvas): Matplotlib figure to include in the report.
        temperature (float): Temperature at which the test was conducted.
        output_dir (Path): Directory to save the generated PDF report.
        time_series_y (float): Y location tracker for time series table.

    **Methods**:
        **generate_report()**: Generates and saves the PDF report.
        **build_report_base(margins: float)**: Initializes the PDF report with margins.
        **build_header()**: Draws the header for the report.
        **build_title_block(metadata: dict | None = None)**: Draws the title block with metadata
        **build_test_table(test_data: list = [])**: Draws the test results table.
        **build_time_series_table(data: dict[int, float])**: Draws the time series data table
        **add_figure()**: Adds the matplotlib figure to the PDF report.
        **dummy_figure()**: Generates a dummy matplotlib figure for testing.
    """
    def __init__(
            self,
            metadata: Dict[str, Any],
            test_data: dict,
            time_series: Dict[int, float],
            temperature: float,
            output_dir: Path,
            figure: FigureCanvas | None = None
    ) -> None:

        self.metadata = metadata
        self.test_data = test_data
        self.time_series = time_series
        self.temperature = temperature
        self.output_dir = output_dir
        
        # Layout configuration
        self.layout = DEFAULT_LAYOUT
        self.figure_config = DEFAULT_FIGURE_CONFIG

        # Y location trackers
        self.time_series_y = 0

    def generate_report(self):
        """Call the draw functions and exports the report.

        Args:

        Returns:
            pdf object
        """
        filename = Path(self.output_dir) / 'report-pdf.pdf'
        filename = str(filename)

        # Call remaining draw methods
        self.build_report_base(self.layout.left_margin_mm)
        self.build_header()
        self.build_title_block(self.metadata)
        self.build_test_table([])
        self.build_time_series_table(self.time_series)
        
        # Create and add figure using new design
        self._add_time_series_figure()

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

    def build_time_series_table(self, data: dict[int, float]) -> None:
        """Draws the 2 x 11 time series table with a title above it.

        Args:
            data: 2D array of time series data
        """
        self.pdf.ln(10)
        title = "Dissolved Oxygen Re-circulation Test (1000 mL)"
        self.pdf.cell(
            text=title,
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT"
        )
        self.pdf.ln(5)
        self.time_series_y = self.pdf.get_y()

        self.pdf.ln(5)
        col_names = ['Time (min)', 'Dissolved Oxygen (mg/L)']
        with self.pdf.table(col_widths=(30), align="L") as table:
            header_row = table.row()
            for col_name in col_names:
                header_row.cell(col_name)

            for time, do_value in data.items():
                row = table.row()
                row.cell(str(time), align="C")
                row.cell(str(do_value), align="C")
        self.pdf.ln(5)
        self.pdf.cell(text=f"Temperature: {self.temperature} °C", align="L")

    def add_figure(self, fig: FigureCanvas, figure_path: Path) -> None:
        """Adds the matplot lib figure to the PDF report.
        """
        left_margin = self.pdf.l_margin
        current_y = self.time_series_y

        # Determine placement for the figure to the right of the table.
        fig_width_in, fig_height_in = fig.get_size_inches()
        available_width = (self.pdf.w - self.pdf.r_margin) - (left_margin + 70)
        figure_width = available_width
        figure_height = figure_width * (fig_height_in / fig_width_in)

        figure_x = left_margin + 75  # table width plus gap
        figure_y = current_y
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

        #figure_bottom_y = figure_y + figure_height
        #self.pdf.set_y(max(table_bottom_y, figure_bottom_y) + 8)
        self.pdf.set_font(style="B", size=10)

    def _add_time_series_figure(self) -> None:
        """Create and add time series figure using the new design.
        
        This method uses the pure plotting function and layout configuration
        to create a properly sized figure for the PDF.
        """
        # Calculate optimal figure dimensions
        page_width_mm = self.pdf.w
        figure_width_mm = self.layout.calculate_figure_width(page_width_mm)
        figure_x, _ = self.layout.get_figure_position(page_width_mm)
        
        # Calculate figure size in inches for matplotlib
        figure_width_inches, figure_height_inches = self.figure_config.calculate_size_for_width(figure_width_mm)
        
        # Create the figure using pure plotting function
        figure = make_time_series_figure(
            data=self.time_series,
            temperature_c=self.temperature,
            size_inches=(figure_width_inches, figure_height_inches),
            dpi=self.figure_config.dpi
        )
        
        # Save to temporary file
        temp_path = save_figure_to_temp_file(figure, str(self.output_dir))
        
        try:
            # Calculate figure height in mm for PDF
            figure_height_mm = figure_width_mm * (figure_height_inches / figure_width_inches)
            
            # Add to PDF
            self.pdf.image(
                temp_path,
                x=figure_x,
                y=self.time_series_y,
                w=figure_width_mm,
                h=figure_height_mm
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def dummy_figure(self) -> FigureCanvas:
        """Generates a dummy matplotlib figure for testing purposes.

        Returns:
            FigureCanvas: A simple matplotlib figure.
        """
        # Generate dummy data for the figure.
        minutes = list(range(0, 11))
        oxygen = [10 - (0.45 * idx) for idx in minutes]

        fig, ax = plt.subplots(figsize=(4.5, 4))
        ax.plot(minutes, oxygen, marker="o", color="#1f77b4")
        ax.set_title("DUMMY PLOT - Dissolved Oxygen Over Time")
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
    if not time_series:
            example_data = {
                1: 8.65,
                2: 7.64,
                3: 5.60,
                4: 4.62,
                5: 3.58,
                6: 2.99,
                7: 2.55,
                8: 2.33,
                9: 2.16,
                10: 2.05,
                11: 1.00
            }
            time_series = example_data

    test_data = data_dict['test_table']
    temp = data_dict['temperature_c']
    # Create default output directory
    output_dir = DEFAULT_EXPORT_DIR
    # Generate the report
    report = GenerateReport(
        metadata=metadata,
        test_data=test_data,
        time_series=time_series,
        temperature=temp,
        output_dir=output_dir
    )
    report.generate_report()
