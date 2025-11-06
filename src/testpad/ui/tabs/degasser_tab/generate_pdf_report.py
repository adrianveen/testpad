"""Report generation for the Degasser Tab."""

import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF, Align, FontFace

from testpad.config.defaults import DEFAULT_EXPORT_DIR, DEFAULT_FUS_LOGO_PATH
from testpad.ui.tabs.degasser_tab.config import (
    DS50_SPEC_RANGES,
    DS50_SPEC_UNITS,
    NO_LIMIT_SYMBOL,
    REPORT_VERSION,
    ROW_SPEC_MAPPING,
    TEST_TABLE_HEADERS,
    TIME_SERIES_HEADERS,
)
from testpad.ui.tabs.degasser_tab.plotting import (
    make_time_series_figure,
    save_figure_to_temp_file,
)
from testpad.ui.tabs.degasser_tab.report_layout import (
    DEFAULT_FIGURE_CONFIG,
    DEFAULT_LAYOUT,
    DEFAULT_STYLE_CONFIG,
)


class GenerateReport:
    """Generates a PDF report for the Degasser Test results.

    Methods:
        - generate_report(): Generates and saves the PDF report.
        - _build_report_base(margins: float): Initializes the PDF report with margins.
        - _build_header(): Draws the header for the report.
        - _build_title_block(metadata: dict | None = None):
        Draws the title block with metadata
        - _build_test_table(test_data: list[dict[str, Any]]):
        Draws the test results table.
        - _build_time_series_table(data: dict[int, float]):
        Draws the time series data table

    """

    def __init__(
        self,
        metadata: dict[str, Any],
        test_data: list[dict[str, Any]],
        time_series: dict[int, float],
        temperature: float | None,
        output_dir: Path,
    ) -> None:
        """Initialize the GenerateReport class.

        Args:
            metadata (dict[str, Any]): Metadata dictionary containing test name,
                location, date, and degasser serial number.
            test_data (list[dict[str, Any]]): List of test data dictionaries
                for the report.
            time_series (dict[int, float]): Time series data for the report.
            temperature (float): Temperature at which the test was conducted.
            output_dir (Path): The path to the output PDF file.

        """
        self.metadata = metadata
        self.test_data = test_data
        self.time_series = time_series
        self.temperature = temperature
        self.output_dir = output_dir
        self.logo_path = DEFAULT_FUS_LOGO_PATH

        # Layout configuration
        self.layout = DEFAULT_LAYOUT
        self.figure_config = DEFAULT_FIGURE_CONFIG
        self.styling_config = DEFAULT_STYLE_CONFIG

        # Y location trackers
        self.time_series_y = 0

    def generate_report(self) -> None:
        """Call the draw functions and exports the report."""
        serial_num = self.metadata.get("ds50_serial", "").replace("#", "")
        filename = Path(self.output_dir) / f"FUS DS-50 Test Report-{serial_num}.pdf"
        filename = str(filename)

        # Call remaining draw methods
        self._build_report_base(self.layout.left_margin_mm)
        self._build_header(logo_path=self.logo_path)
        self._build_title_block(self.metadata)
        self._build_test_table(self.test_data)
        self._build_time_series_table(self.time_series)

        # Create and add figure
        self._add_time_series_figure()

        # Save PDF to the output path
        # Make the directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.pdf.output(filename)

    def _build_report_base(self, margins: float) -> None:
        """Initialize the report object and draws the report skeleton such as margins.

        Args:
            margins(float): Margin values specified by the config.

        """
        self.pdf = FPDF(orientation="P", unit="mm", format="letter")
        self.pdf.add_page()
        self.pdf.set_margins(left=margins, top=margins * 0.75, right=margins)
        self.pdf.set_font("helvetica", size=self.styling_config.header_text_size)

    def _build_header(self, logo_path: Path) -> None:
        """Draw the header for the report which includes company name and logo.

        Args:
            logo_path: Full path to the logo image file.

        """
        # Add FUS Logo
        self.pdf.image(
            str(logo_path),
            w=self.styling_config.logo_width_mm,
            keep_aspect_ratio=self.styling_config.logo_keep_aspect_ratio,
        )

    def _build_title_block(self, metadata: dict) -> None:
        """Draw the 2 x 4 metadata table and the report title.

        There is 1 col for each label and 1 for each field.

        Args:
            metadata(dict): Metadata dictionary containing test name,
            location, date and degasser serial #

        """
        # Convert keys to more user-friendly labels
        metadata = {
            "Tester": metadata.get("tester_name", ""),
            "Date": metadata.get("test_date", ""),
            "DS-50 Serial Number": metadata.get("ds50_serial", ""),
            "Location": metadata.get("location", ""),
        }

        self.pdf.set_font(
            style=self.styling_config.title_text_style,
            size=self.styling_config.title_text_size,
        )
        # Draw the report title
        self.pdf.ln(self.layout.title_spacing_mm)  # Add spacing after header
        self.pdf.cell(
            text=f"FUS DS-50 Test Report version {REPORT_VERSION}",
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT",
        )
        # Add spacing in mm
        self.pdf.ln(self.layout.title_spacing_mm)

        values = list(metadata.items())
        rows = [values[i : i + 2] for i in range(0, len(values), 2)]

        value_font_style = FontFace(
            emphasis=self.styling_config.metadata_text_style,
            size_pt=self.styling_config.metadata_text_size,
        )

        self.pdf.set_font(
            style=self.styling_config.subtitle_text_style,
            size=self.styling_config.metadata_text_size,
        )
        # Create a table for the title block
        # Calculate column widths for centering
        # Page width minus margins
        usable_width = self.pdf.w - (2 * self.layout.left_margin_mm)
        # Two equal-width content columns with small spacing between
        spacing_col = 10  # Space between the two metadata columns
        content_col = int((usable_width - spacing_col) / 2)

        with self.pdf.table(
            col_widths=(content_col, spacing_col, content_col),
            align=Align.C,
            markdown=True,
        ) as table:
            for pair in rows:
                row = table.row()
                # First column (left field)
                label, value = pair[0]
                if label == "Date":
                    # Value is already a Python date object (converted by model)
                    value = value.strftime("%Y-%m-%d")
                row.cell(
                    text=f"{label}: --{value}--",
                    border=False,
                    align=Align.C,
                    style=value_font_style,
                )
                # Spacing column
                row.cell(text="", border=False)
                # Second column (right field) - handle odd number of fields
                if len(pair) > 1:
                    label, value = pair[1]
                    if label == "Date":
                        value = value.strftime("%Y-%m-%d")
                    row.cell(
                        text=f"{label}: --{value}--",
                        border=False,
                        align=Align.C,
                        style=value_font_style,
                    )
                else:
                    # Odd number of fields, pad the last row
                    row.cell("", border=False)

    def _build_test_table(self, test_data: list[dict[str, Any]]) -> None:
        """Draws the 8 row x 5 col table for the test results and default values.

        Args:
            test_data: List of dictionaries containing measured data and pass/fail inputs

        """
        headers = TEST_TABLE_HEADERS
        # Set font styles for each section of the table
        header_style = FontFace(
            emphasis=self.styling_config.header_text_style,
            size_pt=self.styling_config.header_text_size,
            color=self.styling_config.header_text_color,
        )
        spec_style = FontFace(
            emphasis=self.styling_config.values_text_style,
            size_pt=self.styling_config.spec_text_size,
            color=self.styling_config.spec_text_color,
        )
        data_style = FontFace(
            emphasis=self.styling_config.values_text_style,
            size_pt=self.styling_config.data_text_size,
            color=self.styling_config.data_text_color,
        )

        self.pdf.ln(
            self.layout.section_spacing_mm,
        )  # Add a spacer before the data table

        with self.pdf.table(col_widths=(40, 25, 25, 25, 25)) as table:
            header_row = table.row()
            for header in headers:
                header_row.cell(header, Align.C, style=header_style)
            # Test Results and Headers
            for idx, test_row_dict in enumerate(test_data):
                row = table.row()

                # Column 1: Description
                row.cell(test_row_dict["description"], align="L", style=header_style)

                # Column 2: Pass/Fail
                pas_fail_text = test_row_dict.get("pass_fail", "") or ""
                row.cell(pas_fail_text, align="C", style=data_style)

                # Get specs from config
                spec_key = ROW_SPEC_MAPPING[idx]
                spec = (
                    DS50_SPEC_RANGES.get(spec_key, (None, None))
                    if spec_key
                    else (None, None)
                )
                units = (
                    DS50_SPEC_UNITS.get(spec_key, (None, None)) if spec_key else ""
                )

                # Column 3: Spec_Min
                if spec[0] is not None:
                    if isinstance(spec[0], float):
                        spec_min_text = f"{spec[0]:.2f} {units}"
                    else:
                        spec_min_text = f"{spec[0]} {units}"
                else:
                    spec_min_text = NO_LIMIT_SYMBOL
                row.cell(spec_min_text, align="C", style=spec_style)

                # Column 4: Spec_Max
                if spec[1] is not None:
                    if isinstance(spec[1], float):
                        spec_max_text = f"{spec[1]:.2f} {units}"
                    else:
                        spec_max_text = f"{spec[1]} {units}"
                else:
                    spec_max_text = NO_LIMIT_SYMBOL
                row.cell(spec_max_text, align="C", style=spec_style)

                # Column 5: Data Measured - set to gray
                data_measured = test_row_dict.get("measured")
                if isinstance(data_measured, float):
                    data_measured_text = (
                        f"{data_measured:.2f} {units}"
                        if data_measured is not None
                        else NO_LIMIT_SYMBOL
                    )
                else:
                    data_measured_text = (
                        f"{data_measured}"
                        if data_measured is not None
                        else NO_LIMIT_SYMBOL
                    )
                row.cell(data_measured_text, align="C", style=data_style)

    def _build_time_series_table(self, data: dict[int, float]) -> None:
        """Draws the 2 x 11 time series table with a title above it.

        Args:
            data: 2D array of time series data

        """
        # Add spacer
        self.pdf.ln(self.layout.section_spacing_mm)

        # Main title - bold, font 12
        self.pdf.set_font(
            style=self.styling_config.subtitle_text_style,
            size=self.styling_config.subtitle_text_size,
        )
        title = "Dissolved Oxygen Re-circulation Test"
        self.pdf.cell(
            text=title,
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT",
        )

        # Subtitle - non-bold, font 12
        self.pdf.set_font(
            style=self.styling_config.values_text_style,
            size=self.styling_config.subtitle_text_size,
        )
        self.pdf.cell(
            text="1000 mL Distilled Water",
            align=Align.L,
            center=True,
            new_x="RIGHT",
            new_y="NEXT",
        )

        # Add spacer and get current y position of table
        self.pdf.ln(self.layout.section_spacing_mm)
        self.time_series_y = self.pdf.get_y()

        # Define styles for table cells (FontFace only works in table context)
        header_style = FontFace(
            emphasis=self.styling_config.header_text_style,
            size_pt=self.styling_config.header_text_size,
        )
        data_style = FontFace(
            emphasis=self.styling_config.values_text_style,
            size_pt=self.styling_config.data_text_size,
            color=self.styling_config.data_text_color,
        )

        # Table with header row - bold, font 10
        col_names = TIME_SERIES_HEADERS
        with self.pdf.table(col_widths=(30), align="L") as table:
            header_row = table.row()
            for col_name in col_names:
                header_row.cell(col_name, style=header_style)
            for time, do_value in data.items():
                row = table.row()
                row.cell(str(time), align="C")
                row.cell(f"{do_value:.2f}", align="C", style=data_style)

        # Add spacer and add temperature
        self.pdf.ln(self.layout.section_spacing_mm / 2)
        self.pdf.set_font(
            style=self.styling_config.values_text_style,
            size=self.styling_config.data_text_size,
        )
        if self.temperature:
            self.pdf.cell(text=f"Temperature: {self.temperature} °C", align="L")

    def _add_time_series_figure(self) -> None:
        """Create and add time series figure to PDF.

        This method uses the pure plotting function and layout configuration
        to create a properly sized figure for the PDF.
        """
        # Calculate optimal figure dimensions
        page_width_mm = self.pdf.w
        figure_width_mm = self.layout.calculate_figure_width(page_width_mm)
        figure_x, _ = self.layout.get_figure_position(page_width_mm)

        # Calculate figure size in inches for matplotlib
        figure_width_inches, figure_height_inches = (
            self.figure_config.calculate_size_for_width(figure_width_mm)
        )

        # Create the figure using pure plotting function
        figure = make_time_series_figure(
            data=self.time_series,
            temperature_c=self.temperature,
            size_inches=(figure_width_inches, figure_height_inches),
            dpi=self.figure_config.dpi,
        )

        # Save to temporary file
        temp_path = save_figure_to_temp_file(figure, str(self.output_dir))

        try:
            # Calculate figure height in mm for PDF
            figure_height_mm = figure_width_mm * (
                figure_height_inches / figure_width_inches
            )

            # Add to PDF
            self.pdf.image(
                temp_path,
                x=figure_x,
                y=self.time_series_y,
                w=figure_width_mm,
                h=figure_height_mm,
            )

        finally:
            # Clean up temporary file
            try:
                Path(temp_path).unlink()
            except OSError:
                pass


if __name__ == "__main__":
    """Run this file directly to generate a report with sample date."""
    # Example Usage
    # Create Dummy metadata
    sample_metadata = {
        "tester_name": "First Last",
        "test_date": datetime.date(2025, 10, 23),
        "ds50_serial": "#9999",
        "location": "Toronto Lab - Sunnybrook",
    }

    # Dummy time series data
    example_time_series = {
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
        11: 1.00,
    }

    # Dummy test table data matching the expected format
    example_test_data = [
        {"description": "Vacuum Pressure:", "pass_fail": "Pass", "measured": -24.5},
        {"description": "Flow Rate:", "pass_fail": "Pass", "measured": 485.0},
        {
            "description": "Dissolved Oxygen Level Test:",
            "pass_fail": "Pass",
            "measured": 2.15,
        },
        {
            "description": "Dissolved Oxygen Re-circulation Test (1000 mL):",
            "pass_fail": "",
            "measured": None,
        },
        {
            "description": "   Starting DO Level:",
            "pass_fail": "Pass",
            "measured": 8.65,
        },
        {
            "description": "   Time to Reach 4 mg/L (min):",
            "pass_fail": "Pass",
            "measured": 4.0,
        },
        {
            "description": "   Time to Reach 2 mg/L (min):",
            "pass_fail": "Pass",
            "measured": 8.0,
        },
    ]

    metadata = sample_metadata
    time_series = example_time_series
    test_data = example_test_data
    temp = 25.0

    # Create default output directory
    output_dir = DEFAULT_EXPORT_DIR
    # Generate the report
    report = GenerateReport(
        metadata=metadata,
        test_data=example_test_data,
        time_series=time_series,
        temperature=temp,
        output_dir=output_dir,
    )
    report.generate_report()
