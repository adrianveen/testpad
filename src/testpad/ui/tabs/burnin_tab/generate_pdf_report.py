#!/usr/bin/env python
import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fpdf import FPDF, Align, FontFace

from testpad.config.defaults import DEFAULT_EXPORT_DIR, DEFAULT_FUS_LOGO_PATH
from testpad.ui.tabs.burnin_tab.report_layout import (
    DEFAULT_FIGURE_CONFIG,
    DEFAULT_LAYOUT,
    DEFAULT_STYLE_CONFIG,
)

if TYPE_CHECKING:
    from testpad.core.burnin.burnin_stats import BurninStats


class GenerateReport:
    """Generates a PDF report for the Burnin Tab."""

    def __init__(
        self,
        meta_data: dict[str, Any],
        burnin_stats: "BurninStats",
        figures: list,
        output_dir: Path = DEFAULT_EXPORT_DIR,
        logo_path: Path = DEFAULT_FUS_LOGO_PATH,
    ) -> None:
        """Initialize the GenerateReport class.

        Args:
            meta_data (dict[str, Any]): Metadata dictionary containing test name,
                location, date, and RK-300 serial number.
            burnin_stats (BurninStats): BurninStats object to generate the report
            figures (list): List of matplotlib figures to include in the report.
            output_dir (Path): The path to the output PDF file.
            logo_path (Path): The path to the logo image file.

        """
        self.meta_data = meta_data
        self.burnin_stats = burnin_stats

        self.positive_stats = self.burnin_stats.positive_stats
        self.negative_stats = self.burnin_stats.negative_stats
        self.pos_neg_stats = (
            self.burnin_stats.positive_stats,
            self.burnin_stats.negative_stats,
        )

        self.figures = figures
        self.output_dir = output_dir
        self.logo_path = logo_path

        # Layout configuration
        self.layout = DEFAULT_LAYOUT
        self.figure_config = DEFAULT_FIGURE_CONFIG
        self.styling_config = DEFAULT_STYLE_CONFIG

    def generate_report(self) -> None:
        """Generate and export the PDF report for the Burnin Tab."""
        filename = (
            Path(self.output_dir)
            / f"RK-300 Burnin Report {datetime.datetime.now().strftime('%Y-%m-%d')}.pdf"
        )
        filename = str(filename)

        # Call drawing methods for report
        self._build_report_base(self.layout.left_margin_mm)
        self._build_header(logo_path=self.logo_path)
        self._build_title_block(meta_data=self.meta_data)
        self._build_stats_table(self.pos_neg_stats)
        self._build_graphs(self.figures)

        # Create and add figures to report
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.pdf.output(filename)

    def _build_report_base(self, margins: float = 0) -> None:
        """Initialize the report and draws the report skeleton such as margins.

        Args:
            margins(float): Margin values specified by the config.

        """
        self.pdf = FPDF(orientation="P", unit="mm", format="A4")
        self.pdf.add_page()
        self.pdf.set_margins(left=margins, top=margins, right=margins)
        self.pdf.set_font("helvetica", size=self.styling_config.header_text_size)

    def _build_header(self, logo_path: Path) -> None:
        """Draws the header for the report which includes company logo.

        Args:
            logo_path: Full path to the logo image file.

        """
        # Add fus logo
        self.pdf.image(
            str(logo_path),
            w=self.styling_config.logo_width_mm,
            keep_aspect_ratio=self.styling_config.logo_keep_aspect_ratio,
        )

    def _build_title_block(self, meta_data: dict) -> None:
        """Draws the title block for the report.

        This includes metadata such as the test name, serial number, date,
        as well as tested by, and the report title.

        Args:
            meta_data(dict): Metadata dictionary containing test name,
            location, date, and RK-300 serial number.

        """
        self.pdf.set_font(
            style=self.styling_config.title_text_style,
            size=self.styling_config.title_text_size,
        )
        # Draw the report title
        self.pdf.ln(self.layout.title_spacing_mm)  # Add spacing after Header
        self.pdf.cell(
            text=f"Burnin Report for {self.meta_data['Test Name']}",
            align=Align.C,
            center=True,
            new_x="RIGHT",
            new_y="NEXT",
        )
        # Add spacing in mm
        self.pdf.ln(self.layout.title_spacing_mm)

        # Pass the metadata values to a list
        values = list(meta_data.items())
        rows = [values[i : i + 2] for i in range(0, len(values), 2)]

        # Set the font style for the values
        value_font_style = FontFace(
            emphasis=self.styling_config.metadata_text_style,
            size_pt=self.styling_config.metadata_text_size,
        )

        # Set the title font style
        self.pdf.set_font(
            style=self.styling_config.subtitle_text_style,
            size=self.styling_config.metadata_text_size,
        )

        # Create a table for the title block
        with self.pdf.table(col_widths=(60), align="C", markdown=True) as table:
            for pair in rows:
                row = table.row()
                for label, value in pair:
                    if label == "Test Date":
                        # Value is already a Python date object (converted by model)
                        value = value.strftime("%Y-%m-%d")
                    row.cell(
                        text=f"{label}: --{value}--",
                        border=False,
                        align=Align.L,
                        style=value_font_style,
                    )
                # If odd number of fields, pad the last line,
                if len(pair) < 2:
                    row.cell("")

    def _build_stats_table(self, stats: tuple[tuple, tuple]) -> None:
        pos_stats = stats[0]
        neg_stats = stats[1]

        # Build table with following value names
        self.pdf.ln(self.layout.section_spacing_mm)
        # TODO: Replace with config
        stats_labels = [
            "Mean",
            "Median",
            "Min",
            "Max",
            "Std",
            "Variance",
            "25th Percentile",
            "75th Percentile",
            "Skewness",
            "Kurtosis",
            "Above Threshold",
            "Below Threshold",
            "Peaks Above Threshold",
            "Peaks Below Threshold",
        ]
        headers = [
            "Values",
            "Positive Error Values",
            "Negative Error Values",
        ]

        header_font_style = FontFace(
            emphasis=self.styling_config.header_text_style,
            size_pt=self.styling_config.header_text_size,
            color=self.styling_config.header_text_color,
        )

        data_style = FontFace(
            emphasis=self.styling_config.values_text_style,
            size_pt=self.styling_config.data_text_size,
            color=self.styling_config.data_text_color,
        )

        with self.pdf.table(col_widths=(50), align="C", markdown=True) as table:
            header_row = table.row()
            for header in headers:
                header_row.cell(header, Align.C, style=header_font_style)
            for i in range(len(stats_labels)):
                row = table.row()
                label = stats_labels[i]
                row.cell(label, Align.C)
                # TODO @adrianveen: Replace strings with iterable from config
                if label in {"Above Threshold", "Below Threshold"}:
                    pos_value = str(pos_stats[i]) + "%"
                    neg_value = str(neg_stats[i]) + "%"
                else:
                    pos_value = str(pos_stats[i])
                    neg_value = str(neg_stats[i])
                row.cell(pos_value, Align.C, style=data_style)
                row.cell(neg_value, Align.C, style=data_style)

    def _build_graphs(self, temp_pngs: list) -> None:
        """Take a list of temporary PNGs paths to add to the PDF report.

        Args:
            temp_pngs(list): List of temporary PNG paths

        """
        self.pdf.ln(self.layout.title_spacing_mm)
        # Calculate optimal figure dimensions
        page_width_mm = self.pdf.w
        figure_width_mm = page_width_mm - (2 * self.layout.left_margin_mm)

        # Add to PDF one at a time
        # Calculate figure height in mm for PDF
        figure_height_mm = self.pdf.h / 2 - (2 * self.layout.top_margin_mm)

        for j in range(4):
            try:
                # Add to PDF
                self.pdf.image(
                    temp_pngs[j],
                    w=figure_width_mm,
                    h=figure_height_mm,
                    keep_aspect_ratio=True,
                )
            finally:
                # Clean up temporary file
                try:
                    Path(temp_pngs[j]).unlink(missing_ok=True)
                except OSError as e:
                    msg = f"[WARNING] Failed to delete: {temp_pngs[j]}: {e}"
                    print(msg)


def main() -> None:
    """Allow standalone execution of the GenerateReport class."""
    sample_meta_data = {
        "tested_by": "Tester Lastname",
        "test_date": datetime.datetime.now(),
        "test_name": "RK-300",
        "RK-300_serial_number": "1234567890",
    }
    sample_burnin_stats_pos = {
        "mean": 56,
        "median": 58,
        "min": 37,
        "max": 70,
        "std": 4.54,
        "variance": 20.73,
        "25th_percentile": -57,
        "75th_percentile": -58,
        "skewness": -2.16,
        "kurtosis": 1.64,
        "prcnt_above_thresh": 99.42,
        "prcnt_below_thresh": 0.58,
        "num_peaks_above_thresh": 3290,
        "num_peaks_below_thresh": 0,
    }
    report = GenerateReport(
        meta_data=sample_meta_data,
        burnin_stats=sample_burnin_stats_pos,
        figures=[],
    )
    report.generate_report()


if __name__ == "__main__":
    main()
