from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from typing import Any, Dict, List, Optional

from testpad.ui.tabs.burning_tab import BurninTab
from testpad.core.burnin.config import DEFAULT_TEST_DATE


# ------------------ Data Structures ------------------
@dataclass
class Metadata:
    tested_by: str = ""
    test_date: date | None = None  # Will be datetime.date
    rk300_serial: str = ""
    test_name: str = ""


# ------------------ Model ------------------
class BurningModel:
    """Model for burnin tab.

    Metadata:
        tested_by: Name of the person who ran the test.
        test_date: Date of the test.
        rk300_serial: RK-300 serial number.
        test_name: Name of the test.

    Burning Stats:
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
        self._meta_data = Metadata(test_date=DEFAULT_TEST_DATE)
        burnin_tab = BurninTab()
        pos_stats = burnin_tab.stats.positive_stats
        neg_stats = burnin_tab.stats.negative_stats
