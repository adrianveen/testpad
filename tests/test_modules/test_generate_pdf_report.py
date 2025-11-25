"""Tests for Degasser PDF Report Generation."""

from datetime import date
from pathlib import Path

import pytest

from testpad.ui.tabs.degasser_tab.config import NO_LIMIT_SYMBOL
from testpad.ui.tabs.degasser_tab.generate_pdf_report import GenerateReport


class TestReportFormatting:
    """Tests for value formatting helpers."""

    @pytest.fixture
    def report_generator(self, tmp_path: Path) -> GenerateReport:
        """Create a dummy report generator instance."""
        return GenerateReport(
            metadata={},
            test_data=[],
            time_series={},
            temperature=None,
            output_dir=tmp_path,
        )

    def test_format_spec_value(self, report_generator: GenerateReport) -> None:
        """Test specification value formatting."""
        # Float with unit
        assert report_generator.format_spec_value(5.0, "mg/L") == "5.00 mg/L"

        # Int with unit
        assert report_generator.format_spec_value(10, "min") == "10 min"

        # None (no limit)
        assert report_generator.format_spec_value(None, "any") == NO_LIMIT_SYMBOL

        # Value without unit
        assert report_generator.format_spec_value(100, "") == "100"

    def test_format_measured_value(self, report_generator: GenerateReport) -> None:
        """Test measured value formatting."""
        # Float with unit
        assert report_generator.format_measured_value(5.123, "mg/L") == "5.12 mg/L"

        # Int with unit
        assert report_generator.format_measured_value(10, "min") == "10 min"

        # String value
        assert report_generator.format_measured_value("Pass", "") == "Pass"

        # None
        assert report_generator.format_measured_value(None, "") == NO_LIMIT_SYMBOL


class TestReportGeneration:
    """Integration tests for report generation."""

    def test_generate_report_creates_file(self, tmp_path: Path) -> None:
        """Test that generate_report creates a PDF file."""
        metadata = {
            "tester_name": "Test User",
            "test_date": date(2025, 1, 1),
            "ds50_serial": "#TEST1234",
            "location": "Lab A",
        }

        # Minimal valid test data structure
        test_data = [
            {"description": "Test 1", "pass_fail": "Pass", "measured": 1.0},
            {"description": "Test 2", "pass_fail": "Pass", "measured": 2.0},
            # Add enough rows to match config if strictly required,
            # but GenerateReport loops over input list, so small list should work
            # unless index access is hardcoded against config mapping.
            # View logic uses enumerate, but ROW_SPEC_MAPPING relies on index.
            # Let's provide 7 dummy rows to be safe and match NUM_TEST_ROWS.
        ] + [
            {"description": f"Test {i}", "pass_fail": "", "measured": None}
            for i in range(3, 8)
        ]

        time_series: dict[int, float] = dict.fromkeys(range(21), 5.0)

        report = GenerateReport(
            metadata=metadata,
            test_data=test_data,
            time_series=time_series,
            temperature=25.0,
            output_dir=tmp_path,
        )

        output_file = report.generate_report(filename="test_report.pdf", overwrite=True)

        assert output_file.exists()
        assert output_file.name == "test_report.pdf"
        assert output_file.stat().st_size > 0
