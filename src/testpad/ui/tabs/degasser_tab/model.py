"""Degasser tab model."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, final

from testpad.config.defaults import DEFAULT_EXPORT_DIR

from .config import (
    DEFAULT_TEST_DATE,
    DEFAULT_TEST_DESCRIPTIONS,
    DS50_SPEC_RANGES,
    HEADER_ROW_INDEX,
    MINIMUM_END_MINUTE,
    ROW_SPEC_MAPPING,
    START_MINUTE,
)

if TYPE_CHECKING:
    from datetime import date


# ------------------ Data Structures ------------------
@dataclass
class TestResultRow:
    """Test result row Data Class."""

    description: str
    pass_fail: str = ""  # "Pass" / "Fail" / "" (UI enforces)
    spec_min: float | None = None
    spec_max: float | None = None
    measured: float | None = None


@dataclass
class TimeSeriesState:
    """Time series state Data Class."""

    loaded: bool
    points_filled: int
    minutes_with_data: list[int]
    temperature_c: float | None = None


@dataclass
class Metadata:
    """Metadata Data Class."""

    tester_name: str = ""
    test_date: date | None = None  # Will be a datetime.date or QDate
    ds50_serial: str = ""
    location: str = ""


# ------------------ Model ------------------
@final
class DegasserModel:
    """Simple model for a 10-minute dissolved O2 test.

    Table A (Test Results):
      - 4 rows.
      - Columns: Description (static), Pass/Fail, Spec_Min, Spec_Max, Data Measured.
      - Only non-description fields user-editable.

    Table B (Time Series):
      - Minutes fixed: 0..10 (inclusive).
      - oxygen_mg_per_L > 0 (float).
      - Stored in _oxygen_data: minute -> value.

    Temperature:
      - Single optional static value (applies to entire test).

    CSV Import:
      - Flexible headers for time & oxygen:
          time aliases: time, Time, minute, minutes, t_min
          oxygen aliases: oxygen, oxygen_mg_per_L, o2, O2, do2, DO2
          (temperature optional: temperature_c, temp_c, Temperature, temp)
      - Minutes coerced to int; must be 0..10.
      - Oxygen must be > 0.

    Errors:
      - All validation failures raise ValueError (UI should catch and display).

    """

    def __init__(self) -> None:
        """Initialize a new DegasserModel instance.

        The model is initialized with an empty time series and a default set of test
        result rows. The temperature is set to None, and the metadata is initialized
        with the default test date.

        """
        self._oxygen_data: dict[int, float] = {}
        self._temperature_c: float | None = None
        self._test_rows: list[TestResultRow] = self._create_default_test_rows()
        self._source_path: str | None = None
        self._output_directory: Path = DEFAULT_EXPORT_DIR

        self._metadata = Metadata(test_date=DEFAULT_TEST_DATE())

    @staticmethod
    def _create_default_test_rows() -> list[TestResultRow]:
        """Create test result rows initialized with spec ranges from config.

        Returns:
            List of TestResultRow objects with descriptions and spec ranges populated.

        """
        rows = []
        for row_idx, description in enumerate(DEFAULT_TEST_DESCRIPTIONS):
            # Look up spec key for this row (None for header row)
            spec_key = ROW_SPEC_MAPPING[row_idx]

            if spec_key is not None:
                # Get spec range from config
                spec_range = DS50_SPEC_RANGES.get(spec_key, (None, None))
                spec_min, spec_max = spec_range
            else:
                # Header row - no specs
                spec_min, spec_max = None, None

            rows.append(
                TestResultRow(
                    description=description,
                    spec_min=spec_min,
                    spec_max=spec_max,
                )
            )
        return rows

    # -------- Validation Helpers --------
    @staticmethod
    def _validate_minute(minute: int) -> None:
        """Ensure minute identifier is an integer within the allowed 0..10 window."""
        if not isinstance(minute, int):
            msg = "Minute must be an integer."
            raise TypeError(msg)
        if minute < START_MINUTE or minute > MINIMUM_END_MINUTE:
            msg = f"Minute must be in range {START_MINUTE}..{MINIMUM_END_MINUTE}."
            raise ValueError(msg)

    @staticmethod
    def _coerce_minute(raw: str) -> int:
        """Parse a raw time value into a valid minute slot, raise if coercion fails."""
        try:
            m = int(float(raw))
        except Exception as e:
            msg = f"Time value not numeric: {raw}"
            raise ValueError(msg) from e
        DegasserModel._validate_minute(m)
        return m

    @staticmethod
    def _validate_oxygen(value: float | str) -> float:
        """Normalize oxygen readings to float and enforce the > 0 mg/L requirement."""
        try:
            v = float(value)
        except Exception as e:
            msg = f"Oxygen value not numeric: {value}"
            raise ValueError(msg) from e
        if v <= 0:
            msg = "Oxygen (mg/L) must be > 0."
            raise ValueError(msg)
        return v

    # -------- Metadata API --------
    def set_metadata_field(self, field: str, value: str | date) -> None:
        """Update a metadata field."""
        if not hasattr(self._metadata, field):
            msg = f"Unknown metadata field: {field}"
            raise ValueError(msg)
        setattr(self._metadata, field, value)

    def get_metadata(self) -> Metadata:
        """Return a copy of the current metadata."""
        return Metadata(**asdict(self._metadata))

    # -------- Time Series API --------
    def set_measurement(self, minute: int, oxygen_mg_per_l: float) -> TimeSeriesState:
        """Insert or update the oxygen reading for a specific minute slot."""
        self._validate_minute(minute)
        self._oxygen_data[minute] = self._validate_oxygen(oxygen_mg_per_l)
        return self.get_state()

    def clear_measurement(self, minute: int) -> TimeSeriesState:
        """Remove any stored reading for the given minute (no-op if missing)."""
        self._validate_minute(minute)
        self._oxygen_data.pop(minute, None)
        return self.get_state()

    def list_measurements(self) -> list[tuple[int, float]]:
        """Return the stored readings sorted by minute for stable UI rendering."""
        return sorted(self._oxygen_data.items())

    def build_time_series_rows(self) -> list[tuple[int, float | None]]:
        """Return the time series data as a list of rows for the UI table."""
        return [
            (m, self._oxygen_data.get(m))
            for m in range(START_MINUTE, MINIMUM_END_MINUTE + 1)
        ]

    # -------- Temperature --------
    def set_temperature(self, temperature_c: float | str) -> TimeSeriesState:
        """Store the shared bath temperature, coercing numeric inputs to float."""
        try:
            t = float(temperature_c)
        except Exception as e:
            msg = "Temperature must be numeric."
            raise ValueError(msg) from e
        self._temperature_c = t
        return self.get_state()

    def clear_temperature(self) -> TimeSeriesState:
        """Reset the optional temperature reading back to an unset state."""
        self._temperature_c = None
        return self.get_state()

    def get_temperature_c(self) -> float | None:
        """Return the current temperature reading, or None if unset."""
        return self._temperature_c

    # -------- Test Results Table --------
    def update_test_row(
        self,
        index: int,
        pass_fail: str | None = None,
        spec_min: float | str | None = None,
        spec_max: float | str | None = None,
        measured: float | str | None = None,
    ) -> list[TestResultRow]:
        """Update a row in the test results table.

        Mutate a single test-result row, coercing numerics and returning a copy list.

        Args:
            index: The index of the row to update.
            pass_fail: The new pass/fail value for the row.
            spec_min: The new spec min value for the row.
            spec_max: The new spec max value for the row.
            measured: The new measured value for the row.

        Raises:
            ValueError: If the index is out of range.

        """
        if not (0 <= index < len(self._test_rows)):
            msg = "Test row index out of range."
            raise ValueError(msg)
        row = self._test_rows[index]

        # Update spec fields first (if provided)
        if spec_min is not None:
            row.spec_min = float(spec_min)
        if spec_max is not None:
            row.spec_max = float(spec_max)

        # Update measured value (if provided)
        if measured is not None:
            # Handle empty string as clearing the measured value
            if str(measured).strip() == "":
                row.measured = None
            else:
                row.measured = float(measured)

        # Auto-validate Pass/Fail ONLY if pass_fail was not explicitly provided
        # and measured value was updated
        self._auto_validate_pass_fail(row)

        # If pass_fail was explicitly provided, use that (overrides auto-validation)
        if pass_fail is not None:
            row.pass_fail = pass_fail

        return self.get_test_rows()

    def _auto_validate_pass_fail(self, row: TestResultRow) -> None:
        """Auto-validate the pass/fail status of a test row.

        This method is called after a test row is updated with measured value.
        It checks the measured value against the spec range and updates the
        pass/fail status accordingly.

        Args:
            row: The test row to validate.

        """
        if row.measured is None:
            # Clear pass/fail if measured value is cleared
            row.pass_fail = ""
        elif row.spec_min is not None or row.spec_max is not None:
            # Check against spec limits (None means no limit on that end)
            # Type narrowing: row.measured is guaranteed non-None here
            measured_val = row.measured
            passes_min = row.spec_min is None or measured_val >= row.spec_min
            passes_max = row.spec_max is None or measured_val <= row.spec_max

            if passes_min and passes_max:
                row.pass_fail = "Pass"  # noqa: S105
            else:
                row.pass_fail = "Fail"  # noqa: S105

    def get_test_rows(self) -> list[TestResultRow]:
        """Return deep-copied test rows so callers cannot mutate internal state."""
        return [TestResultRow(**asdict(r)) for r in self._test_rows]

    # -------- CSV Load / Save --------
    @staticmethod
    def _resolve_header(
        headers: set[str],
        candidates: set[str],
        required_col: bool,
    ) -> str | None:
        """Resolve a column header from a set of candidates."""
        for h in headers:
            if h in candidates:
                return h
        if required_col:
            expected = sorted(candidates)
            msg = f"Missing required column; expected one of: {expected}"
            raise ValueError(msg)
        return None

    def load_from_csv(self, path: str) -> TimeSeriesState:
        """Load time series from CSV.

        Headers (one of each required):
          time aliases: time, Time, minute, minutes, t_min
          oxygen aliases: oxygen, oxygen_mg_per_L, o2, O2, do2, DO2
          temperature (optional): temperature_c, temp_c, Temperature, temp.

        Args:
            path (str): The file path to load the CSV data from.

        Raises:
            ValueError on first invalid row.

        """
        time_aliases = {"time", "Time", "minute", "minutes", "t_min"}
        oxy_aliases = {"oxygen", "oxygen_mg_per_L", "o2", "O2", "do2", "DO2"}
        temp_aliases = {"temperature_c", "temp_c", "Temperature", "temp"}

        self._source_path = path
        with Path(path).open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                msg = "CSV missing header row."
                raise ValueError(msg)
            headers = set(reader.fieldnames)

            time_col = self._resolve_header(headers, time_aliases, required_col=True)
            oxy_col = self._resolve_header(headers, oxy_aliases, required_col=True)
            temp_col = self._resolve_header(headers, temp_aliases, required_col=False)

            # Start fresh
            self._oxygen_data.clear()

            # Type narrowing:
            # time_col and oxy_col are not None because required_col=True
            if time_col is None:
                msg = "Internal error: time_col not resolved when required."
                raise RuntimeError(msg)
            if oxy_col is None:
                msg = "Internal error: oxy_col not resolved when required."
                raise RuntimeError(msg)

            for line_no, row in enumerate(reader, start=2):
                raw_time = row.get(time_col, "").strip()
                raw_oxy = row.get(oxy_col, "").strip()
                if raw_time == "" or raw_oxy == "":
                    msg = f"Blank time or oxygen at line {line_no}."
                    raise ValueError(msg)
                minute = self._coerce_minute(raw_time)
                oxy_val = self._validate_oxygen(raw_oxy)
                self._oxygen_data[minute] = oxy_val  # overwrite if duplicate
                if temp_col:
                    raw_temp = row.get(temp_col, "").strip()
                    if raw_temp:
                        try:
                            self._temperature_c = float(raw_temp)
                        except ValueError as e:
                            msg = f"Invalid temperature at line {line_no}: {raw_temp}"
                            raise ValueError(msg) from e

        return self.get_state()

    def export_csv(
        self,
        path: str,
        include_temperature: bool = True,
    ) -> None:
        """Write the time-series data (and optional temperature) to a tidy CSV file.

        Args:
            path (str): The file path to write the CSV data to.
            include_temperature (bool): If True, includes the temperature
                column if set. Defaults to True.

        """
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            cols = ["minute", "oxygen_mg_per_L"]
            if include_temperature and self._temperature_c is not None:
                cols.append("temperature_c")
            writer.writerow(cols)
            for minute, oxy in self.list_measurements():
                row = [minute, oxy]
                if include_temperature and self._temperature_c is not None:
                    row.append(self._temperature_c)
                writer.writerow(row)

    # -------- Output Directory --------
    def get_output_directory(self) -> Path:
        """Get the current output directory.

        Returns:
            Path: The current output directory.

        """
        return self._output_directory

    def set_output_directory(self, path: Path) -> None:
        """Set the output directory for reports.

        Args:
            path: The new output directory.

        Raises:
            ValueError: If the path is not absolute.

        """
        path = Path(path)
        if not path.is_absolute():
            msg = "Output directory must be absolute."
            raise ValueError(msg)

        self._output_directory = path

    # -------- State / Reset / Serialization --------
    def reset(self) -> TimeSeriesState:
        """Restore the model to a pristine state with default rows and no data."""
        self._oxygen_data.clear()
        self._temperature_c = None
        self._test_rows = self._create_default_test_rows()
        self._source_path = None
        self._metadata = Metadata(test_date=DEFAULT_TEST_DATE())
        return self.get_state()

    def validate_for_report(self) -> list[str]:
        """Check for missing or empty values before report generation.

        This is a soft validation - reporst can be generated with missing data,
        but users should be warned about what is missing.

        Returns:
            List of human-readable warning messages about missing data.
            Empty list if all fields are populated.

        """
        warnings = []

        # Metadata validation
        if not self._metadata.tester_name or not self._metadata.tester_name.strip():
            warnings.append("'Tester Name'")
        if not self._metadata.test_date:
            warnings.append("'Test Date'")
        if not self._metadata.ds50_serial or not self._metadata.ds50_serial.strip():
            warnings.append("'DS50 Serial Number'")
        if not self._metadata.location or not self._metadata.location.strip():
            warnings.append("'Location'")

        # Test Table validation
        for idx, row in enumerate(self._test_rows):
            if idx == HEADER_ROW_INDEX:
                continue
            # Get the test description and strip whitespace/punctuation
            desc = DEFAULT_TEST_DESCRIPTIONS[idx].rstrip(":").strip().split(" {", 1)[0]

            # Check measured value
            if row.measured is None:
                warnings.append(f"'{desc}' measurement")

            # Check pass/fail value
            if not row.pass_fail or not row.pass_fail.strip():
                warnings.append(f"'{desc}' pass/fail")

        # Time Series validation
        if not self._oxygen_data:
            warnings.append("Dissolved Oxygen measurements")

        return warnings

    def get_state(self) -> TimeSeriesState:
        """Snapshot the current model state for presenter/view consumption."""
        return TimeSeriesState(
            loaded=bool(self._oxygen_data),
            points_filled=len(self._oxygen_data),
            temperature_c=self._temperature_c,
            minutes_with_data=sorted(self._oxygen_data.keys()),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the model to primitive types for persistence or debugging.

        Returns:
            Dict: A dictionary representation of the model state.

        Dict Keys:
            - "time_series": dict[int, float] - minute to oxygen mapping.
            - "temperature_c": float | None - the bath temperature.
            - "test_table": list[dict[str, Any]] - list of test result rows as dicts.
            - "source_path": str | None - path of last loaded CSV, if any.
            - "metadata": dict[str, Any] - metadata fields as a dict.

        """
        # Persistence breadcrumb:
        # - Mirror this structure with `state_schema.json`.
        # - Future helper: add `from_dict` to rehydrate `_oxygen_data`,
        #   `_temperature_c`, `_test_rows`, `_source_path`, and metadata once
        #   presenter captures it.
        return {
            "time_series": dict(self._oxygen_data.items()),
            "temperature_c": self._temperature_c,
            "test_table": [asdict(r) for r in self.get_test_rows()],
            "source_path": self._source_path,
            "metadata": asdict(self._metadata),
        }
