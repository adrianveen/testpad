"""View state data structures for the degasser tab.

This module defines the ViewState pattern data structures used to communicate
between the Presenter and View layers.
"""

from dataclasses import dataclass, field
from datetime import date

from testpad.ui.tabs.degasser_tab.model import TestResultRow


@dataclass(frozen=True)
class DegasserViewState:
    """Immutable snapshot of all data to display in the degasser view.

    This class represents the complete UI state. The Presenter creates instances
    of this class from the Model, and the View renders them.
    """

    # Metadata Fields
    tester_name: str = ""
    location: str = ""
    ds50_serial: str = ""
    test_date: date | None = None

    # Time Series Chart Data
    time_series_measurements: list[tuple[int, float]] = field(default_factory=list)
    temperature_c: float | None = None

    # Test Table Data (we'll expand this in Phase 3)
    test_rows: list[TestResultRow] = field(default_factory=list)

    # Time Series Table Data (we'll expand this in Phase 3)
    time_series_table_rows: list[tuple[int, float | None]] = field(
        default_factory=list,
    )
