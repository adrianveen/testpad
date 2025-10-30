from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import TYPE_CHECKING

from testpad.core.burnin.config import DEFAULT_TEST_DATE

if TYPE_CHECKING:
    from datetime import date

    from PySide6.QtCore import QDate


# ------------------ Data Structures ------------------
@dataclass
class Metadata:
    tested_by: str = ""
    test_date: date | None = None
    test_name: str = ""
    rk300_serial: str = ""


# ------------------ Model ------------------
class BurninModel:
    """Model for burnin tab.

    Metadata:
        tested_by: Name of the person who ran the test.
        test_date: Date of the test.
        rk300_serial: RK-300 serial number.
        test_name: Name of the test.

    Burn-in Stats:
        mean: Mean value of the burnin.
        median: Median value of the burnin.
        min: Minimum value of the burnin.
        max: Maximum value of the burnin.
        std: Standard deviation of the burnin.
        variance: Variance of the burnin.
        25th_percentile: 25th percentile of the burnin.
        75th_percentile: 75th percentile of the burnin.
        skewness: Skewness of the burnin.
        kurtosis: Kurtosis of the burnin.
        prcnt_above_thresh: Percentage of values above the threshold.
        prcnt_below_thresh: Percentage of values below the threshold.
        num_peaks_above_thresh: Number of peaks above the threshold.
        num_peaks_below_thresh: Number of peaks below the threshold.

    Burnin stats calcualted for both positive and negative motor directions.

    """

    def __init__(self) -> None:
        """Initialize BurninModel with default metadata.

        The default metadata will have a test date of DEFAULT_TEST_DATE.
        """
        self._meta_data = Metadata(test_date=DEFAULT_TEST_DATE())

    def update_metadata(self, data: dict) -> None:
        """Update metadata with given data.

        Args:
            data: A dictionary containing the metadata to be updated.

        Raises:
            ValueError: If the metadata field does not exist.

        """
        # Filter valid fields
        valid = [f.name for f in fields(Metadata)]

        for k, v in data.items():
            if k in valid:
                if k == "test_date" and isinstance(v, QDate):
                    v = v.toPython()
                setattr(self._meta_data, k, v)

    def get_metadata(self) -> Metadata:
        """Return a copy of the current metadata."""
        return Metadata(**asdict(self._meta_data))
