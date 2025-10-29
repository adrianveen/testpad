#!/usr/bin/env python
import datetime
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fpdf import FPDF, Align, FontFace

from testpad.config.defaults import DEFAULT_EXPORT_DIR, DEFAULT_FUS_LOGO_PATH
from testpad.core.burnin.burnin_stats import BurninStats
from testpad.core.burnin.burnin_graph import BurninGraph
from testpad.ui.tabs.burnin_tab.report_layout import (
    DEFAULT_FIGURE_CONFIG,
    DEFAULT_LAYOUT,
    DEFAULT_STYLE_CONFIG,
)


class GenerateReport:
    """Generates a PDF report for the Burnin Tab."""

    def __init__(
        self,
        meta_data: Dict[str, Any],
        burnin_stats: BurninStats,
        output_dir: Path = DEFAULT_EXPORT_DIR,
        logo_path: Path = DEFAULT_FUS_LOGO_PATH,
    ) -> None:
        """Initializes the GenerateReport class.

        Args:
            burnin_stats (BurninStats): The BurninStats object to generate the report for.
            output_path (Path): The path to the output PDF file.
            layout (Optional[Dict[str, Any]], optional): The layout configuration for the report. Defaults to DEFAULT_LAYOUT.
            style_config (Optional[Dict[str, Any]], optional): The style configuration for the report. Defaults to DEFAULT_STYLE_CONFIG.
            figure_config (Optional[Dict[str, Any]], optional): The figure configuration for the report. Defaults to DEFAULT_FIGURE_CONFIG.
        """
        self.meta_data = meta_data
        self.burnin_stats = burnin_stats
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
        # self._build_stats_table(burnin_stats=self.burnin_stats)
        # self._build_graphs()

        # Create and add figures to report
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.pdf.output(filename)

    def _build_report_base(self, margins: float = 0) -> None:
        """Initializes the report and draws the report skeleton such as margins.

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

    def _build_title_block(self, meta_data: Dict[str, Any]) -> None:
        """Draws the title block for the report.

        This includes metadata such as the test name, serial number, date,
        as well as tested by, and the report title.

        Args:
            meta_data(dict): Metadata dictionary containing test name,
            location, date, and RK-300 serial number.

        """
        # Convert keys to more user-friendly names
        meta_data = {
            "Tested By": meta_data.get("tested_by", ""),
            "Test Name": meta_data.get("test_name", ""),
            "Date": meta_data.get("test_date", ""),
            "RK-300 Serial Number": meta_data.get("RK-300_serial_number", ""),
        }

        self.pdf.set_font(
            style=self.styling_config.title_text_style,
            size=self.styling_config.title_text_size,
        )
        # Draw the report title
        self.pdf.ln(self.layout.title_spacing_mm)  # Add spacing after Header
        self.pdf.cell(
            text=f"Burnin Report for {self.meta_data['test_name']}",
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
        with self.pdf.table(col_widths=(90), align="L", markdown=True) as table:
            for pair in rows:
                row = table.row()
                for label, value in pair:
                    if label == "Date":
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

    def _build_stats_table(self) -> None:
        pass

    def _build_graphs(self) -> None:
        pass


def main():
    """Allow standalone execution of the GenerateReport class."""
    sample_meta_data = {
        "tested_by": "Tester McTestface",
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
    sample_burnin_stats_neg = {
        "mean": -58,
        "median": -55,
        "min": 11,
        "max": 85,
        "std": 9.99,
        "variance": 99.83,
        "25th_percentile": -50,
        "75th_percentile": -70,
        "skewness": -0.56,
        "kurtosis": -1.19,
        "prcnt_above_thresh": 99.99,
        "prcnt_below_thresh": 0.01,
        "num_peaks_above_thresh": 0,
        "num_peaks_below_thresh": 5801,
    }
    report = GenerateReport(
        meta_data=sample_meta_data, burnin_stats=sample_burnin_stats_pos
    )
    report.generate_report()


if __name__ == "__main__":
    main()
