from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Iterable
from datetime import date
import csv
from .config import (
    MIN_MINUTE,
    MAX_MINUTE,
    DEFAULT_TEST_DESCRIPTIONS
)

# ------------------ Data Structures ------------------
@dataclass
class TestResultRow:
    description: str
    pass_fail: str = ""          # "Pass" / "Fail" / "" (UI enforces)
    spec_min: Optional[float] = None
    spec_max: Optional[float] = None
    measured: Optional[float] = None

@dataclass
class DissolvedO2State:
    loaded: bool
    points_filled: int
    temperature_c: float | None
    minutes_with_data: List[int]

@dataclass
class Metadata:
    tester_name: str = ""
    test_date: date | None = None # Will be a datetime.date or QDate
    ds50_serial: str = ""
    location: str = ""

# ------------------ Model ------------------
class DegasserModel:
    """
    Simple model for a 10-minute dissolved O2 test.

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
        self._oxygen_data: Dict[int, float] = {}
        self._temperature_c: float | None = None
        self._test_rows: List[TestResultRow] = [
            TestResultRow(desc) for desc in DEFAULT_TEST_DESCRIPTIONS
        ]
        self._source_path: str | None = None

        self._metadata = Metadata()

    # -------- Validation Helpers --------
    @staticmethod
    def _validate_minute(minute: int) -> None:
        """Ensure the minute identifier is an integer within the allowed 0..10 window."""
        if not isinstance(minute, int):
            raise ValueError("Minute must be an integer.")
        if minute < MIN_MINUTE or minute > MAX_MINUTE:
            raise ValueError(f"Minute must be in range {MIN_MINUTE}..{MAX_MINUTE}.")

    @staticmethod
    def _coerce_minute(raw: str) -> int:
        """Parse a raw time value into a valid minute slot, raising if coercion fails."""
        try:
            m = int(float(raw))
        except Exception as e:
            raise ValueError(f"Time value not numeric: {raw}") from e
        DegasserModel._validate_minute(m)
        return m

    @staticmethod
    def _validate_oxygen(value: float | str | int) -> float:
        """Normalize an oxygen reading to float and enforce the > 0 mg/L requirement."""

        try:
            v = float(value)
        except Exception as e:
            raise ValueError(f"Oxygen value not numeric: {value}") from e
        if v <= 0:
            raise ValueError("Oxygen (mg/L) must be > 0.")
        return v

    # -------- Metadata API --------
    def set_metadata_field(self, field: str, value: Any) -> None:
        """Update a metadata field."""
        if not hasattr(self._metadata, field):
            raise ValueError(f"Unknown metadata field: {field}")
        setattr(self._metadata, field, value)
    def get_metadata(self) -> Metadata:
        """Return a copy of the current metadata."""
        return Metadata(**asdict(self._metadata))
    # -------- Time Series API --------
    def set_measurement(self, minute: int, oxygen_mg_per_L: float) -> DissolvedO2State:
        """Insert or update the oxygen reading for a specific minute slot."""
        self._validate_minute(minute)
        self._oxygen_data[minute] = self._validate_oxygen(oxygen_mg_per_L)
        return self.get_state()

    def bulk_set_measurements(self, pairs: Iterable[tuple[int, float]]) -> DissolvedO2State:
        """Apply multiple minute/value pairs, validating each in sequence."""
        for m, v in pairs:
            self.set_measurement(m, v)
        return self.get_state()

    def clear_measurement(self, minute: int) -> DissolvedO2State:
        """Remove any stored reading for the given minute (no-op if missing)."""
        self._validate_minute(minute)
        self._oxygen_data.pop(minute, None)
        return self.get_state()

    def list_measurements(self) -> List[tuple[int, float]]:
        """Return the stored readings sorted by minute for stable UI rendering."""
        return sorted(self._oxygen_data.items())

    def build_time_series_rows(self) -> List[tuple[int, Optional[float]]]:
        """Generate an 11-row minute grid with gaps filled by ``None`` for the UI table."""
        return [(m, self._oxygen_data.get(m)) for m in range(MIN_MINUTE, MAX_MINUTE + 1)]

    # -------- Temperature --------
    def set_temperature(self, temperature_c: float | str | int) -> DissolvedO2State:
        """Store the shared bath temperature, coercing numeric inputs to float."""
        try:
            t = float(temperature_c)
        except Exception as e:
            raise ValueError("Temperature must be numeric.") from e
        self._temperature_c = t
        return self.get_state()

    def clear_temperature(self) -> DissolvedO2State:
        """Reset the optional temperature reading back to an unset state."""
        self._temperature_c = None
        return self.get_state()
    def get_temperature_c(self) -> float | None:
        """Return the current temperature reading, or None if unset."""
        return self._temperature_c

    # -------- Test Results Table --------
    def update_test_row(self,
                        index: int,
                        pass_fail: Optional[str] = None,
                        spec_min: Optional[float | str] = None,
                        spec_max: Optional[float | str] = None,
                        measured: Optional[float | str] = None) -> List[TestResultRow]:
        """Mutate a single test-result row, coercing numerics and returning a copy list."""
        if not (0 <= index < len(self._test_rows)):
            raise ValueError("Test row index out of range.")
        row = self._test_rows[index]
        if pass_fail is not None:
            row.pass_fail = pass_fail
        if spec_min is not None:
            row.spec_min = float(spec_min)
        if spec_max is not None:
            row.spec_max = float(spec_max)
        if measured is not None:
            row.measured = float(measured)
        return self.get_test_rows()

    def get_test_rows(self) -> List[TestResultRow]:
        """Return deep-copied test rows so callers cannot mutate internal state."""
        return [TestResultRow(**asdict(r)) for r in self._test_rows]

    def set_test_descriptions(self, descriptions: List[str]) -> None:
        """
        Developer utility (not user-facing).
        Reassigns the static description column (length must remain 4).
        """
        if len(descriptions) != 4:
            raise ValueError("Exactly 4 descriptions required.")
        for i, desc in enumerate(descriptions):
            self._test_rows[i].description = desc

    # -------- CSV Load / Save --------
    def load_from_csv(self, path: str) -> DissolvedO2State:
        """
        Loads time series from CSV.\n
        Headers (one of each required):
          time aliases: time, Time, minute, minutes, t_min
          oxygen aliases: oxygen, oxygen_mg_per_L, o2, O2, do2, DO2
          temperature (optional): temperature_c, temp_c, Temperature, temp
        
        Args:
            path (str): The file path to load the CSV data from.
            
        Raises:
            ValueError on first invalid row.
        """
        time_aliases = {"time", "Time", "minute", "minutes", "t_min"}
        oxy_aliases = {"oxygen", "oxygen_mg_per_L", "o2", "O2", "do2", "DO2"}
        temp_aliases = {"temperature_c", "temp_c", "Temperature", "temp"}

        self._source_path = path
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV missing header row.")
            headers = set(reader.fieldnames)

            def resolve(candidates: set[str], required: bool) -> Optional[str]:
                for h in headers:
                    if h in candidates:
                        return h
                if required:
                    raise ValueError(f"Missing required column; expected one of: {sorted(candidates)}")
                return None

            time_col = resolve(time_aliases, True)
            oxy_col = resolve(oxy_aliases, True)
            temp_col = resolve(temp_aliases, False)

            # Start fresh
            self._oxygen_data.clear()

            for line_no, row in enumerate(reader, start=2):
                raw_time = row.get(time_col, "").strip()
                raw_oxy = row.get(oxy_col, "").strip()
                if raw_time == "" or raw_oxy == "":
                    raise ValueError(f"Blank time or oxygen at line {line_no}.")
                minute = self._coerce_minute(raw_time)
                oxy_val = self._validate_oxygen(raw_oxy)
                self._oxygen_data[minute] = oxy_val  # overwrite if duplicate
                if temp_col:
                    raw_temp = temp_col
                    if raw_temp:
                        try:
                            self._temperature_c = float(raw_temp)
                        except ValueError:
                            raise ValueError(f"Invalid temperature at line {line_no}: {raw_temp}")

        return self.get_state()

    def export_csv(self, path: str, include_temperature: bool = True) -> None:
        """Write the time-series data (and optional temperature) to a tidy CSV file.
        
        Args:
            path (str): The file path to write the CSV data to.
            include_temperature (bool): If True, includes the temperature column if set.
                Defaults to True.
        """
        with open(path, "w", newline="", encoding="utf-8") as f:
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

    # -------- State / Reset / Serialization --------
    def reset(self) -> DissolvedO2State:
        """Restore the model to a pristine state with default rows and no data."""
        self._oxygen_data.clear()
        self._temperature_c = None
        self._test_rows = [TestResultRow(desc) for desc in DEFAULT_TEST_DESCRIPTIONS]
        self._source_path = None
        self._metadata = Metadata()
        return self.get_state()

    def get_state(self) -> DissolvedO2State:
        """Snapshot the current model state for presenter/view consumption."""
        return DissolvedO2State(
            loaded=bool(self._oxygen_data),
            points_filled=len(self._oxygen_data),
            temperature_c=self._temperature_c,
            minutes_with_data=sorted(self._oxygen_data.keys()),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the model to primitive types for persistence or debugging.
        
        Returns:
            Dict: A dictionary representation of the model state.
        
        Dict Keys:
            - "time_series": Dict[int, float] - minute to oxygen mapping.
            - "temperature_c": float | None - the bath temperature.
            - "test_table": List[Dict[str, Any]] - list of test result rows as dicts.
            - "source_path": str | None - path of last loaded CSV, if any.
            - "metadata": Dict[str, Any] - metadata fields as a dict.
        """
        # Persistence breadcrumb:
        # - Mirror this structure with `state_schema.json`.
        # - Future helper: add `from_dict` to rehydrate `_oxygen_data`, `_temperature_c`,
        #   `_test_rows`, `_source_path`, and metadata once presenter captures it.
        return {
            "time_series": {str(k): v for k, v in self._oxygen_data.items()},
            "temperature_c": self._temperature_c,
            "test_table": [asdict(r) for r in self.get_test_rows()],
            "source_path": self._source_path,
            "metadata": asdict(self._metadata),
        }
