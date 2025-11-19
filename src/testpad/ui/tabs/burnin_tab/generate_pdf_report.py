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
        burnin_stats: list["BurninStats"],
        list_of_temp_pngs: list,
        output_dir: Path = DEFAULT_EXPORT_DIR,
        logo_path: Path = DEFAULT_FUS_LOGO_PATH,
    ) -> None:
        """Initialize the GenerateReport class.

        Args:
            meta_data (dict[str, Any]): Metadata dictionary containing test name,
                location, date, and RK-300 serial number.
            burnin_stats (BurninStats): BurninStats object to generate the report
            list_of_temp_pngs (list): List of matplotlib figures to include in
                the report.
            output_dir (Path): The path to the output PDF file.
            logo_path (Path): The path to the logo image file.

        """
        self.meta_data = meta_data
        self.burnin_stats = burnin_stats
        self.axis_names = []
        self.pos_stats = []
        self.neg_stats = []
        self.pos_neg_stats: list[tuple] = []

        for stats in self.burnin_stats:
            axis_name = stats.axis_name
            positive_stats = stats.positive_stats
            negative_stats = stats.negative_stats
            self.axis_names.append(axis_name)
            self.pos_stats.append(positive_stats)
            self.neg_stats.append(negative_stats)
            self.pos_neg_stats.append((positive_stats, negative_stats))

        # self.pos_neg_stats = (
        #     self.pos_stats,
        #     self.neg_stats,
        # )

        self.figures = list_of_temp_pngs
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
        for i, stats in enumerate(self.pos_neg_stats):
            self._build_stats_table(stats, self.axis_names[i])
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
            text=f"Burnin Report for {self.meta_data['RK300 Serial #']}",
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
                if label == "Test Date":
                    # Value is a Python date object (converted by presenter)
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
                    if label == "Test Date":
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

    def _build_stats_table(self, stats: tuple[tuple, tuple], axis_name: str) -> None:
        """Build a table for the positive and negative error values.

        Args:
            stats (tuple[tuple, tuple]): A tuple containing the positive
                and negative error values.
            axis_name (str): Name of the axis.

        """
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
            "Std. Dev.",
            # "Variance",
            # "25th Percentile",
            # "75th Percentile",
            # "Skewness",
            # "Kurtosis",
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

        self.pdf.cell(
            text=f"Axis {axis_name} Error Statistics",
            align=Align.C,
            center=True,
            border=0,
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.pdf.ln(self.layout.section_spacing_mm)
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

        for j in range(len(temp_pngs)):
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
    """Allow standalone execution of the GenerateReport class for manual testing."""

    class _MockBurninStats:
        def __init__(
            self,
            axis_name: str,
            positive_stats: tuple[float, ...],
            negative_stats: tuple[float, ...],
        ) -> None:
            self.axis_name = axis_name
            self.positive_stats = positive_stats
            self.negative_stats = negative_stats

    sample_meta_data: dict[str, Any] = {
        "Test Name": "RK-300 Burnin Test",
        "Test Date": datetime.date(2025, 1, 15),
        "Location": "Lab A",
        "RK300 Serial #": "SN-123456",
    }

    stats_x = _MockBurninStats(
        "X",
        (56.2, 58.1, 37.5, 70.3, 4.54, 99.42, 0.58, 3290, 0),
        (-54.8, -57.2, -68.9, -35.1, 4.32, 98.76, 1.24, 3145, 2),
    )
    stats_y = _MockBurninStats(
        "Y",
        (52.1, 53.4, 34.2, 68.7, 5.12, 98.52, 1.48, 3201, 1),
        (-53.6, -54.9, -69.3, -33.8, 4.98, 97.89, 2.11, 3087, 3),
    )

    report = GenerateReport(
        meta_data=sample_meta_data,
        burnin_stats=[stats_x, stats_y],  # type: ignore[arg-type]
        list_of_temp_pngs=[],
    )
    report.generate_report()
    print(f"Test report generated in: {DEFAULT_EXPORT_DIR}")


if __name__ == "__main__":
    main()
