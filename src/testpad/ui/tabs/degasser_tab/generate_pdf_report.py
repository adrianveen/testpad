from pathlib import Path
from typing import Any, Dict, Optional
import os

from fpdf import FPDF, Align

from testpad.config.defaults import DEFAULT_EXPORT_DIR
from testpad.ui.tabs.degasser_tab.config import (
        DEFAULT_TEST_DESCRIPTIONS,
        NO_LIMIT_SYMBOL,
        ROW_SPEC_MAPPING,
        TEST_TABLE_HEADERS,
        REPORT_VERSION,
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
        temperature (float): Temperature at which the test was conducted.
        output_dir (Path): Directory to save the generated PDF report.
        time_series_y (float): Y location tracker for time series table.

    Methods:
        - generate_report(): Generates and saves the PDF report.
        - _build_report_base(margins: float): Initializes the PDF report with margins.
        - _build_header(): Draws the header for the report.
        - _build_title_block(metadata: dict | None = None): Draws the title block with metadata
        - _build_test_table(test_data: list = []): Draws the test results table.
        - _build_time_series_table(data: dict[int, float]): Draws the time series data table
    """
    def __init__(
            self,
            metadata: Dict[str, Any],
            test_data: dict,
            time_series: Dict[int, float],
            temperature: Optional[float],
            output_dir: Path
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
        self._build_report_base(self.layout.left_margin_mm)
        self._build_header()
        self._build_title_block(self.metadata)
        self._build_test_table(self.test_data)
        self._build_time_series_table(self.time_series)
        
        # Create and add figure using new design
        self._add_time_series_figure()

        # Save PDF to the output path
        # Make the directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.pdf.output(filename)

    def _build_report_base(self, margins: float):
        """Initializes the report object and draws the report skeleton such as margins.

        Args:
            margin(float): Margin values specified by the config.
        """
        self.pdf = FPDF(orientation="P", unit="mm", format="letter")
        self.pdf.add_page()
        self.pdf.set_margins(left=margins, top=margins, right=margins)
        self.pdf.set_font("helvetica", size=12)     

    def _build_header(self):
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


    def _build_title_block(self, metadata: dict):
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
            text=f"FUS DS-50 Test Report version {REPORT_VERSION}",
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

    def _build_test_table(self, test_data: dict):
        """Draws the 8 row x 5 col table for the test results and default values.

        Args:
            test_data: Dictionary of the measured data as well as all pass/fail inputs
            y_start: Y location to start drawing the table.
        Returns:
            New y location for drawing next report section.
        """
        headers = TEST_TABLE_HEADERS
        self.pdf.ln(5) # Add a spacer before the data table

        with self.pdf.table(col_widths=(40, 25, 25, 25, 25)) as table:
            header_row = table.row()
            for header in headers:
                header_row.cell(header, Align.C)
            # Test Results and Headers
            for idx, test_row_dict in enumerate(test_data):
                row = table.row()

                # Column 1: Description
                row.cell(test_row_dict['description'], align="L")

                # Column 2: Pass/Fail
                pas_fail_text = test_row_dict.get('pass_fail','') or ''
                row.cell(pas_fail_text, align="C")

                # Get specs from config
                spec_key = ROW_SPEC_MAPPING[idx]
                spec = DS50_SPEC_RANGES.get(spec_key, (None, None)) if spec_key else (None, None)
                units = DS50_SPEC_UNITS.get(spec_key, (None, None)) if spec_key else ""

                # Column 3: Spec_Min
                if spec[0] is not None:
                    if isinstance(spec[0], float):
                        spec_min_text = f"{spec[0]:.2f} {units}"
                    else:
                        spec_min_text = f"{spec[0]} {units}"
                else:
                    spec_min_text = NO_LIMIT_SYMBOL
                row.cell(spec_min_text, align="C")

                # Column 4: Spec_Max 
                if spec[1] is not None:
                    if isinstance(spec[1], float):
                        spec_max_text = f"{spec[1]:.2f} {units}"
                    else:
                        spec_max_text = f"{spec[1]} {units}"
                else:
                    spec_max_text = NO_LIMIT_SYMBOL
                row.cell(spec_max_text, align="C")

                # Column 5: Data Measured
                data_measured = test_row_dict.get('measured')
                if isinstance(data_measured, float):
                    data_measured_text = f"{data_measured:.2f} {units}" if data_measured is not None else NO_LIMIT_SYMBOL
                else:
                    data_measured_text = f"{data_measured}" if data_measured is not None else NO_LIMIT_SYMBOL
                row.cell(data_measured_text, align="C")

    def _build_time_series_table(self, data: dict[int, float]) -> None:
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
                row.cell(f"{do_value:.2f}", align="C")
        self.pdf.ln(5)
        self.pdf.cell(text=f"Temperature: {self.temperature} °C", align="L")

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
