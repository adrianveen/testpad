"""Report generation for the Degasser Tab."""

import contextlib
import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF, Align, FontFace
from fpdf.table import Table

from testpad.config.defaults import DEFAULT_EXPORT_DIR, DEFAULT_FUS_LOGO_PATH
from testpad.ui.tabs.degasser_tab.config import (
    DEFAULT_TEST_DESCRIPTIONS,
    DISSOLVED_OXYGEN_STRING,
    DISTILLED_WATER_STRING,
    DS50_SPEC_RANGES,
    DS50_SPEC_UNITS,
    HEADER_ROW_INDEX,
    NO_LIMIT_SYMBOL,
    PDF_REPORT_NAME_PREFIX,
    RE_CIRCULATION_STRING,
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

    def generate_report(
        self,
        filename: str | Path | None = None,
        overwrite: bool = False,
        auto_increment: bool = False,
    ) -> Path:
        """Call the draw functions and exports the report.

        Args:
            filename: The filename to save the report to. If None, a filename
            overwrite: Overwrite the existing file if it exists
            auto_increment: Increment the filename if it already exists

        """
        serial_num = self.metadata.get("ds50_serial", "").replace("#", "")
        if filename is None:
            filename = (
                Path(self.output_dir) / f"{PDF_REPORT_NAME_PREFIX}{serial_num}.pdf"
            )
        else:
            filename = Path(filename)

        # Check if file exists before building pdf
        if filename.exists() and not overwrite:
            if auto_increment:
                filename = self._get_next_available_filename(filename)
            else:
                msg = (
                    f"Report already exists: {filename}\n"
                    f"Use overwrite=True or auto_increment=True to handle this."
                )
                raise FileExistsError(msg)

        # Make the directory if it doesn't exist
        output_path = Path(self.output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            msg = f"Failed to create output directory '{output_path}': {e}"
            raise OSError(msg) from e

        # Verify directory was actually created
        if not output_path.exists() or not output_path.is_dir():
            msg = (
                f"Output directory does not exist or is not a directory: "
                f"'{output_path}'"
            )
            raise OSError(msg)

        # Call remaining draw methods
        self._build_report_base(self.layout.left_margin_mm)
        self._build_header(logo_path=self.logo_path)
        self._build_title_block(self.metadata)
        self._build_test_table(self.test_data)
        self._build_time_series_table(self.time_series)

        # Create and add figure
        self._add_time_series_figure()

        # Save PDF to the output path
        self.pdf.output(str(filename))

        return filename

    def _get_next_available_filename(
        self, base_filename: Path, max_attempts: int = 100
    ) -> Path:
        """Find next available filename with increment suffix.

        Args:
          base_filename: Original filename (e.g., "DS50_Test_Report_#9999.pdf")
          max_attempts: Maximum number of suffixes to try

        Returns:
          Next available path (e.g., "DS50_Test_Report_#9999_1.pdf")

        Raises:
          OSError: If max_attempts reached without finding available filename

        """
        if not base_filename.exists():
            return base_filename

        # Extract stem and suffix
        # "DS50_Test_Report_#9999.pdf" -> stem="DS50_Test_Report_#9999", suffix=".pdf"
        stem = base_filename.stem
        suffix = base_filename.suffix
        parent = base_filename.parent

        for i in range(1, max_attempts + 1):
            new_filename = parent / f"{stem}_{i}{suffix}"
            if not new_filename.exists():
                return new_filename

        msg = f"Could not find available filename after {max_attempts} attempts"
        raise OSError(msg)

    def _build_report_base(self, margins: float) -> None:
        """Initialize the report object and draws the report skeleton such as margins.

        Args:
            margins(float): Margin values specified by the config.

        """
        self.pdf = FPDF(orientation="P", unit="mm", format="letter")
        self.pdf.add_page()
        self.pdf.set_margins(left=margins, top=margins * 0.75, right=margins)
        self.pdf.set_auto_page_break(auto=True, margin=self.layout.bottom_margin_mm)
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

        # TODO: Nearly identical code to burnin report - refactor to common method
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
                    text=f"{label}: --{value if value else '      '}--",
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
                        text=f"{label}: --{value if value else '      '}--",
                        border=False,
                        align=Align.C,
                        style=value_font_style,
                    )
                else:
                    # Odd number of fields, pad the last row
                    row.cell("", border=False)

    @staticmethod
    def format_spec_value(value: float | None, unit: str) -> str:
        """Format a specification value with its unit.

        Args:
            value: The specification value (float, int, or None).
            unit: The unit string to append.

        Returns:
            Formatted string (e.g., "5.00 mg/L", "--").

        """
        if value is None:
            return NO_LIMIT_SYMBOL
        if isinstance(value, float):
            return f"{value:.2f} {unit}"
        return f"{value} {unit}" if unit else str(value)

    @staticmethod
    def format_measured_value(value: float | str | None, unit: str) -> str:
        """Format a measured value with its unit.

        Args:
            value: The measured value.
            unit: The unit string to append (only used if value is float).

        Returns:
            Formatted string.

        """
        if value is None:
            return NO_LIMIT_SYMBOL
        if isinstance(value, float):
            return f"{value:.2f} {unit}"
        if isinstance(value, int):
            return f"{value} {unit}" if unit else str(value)
        return f"{value}"

    def _add_test_row(
        self,
        table: Table,
        idx: int,
        row_data: dict[str, Any],
        styles: dict[str, FontFace],
    ) -> None:
        """Add a single row to the test table.

        Args:
            table: The fpdf table object.
            idx: The row index.
            row_data: The dictionary containing row data.
            styles: Dictionary of FontFace styles.

        """
        row = table.row()

        # Handle Header Row (Merged Cell)
        if idx == HEADER_ROW_INDEX:
            row.cell(
                text=f"\n{row_data['description']}",  # newline to space out table
                align=Align.C,
                style=styles["header"],
                colspan=5,
                border=0,
            )
            return

        # Normal Data Row
        # Column 1: Description
        row.cell(row_data["description"], align="L", style=styles["description"])

        # Column 2: Pass/Fail
        pass_fail_text = row_data.get("pass_fail", "") or ""
        row.cell(pass_fail_text, align="C", style=styles["data"])

        # Get specs and units
        spec_key = ROW_SPEC_MAPPING[idx]
        spec: tuple[float | int | None, float | int | None]
        spec = (
            DS50_SPEC_RANGES.get(spec_key, (None, None)) if spec_key else (None, None)
        )
        unit = DS50_SPEC_UNITS.get(spec_key, "") if spec_key else ""

        # Column 3: Spec Min
        spec_min_text = self.format_spec_value(spec[0], unit)
        row.cell(spec_min_text, align="C", style=styles["spec"])

        # Column 4: Spec Max
        spec_max_text = self.format_spec_value(spec[1], unit)
        row.cell(spec_max_text, align="C", style=styles["spec"])

        # Column 5: Data Measured
        data_measured: float | int | str | None = row_data.get("measured")
        data_measured_text = self.format_measured_value(data_measured, unit)
        row.cell(data_measured_text, align="C", style=styles["data"])

    def _build_test_table(self, test_data: list[dict[str, Any]]) -> None:
        """Draws the 8 row x 5 col table for the test results and default values.

        Args:
            test_data: List of dictionaries containing measured data and
                pass/fail inputs

        """
        headers = TEST_TABLE_HEADERS

        # Define styles
        styles = {
            "header": FontFace(
                emphasis=self.styling_config.header_text_style,
                size_pt=self.styling_config.header_text_size,
                color=self.styling_config.header_text_color,
            ),
            "description": FontFace(
                emphasis=self.styling_config.header_text_style,
                size_pt=self.styling_config.description_text_size,
                color=self.styling_config.header_text_color,
            ),
            "spec": FontFace(
                emphasis=self.styling_config.values_text_style,
                size_pt=self.styling_config.spec_text_size,
                color=self.styling_config.spec_text_color,
            ),
            "data": FontFace(
                emphasis=self.styling_config.values_text_style,
                size_pt=self.styling_config.data_text_size,
                color=self.styling_config.data_text_color,
            ),
        }

        self.pdf.ln(
            self.layout.section_spacing_mm,
        )  # Add a spacer before the data table

        with self.pdf.table(col_widths=(40, 25, 25, 25, 25)) as table:
            # Create Header Row
            header_row = table.row()
            for header in headers:
                header_row.cell(header, Align.C, style=styles["header"])

            # Create Data Rows
            for idx, test_row_dict in enumerate(test_data):
                self._add_test_row(table, idx, test_row_dict, styles)

    def _build_time_series_table(self, data: dict[int, float]) -> None:
        """Draws a two-row horizontal table for time series data.

        The first row contains time points (minutes) and the second row contains
        the corresponding dissolved oxygen values (mg/L).

        Args:
            data (dict[int, float]): Dictionary where keys are time points (int)
                and values are dissolved oxygen levels (float).

        """
        # Add spacer
        self.pdf.ln(self.layout.section_spacing_mm)

        # Subtitle - non-bold
        self.pdf.set_font(
            style=self.styling_config.values_text_style,
            size=self.styling_config.header_text_size,
        )
        self.pdf.cell(
            text=f"{DISSOLVED_OXYGEN_STRING} Measurements",
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT",
        )

        # Add spacer and get current y position of table
        self.pdf.ln(self.layout.small_section_spacing_mm)

        # Define styles for table cells (FontFace only works in table context)
        header_style = FontFace(
            emphasis=self.styling_config.header_text_style,
            size_pt=self.styling_config.time_header_text_size,
        )
        data_style = FontFace(
            emphasis=self.styling_config.values_text_style,
            size_pt=self.styling_config.time_data_text_size,
            color=self.styling_config.data_text_color,
        )

        # Table with header row - bold, font 10
        row_names = TIME_SERIES_HEADERS
        times = sorted(data.keys())
        with self.pdf.table(
            col_widths=(22, *([7] * len(times))),
            align=Align.C,
            line_height=5,
        ) as table:
            row_keys = table.row()
            row_keys.cell(text=row_names[0], align=Align.L, style=header_style)
            for time in times:
                row_keys.cell(str(time), align=Align.C, style=data_style)
            row_values = table.row()
            row_values.cell(text=row_names[1], align=Align.L, style=header_style)
            for time in times:
                do_value = data[time]
                row_values.cell(f"{do_value:.2f}", align=Align.C, style=data_style)

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
        # Width: Full page width minus margins
        figure_width_mm = (
            self.pdf.w - self.layout.left_margin_mm - self.layout.right_margin_mm
        )

        # Height: Remaining vertical space minus bottom margin
        # Available height = Page Height - Current Y - Bottom Margin
        bottom_margin_mm = self.layout.bottom_margin_mm
        figure_height_mm = self.pdf.h - self.pdf.get_y() - bottom_margin_mm

        # Safety check to prevent negative or tiny height
        if figure_height_mm < self.layout.figure_min_height_mm:
            figure_height_mm = 50  # Fallback height

        # Calculate figure size in inches for matplotlib
        # We use the exact dimensions calculated above
        figure_width_inches = figure_width_mm / 25.4
        figure_height_inches = figure_height_mm / 25.4

        # Create the figure using pure plotting function
        figure = make_time_series_figure(
            data=self.time_series,
            temperature_c=self.temperature,
            size_inches=(figure_width_inches, figure_height_inches),
            dpi=self.figure_config.dpi,
        )

        # Save to temporary file
        # bbox_inches=None ensures the saved image matches size_inches exactly
        temp_path = save_figure_to_temp_file(figure, str(Path.cwd()))

        try:
            # Add to PDF
            self.pdf.image(
                temp_path,
                x=self.layout.left_margin_mm,
                w=figure_width_mm,
                h=figure_height_mm,
            )

        finally:
            # Clean up temporary file
            with contextlib.suppress(OSError):
                Path(temp_path).unlink()


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
        0: 9.85,
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
        11: 1.99,
        12: 1.98,
        13: 1.97,
        14: 1.96,
        15: 1.95,
        16: 1.94,
        17: 1.93,
        18: 1.92,
        19: 1.91,
        20: 1.90,
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
            "description": (
                f"{DISSOLVED_OXYGEN_STRING} {RE_CIRCULATION_STRING} - "
                f"{DISTILLED_WATER_STRING}"
            ),
            "pass_fail": "",
            "measured": None,
        },
        {
            "description": f"{DEFAULT_TEST_DESCRIPTIONS[4]}",
            "pass_fail": "Pass",
            "measured": 8.65,
        },
        {
            "description": f"{DEFAULT_TEST_DESCRIPTIONS[5]}",
            "pass_fail": "Pass",
            "measured": 4.0,
        },
        {
            "description": f"{DEFAULT_TEST_DESCRIPTIONS[6]}",
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
    report.generate_report(auto_increment=True)
    print(f"Test report generated in: {output_dir}")
