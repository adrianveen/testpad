from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Sequence, Optional

"""
Data Flow (Dissolved O2 Tab)
--------------------------------
Inputs (future):
  - Primary data file (planned): .csv or .txt with columns:
        timestamp (ISO/string), temperature_c (float), oxygen_ppm OR sensor_counts (int/float)
  - Optional calibration file: .yaml containing calibration coefficients:
        {
          "sensor": "XYZ123",
          "slope": <float>,
          "offset": <float>,
          "temperature_comp": { "a": <float>, "b": <float> }
        }

Planned Processing Steps:
  1. load_from_file(path): lightweight parse → cache raw fields
  2. apply_calibration(): convert raw sensor counts → oxygen_ppm (if needed)
  3. compute_summary(): derive aggregates (mean, min, max)
  4. expose state via get_state() / to_dict() for UI + persistence

State Keys (DissolvedO2State):
  loaded        : bool          - Has a file been (successfully) loaded
  source_path   : str | None    - Absolute path to last loaded file
  temperature_c : float | None  - Last parsed (or computed) temperature
  oxygen_ppm    : float | None  - Last parsed or calibrated dissolved oxygen value

Outputs:
  - DissolvedO2State object (immutable snapshot via get_state())
  - Dict form (for serialization / saving UI session state)

Non-Goals (current phase):
  - Real parsing / calibration math
  - Multi-file aggregation
  - Background threading (handled later by presenter/service layer)
"""

@dataclass
class DissolvedO2State:
    loaded: bool = False
    source_path: str | None = None
    temperature_c: float | None = None
    oxygen_ppm: float | None = None


class DissolvedO2Model:
    """In-memory state holder + pure data transformations (logic stubbed for now)."""

    def __init__(self) -> None:
        self._state = DissolvedO2State()

    # -------- State Accessors --------
    def get_state(self) -> DissolvedO2State:
        """Return a copy-like snapshot of current state (read-only for callers)."""
        return DissolvedO2State(**asdict(self._state))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for persistence."""
        return asdict(self._state)

    # -------- Mutators / Lifecycle --------
    def reset(self) -> DissolvedO2State:
        """Clear all loaded data back to defaults."""
        self._state = DissolvedO2State()
        return self.get_state()

    def load_from_file(self, path: str) -> DissolvedO2State:
        """
        Stub: register a file as 'loaded'.
        Future: parse file, populate temperature / oxygen.
        """
        self._state.source_path = path
        self._state.loaded = True
        return self.get_state()

    def set_temperature(self, value: float) -> DissolvedO2State:
        """Set (parsed or computed) temperature in °C."""
        self._state.temperature_c = value
        return self.get_state()

    def set_oxygen(self, ppm: float) -> DissolvedO2State:
        """Set dissolved oxygen value (parts per million)."""
        self._state.oxygen_ppm = ppm
        return self.get_state()

    # -------- Future Calibration Hooks (placeholders) --------
    def apply_calibration(self) -> DissolvedO2State:
        """
        Placeholder: will transform raw sensor counts into oxygen_ppm.
        Currently a no-op.
        """
        return self.get_state()

    def compute_summary(self) -> Dict[str, Optional[float]]:
        """
        Placeholder: aggregate statistics (mean/min/max).
        Returns dict with nulls until real data added.
        """
        return {
            "temperature_mean": self._state.temperature_c,
            "oxygen_mean": self._state.oxygen_ppm,
            "oxygen_min": self._state.oxygen_ppm,
            "oxygen_max": self._state.oxygen_ppm,
        }