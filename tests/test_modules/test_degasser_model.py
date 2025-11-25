# ruff: noqa: PLR2004,S105,S106
"""Tests for degasser_tab model.

This test module covers:
- Validation logic for minutes, oxygen readings, and temperature
- Data manipulation (set/clear measurements)
- CSV import/export functionality
- Edge cases and error handling
"""

from __future__ import annotations

import csv
from datetime import date
from typing import TYPE_CHECKING

import pytest

from testpad.ui.tabs.degasser_tab.config import (
    DS50_SPEC_RANGES,
    MINIMUM_END_MINUTE,
    NUM_TEST_ROWS,
    NUM_TIME_SERIES_COLS,
    START_MINUTE,
)
from testpad.ui.tabs.degasser_tab.model import DegasserModel

if TYPE_CHECKING:
    from pathlib import Path


# ====================================================================================
# VALIDASTION TESTS - Testing the "rules" of the data
# ====================================================================================
class TestMinuteValidation:
    """Test the validation rules for minutes."""

    def test_valid_minutes(self) -> None:
        """Valid minutes (0-20) should be accepted without error."""
        model = DegasserModel()
        for minute in range(NUM_TIME_SERIES_COLS):  # 0, 1 , 2, ..., 20
            model.set_measurement(minute, 5.0)  # Should not raise an error

    def test_negative_minutes_rejected(self) -> None:
        """Negative minutes should raise an error."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="must be in range"):
            model.set_measurement(-1, 5.0)

    def test_minute_too_large_rejected(self) -> None:
        """Minutes greater than 20 should raise an error."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="must be in range"):
            model.set_measurement(NUM_TIME_SERIES_COLS, 5.0)

    def test_set_measurement_stores_data(self) -> None:
        """Setting a measurement should store the data in the model."""
        model = DegasserModel()
        state = model.set_measurement(5, 7.5)

        # Check the state returned
        assert state.loaded is True
        assert state.points_filled == 1
        assert 5 in state.minutes_with_data

        # Check we can retrieve the data
        measurements = model.list_measurements()
        assert measurements == [(5, 7.5)]

    def test_overwrite_measurement(self) -> None:
        """Setting a measurement should overwrite the existing data."""
        model = DegasserModel()
        model.set_measurement(3, 5.0)
        model.set_measurement(3, 7.5)  # Overwrite

        measurements = model.list_measurements()
        assert measurements == [(3, 7.5)]  # Only latest value stored


class TestOxygenValidation:
    """Test the validation rules for oxygen readings."""

    def test_positive_oxygen_accepted(self) -> None:
        """Positive oxygen readings should be accepted without error."""
        model = DegasserModel()
        model.set_measurement(0, 0.1)  # small positive value
        model.set_measurement(1, 4.5)  # normal positive value
        model.set_measurement(2, 10000.0)  # large positive value

    def test_zero_oxygen_rejected(self) -> None:
        """Zero oxygen readings should raise ValueError (must be > 0)."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="must be > 0"):
            model.set_measurement(0, 0.0)

    def test_negative_oxygen_rejected(self) -> None:
        """Negative oxygen readings should raise ValueError (must be > 0)."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="must be > 0"):
            model.set_measurement(0, -0.1)

    def test_nonnumeric_oxygen_rejected(self) -> None:
        """Non-numeric oxygen readings should raise ValueError."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="not_a_number"):
            model.set_measurement(0, "not_a_number")  # type: ignore[arg-type]

    def test_non_integer_minute_rejected(self) -> None:
        """Non-integer minutes should raise ValueError."""
        model = DegasserModel()
        with pytest.raises(TypeError, match="must be an integer"):
            model.set_measurement(0.5, 5.0)  # type: ignore[arg-type]


class TestTemperatureValidation:
    """Test temperature handling (numeric values only)."""

    def test_numeric_temperature_accepted(self) -> None:
        """Numeric temperature values should be accepted."""
        model = DegasserModel()
        model.set_temperature(25.0)
        assert model.get_temperature_c() == 25.0

        model.set_temperature(-5.0)  # Negative temps are allowed
        assert model.get_temperature_c() == -5.0

    def test_string_numeric_temperature_coerced(self) -> None:
        """String numbers should be coerced to float."""
        model = DegasserModel()
        model.set_temperature("37.5")
        assert model.get_temperature_c() == 37.5

    def test_non_numeric_temperature_rejected(self) -> None:
        """Non-numeric temperature should raise ValueError."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="must be numeric"):
            model.set_temperature("not_a_number")  # type: ignore[arg-type]


# ====================================================================================
# DATA MANIPULATION TESTS - Testing the "actions" of the data
# ====================================================================================
class TestMeasurementOperations:
    """Test setting, clearing, and retrieving measurements."""

    def test_set_measurement_stores_data(self) -> None:
        """Setting a measurement should store the data in the model."""
        model = DegasserModel()
        state = model.set_measurement(5, 7.5)

        # Check the state returned
        assert state.loaded is True
        assert state.points_filled == 1
        assert 5 in state.minutes_with_data

        # Check we can retrieve the data
        measurements = model.list_measurements()
        assert measurements == [(5, 7.5)]

    def test_set_multiple_measurements(self) -> None:
        """Setting multiple measurements should store the data in the model."""
        model = DegasserModel()
        state = model.set_measurement(5, 7.5)
        state = model.set_measurement(6, 8.5)
        state = model.set_measurement(7, 9.5)

        # Check the state returned
        state = model.get_state()
        assert state.points_filled == 3
        assert state.minutes_with_data == [5, 6, 7]

    def test_overwrite_measurement(self) -> None:
        """Setting a measurement should overwrite the existing data."""
        model = DegasserModel()
        model.set_measurement(3, 5.0)
        model.set_measurement(3, 7.5)  # Overwrite

        measurements = model.list_measurements()
        assert measurements == [(3, 7.5)]  # Only latest value stored

    def test_clear_measurement(self) -> None:
        """Clearing a measurement should remove it from the model."""
        model = DegasserModel()
        model.set_measurement(3, 5.0)
        model.set_measurement(3, 7.5)  # Overwrite
        model.clear_measurement(3)

        measurements = model.list_measurements()
        assert measurements == []

    def test_clear_nonexistent_measurement_no_error(self) -> None:
        """Clearing a measurement that doesn't exist should not raise an error."""
        model = DegasserModel()
        model.clear_measurement(3)


class TestTimeSeriesRows:
    """Test the times series table generation (0-10 minutes)."""

    def test_empty_time_series_all_none(self) -> None:
        """With no data, all minutes should have None values."""
        model = DegasserModel()
        rows = model.build_time_series_rows()

        # Should have 21 rows (minutes 0-20 inclusive)
        assert len(rows) == NUM_TIME_SERIES_COLS
        assert rows[START_MINUTE] == (START_MINUTE, None)
        assert rows[10] == (10, None)
        assert rows[MINIMUM_END_MINUTE] == (MINIMUM_END_MINUTE, None)

    def test_partial_time_series(self) -> None:
        """Some minutes filled, others None."""
        model = DegasserModel()
        model.set_measurement(0, 8.5)
        model.set_measurement(10, 3.5)

        rows = model.build_time_series_rows()
        assert rows[0] == (0, 8.5)
        assert rows[5] == (5, None)  # not filled
        assert rows[10] == (10, 3.5)


class TestModelReset:
    """Test the reset() method."""

    def test_reset_clears_all_data(self) -> None:
        """Reset should clear measurements, temperature, and test rows."""
        model = DegasserModel()

        # Add some data
        model.set_measurement(5, 7.5)
        model.set_temperature(25.0)
        model.update_test_row(0, pass_fail="Pass", measured=5.0)

        # Reset
        state = model.reset()

        # Check everything is cleared
        assert state.loaded is False
        assert state.points_filled == 0
        assert model.get_temperature_c() is None

        # Test rows should be back to defaults
        rows = model.get_test_rows()
        assert all(r.pass_fail == "" for r in rows)
        assert all(r.measured is None for r in rows)


# ====================================================================================
# CSV IMPORT / EXPORT TESTS - Testing file operations
# ====================================================================================
class TestCSVImport:
    """Test CSV import."""

    def test_load_simple_csv(self, tmp_path: Path) -> None:
        """Load a basic CSV with time and oxygen columns."""
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text(
            "time,oxygen_mg_per_L\n"
            "0,5.0\n"
            "1,7.5\n"
            "2,10.0\n"
            "3,12.5\n"
            "4,15.0\n"
            "5,17.5\n"
            "6,20.0\n"
            "7,22.5\n"
            "8,25.0\n"
            "9,27.5\n"
            "10,30.0\n"
        )

        model = DegasserModel()
        state = model.load_from_csv(str(csv_file))  # type: ignore[arg-type]

        # Check the state
        assert state.loaded is True
        assert state.points_filled == 11
        measurements = model.list_measurements()
        assert len(measurements) == 11

    def test_load_csv_with_temperature(self, tmp_path: Path) -> None:
        """CSV with temperature column should load temperature."""
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text(
            "time,oxygen_mg_per_L,temperature_c\n"
            "0,5.0,25.5\n"
            "1,7.5,25.5\n"
            "2,10.0,25.5\n"
            "3,12.5,25.5\n"
            "4,15.0,25.5\n"
            "5,17.5,25.5\n"
            "6,20.0,25.5\n"
            "7,22.5,25.5\n"
            "8,25.0,25.5\n"
            "9,27.5,25.5\n"
            "10,30.0,25.5\n"
        )

        model = DegasserModel()
        model.load_from_csv(str(csv_file))

        assert model.get_temperature_c() == 25.5

    def test_load_csv_missing_required_columns(self, tmp_path: Path) -> None:
        """CSV with missing required columns should raise ValueError."""
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text(
            "time\n"  # Missing oxygen column!
            "0\n"
            "1\n"
            "2\n"
        )

        model = DegasserModel()
        with pytest.raises(ValueError, match="Missing required column"):
            model.load_from_csv(str(csv_file))

    def test_load_csv_invalid_minute(self, tmp_path: Path) -> None:
        """CSV with invalid minute should raise ValueError."""
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text("time,oxygen_mg_per_L\n0,5.0\n25,7.5\n")

        model = DegasserModel()
        with pytest.raises(ValueError, match="must be in range"):
            model.load_from_csv(str(csv_file))

    def test_load_csv_invalid_oxygen(self, tmp_path: Path) -> None:
        """CSV with invalid oxygen should raise ValueError."""
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text("time,oxygen_mg_per_L\n0,5.0\n1,0.0\n")

        model = DegasserModel()
        with pytest.raises(ValueError, match="must be > 0"):
            model.load_from_csv(str(csv_file))


class TestCSVExport:
    """Test CSV export."""

    def test_export_simple_csv(self, tmp_path: Path) -> None:
        """Export measurements to CSV."""
        model = DegasserModel()
        model.set_measurement(0, 8.5)
        model.set_measurement(5, 7.0)

        csv_file = tmp_path / "export.csv"
        model.export_csv(str(csv_file), include_temperature=False)

        # Read it back and verify
        with csv_file.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0] == {"minute": "0", "oxygen_mg_per_L": "8.5"}
        assert rows[1] == {"minute": "5", "oxygen_mg_per_L": "7.0"}

    def test_export_with_temperatue(self, tmp_path: Path) -> None:
        """Export measurements to CSV with temperature."""
        model = DegasserModel()
        model.set_measurement(0, 8.5)
        model.set_temperature(23.5)

        csv_file = tmp_path / "export.csv"
        model.export_csv(str(csv_file), include_temperature=True)

        with csv_file.open() as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["temperature_c"] == "23.5"


# ====================================================================================
# TEST TABLE TESTS
# ====================================================================================
class TestTableTests:
    """Test the test results table."""

    def test_initial_rows_have_descriptions(self) -> None:
        """Model should initialize with default test descriptions."""
        model = DegasserModel()
        rows = model.get_test_rows()

        # Should have 7 rows
        assert len(rows) == NUM_TEST_ROWS
        # All should have descriptions but empty other fields
        assert all(r.description for r in rows)
        assert all(r.pass_fail == "" for r in rows)

    def test_update_test_row(self) -> None:
        """Update a test row should update the model."""
        model = DegasserModel()
        model.update_test_row(0, pass_fail="Pass", measured=5.0)

        rows = model.get_test_rows()
        assert rows[0].pass_fail == "Pass"
        assert rows[0].measured == 5.0

    def test_update_invalid_row_index(self) -> None:
        """Update a test row with an invalid index should raise ValueError."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="out of range"):
            model.update_test_row(99, pass_fail="Fail")

    def test_auto_pass_fail_validation_within_spec(self) -> None:
        """Measured value within spec range should auto-set Pass/Fail to 'Pass'."""
        model = DegasserModel()

        # Row 0 is vacuum_pressure with spec (None, -22)
        # Any value <= -22 should pass
        model.update_test_row(0, measured=-25.0)
        rows = model.get_test_rows()
        assert rows[0].pass_fail == "Pass"

        # Row 1 is flow_rate with spec (300, 700)
        # Value of 500 should pass
        model.update_test_row(1, measured=500.0)
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Pass"

        # Test boundary values
        model.update_test_row(1, measured=300.0)  # Min boundary
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Pass"

        model.update_test_row(1, measured=700.0)  # Max boundary
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Pass"

    def test_auto_pass_fail_validation_outside_spec(self) -> None:
        """Measured value outside spec range should auto-set Pass/Fail to 'Fail'."""
        model = DegasserModel()

        # Row 1 is flow_rate with spec (300, 700)
        # Value of 800 should fail (above max)
        model.update_test_row(1, measured=800.0)
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Fail"

        # Value of 200 should fail (below min)
        model.update_test_row(1, measured=200.0)
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Fail"

    def test_auto_pass_fail_validation_clears_on_empty(self) -> None:
        """Clearing measured value should clear Pass/Fail."""
        model = DegasserModel()

        # Set a passing value first
        model.update_test_row(1, measured=500.0)
        rows = model.get_test_rows()
        assert rows[1].pass_fail == "Pass"

        # Clear the measured value
        model.update_test_row(1, measured="")
        rows = model.get_test_rows()
        assert rows[1].measured is None
        assert rows[1].pass_fail == ""

    def test_specs_initialized_from_config(self) -> None:
        """Test rows should be initialized with spec ranges from config."""
        model = DegasserModel()
        rows = model.get_test_rows()

        # Row 0: vacuum_pressure (None, -22)
        assert rows[0].spec_min is None
        assert rows[0].spec_max == DS50_SPEC_RANGES["vacuum_pressure"][1]

        # Row 1: flow_rate (300, 700)
        assert rows[1].spec_min == DS50_SPEC_RANGES["flow_rate"][0]
        assert rows[1].spec_max == DS50_SPEC_RANGES["flow_rate"][1]

        # Row 2: do_level (None, 3.0)
        assert rows[2].spec_min is None
        assert rows[2].spec_max == DS50_SPEC_RANGES["do_level"][1]

        # Row 3: Header row - no specs
        assert rows[3].spec_min is None
        assert rows[3].spec_max is None

        # Row 4: recirculation_start (7.0, None)
        assert rows[4].spec_min == DS50_SPEC_RANGES["recirculation_start"][0]
        assert rows[4].spec_max is None


# ====================================================================================
# METADATA TESTS
# ====================================================================================
class TestMetadataHandling:
    """Test the metadata handling."""

    def test_set_metadata_field(self) -> None:
        """Set a metadata field should update the model."""
        model = DegasserModel()
        model.set_metadata_field("tester_name", "Alice")
        model.set_metadata_field("ds50_serial", "DS50-1234")

        metadata = model.get_metadata()
        assert metadata.tester_name == "Alice"
        assert metadata.ds50_serial == "DS50-1234"

    def test_set_invalid_metadata_field(self) -> None:
        """Set a metadata field with an invalid name should raise ValueError."""
        model = DegasserModel()
        with pytest.raises(ValueError, match="Unknown metadata field"):
            model.set_metadata_field("invalid_field", "value")

    def test_metadata_has_default_date(self) -> None:
        """Metadata should initialize with the current date."""
        model = DegasserModel()
        metadata = model.get_metadata()
        assert metadata.test_date is not None
        assert isinstance(metadata.test_date, date)
