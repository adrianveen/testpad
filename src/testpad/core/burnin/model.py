"""Model for burnin tab."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, fields
from datetime import date
from typing import TYPE_CHECKING, final

import h5py
import numpy as np

from testpad.core.burnin.config import DEFAULT_TEST_DATE

if TYPE_CHECKING:
    from pathlib import Path


# ------------------ Data Structures ------------------
@dataclass
class Metadata:
    """Metadata for the burnin tab.

    Attributes:
        tested_by: Name of the person who ran the test.
        test_date: Date of the test.
        rk300_serial: RK-300 serial number.
        test_name: Name of the test.

    """

    tested_by: str = ""
    test_date: date | None = None
    test_name: str = ""
    rk300_serial: str = ""


@dataclass
class BurninGraphOptions:
    """Settings for the burnin tab.

    Attributes:
        print_stats: Whether to print the statistics.
        separate_errors: Whether to show the error values separated by direction.
        moving_average: Whether to show the moving average.
        threshold: Threshold for the error values.
        direction: Direction of the motor.

    """

    print_stats: bool = False
    separate_errors: bool = False
    moving_average: bool = False


@dataclass
class BurninFileInfo:
    """Information for the burnin file.

    Attributes:
        axis_names: Axis name for the burnin file.
        test_number: test number for the burnin file.

    """

    file_path: Path
    axis_name: str | None = None
    test_number: int | None = None

    @classmethod
    def from_path(cls, path: Path) -> BurninFileInfo:
        """Create a BurninFileInfo object from a path.

        Args:
            path: Path to the burnin file.

        Returns:
            BurninFileInfo: A BurninFileInfo object.

        """
        # Extract the axis name and test number from the file name
        axis = cls._extract_axis_name(path)
        test_num = cls._extract_test_number(path)
        return cls(path, axis, test_num)

    @staticmethod
    def _extract_axis_name(path: Path) -> str | None:
        """Extract the axis name from the file name.

        Args:
            path: Path to the burnin file.

        Returns:
            str: The axis name.

        """
        # Extract the axis name from the file name
        if "_axis_A_" in path.name:
            return "A"
        if "_axis_B_" in path.name:
            return "B"
        return None

    @staticmethod
    def _extract_test_number(path: Path) -> int:
        """Extract the test number from the file name.

        Args:
            path: Path to the burnin file.

        Returns:
            int: The test number.

        """
        # Extract the test number from the file name
        match = re.search(r"error_(\d+)", path.name)
        return int(match.group(1)) if match else -1


@dataclass
class BurninData:
    time: np.ndarray
    error: np.ndarray
    positive_errors: np.ndarray
    negative_errors: np.ndarray
    axis_name: str | None
    test_number: int | None


# ------------------ Model ------------------
@final
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
        self._print_stats_option: bool = False
        self._separate_errors_option: bool = False
        self._moving_average_option: bool = False
        self._burnin_file_infos: list[BurninFileInfo] = []
        self._output_folder: Path | None = None
        self._output_file: Path | None = None

    """
    ======== Print Stats Settings ========
    """

    def set_print_stats_option(self) -> None:
        """Toggle the print stats option."""
        self._print_stats_option = not self._print_stats_option

    def get_print_stats_option(self) -> bool:
        """Return the print stats option."""
        return self._print_stats_option

    """
    ======== Separate Errors Settings ========
    """

    def set_separate_errors_option(self) -> None:
        """Toggle the separate errors option."""
        self._separate_errors_option = not self._separate_errors_option

    def get_separate_errors_option(self) -> bool:
        """Return the separate errors option."""
        return self._separate_errors_option

    """
    ======== Moving Average Settings ========
    """

    def set_moving_average_option(self) -> None:
        """Toggle the moving average option."""
        self._moving_average_option = not self._moving_average_option

    def get_moving_average_option(self) -> bool:
        """Return the moving average option."""
        return self._moving_average_option

    """
    ======== Burnin File Settings ========
    """

    def set_burnin_files(self, burnin_file_infos: list[BurninFileInfo]) -> None:
        """Set the burnin file path and stores the info BurninFileInfo objects."""
        self._burnin_file_infos = burnin_file_infos

    def clear_burnin_file(self) -> None:
        """Clear the burnin file path."""
        self._burnin_file_infos = []

    def get_burnin_file(self) -> list[BurninFileInfo]:
        """Return the burnin file path."""
        return self._burnin_file_infos

    def has_burnin_file(self) -> bool:
        """Return True if the burnin file path is not empty."""
        return bool(self._burnin_file_infos)

    """
    ======== Output File Settings ========
    """

    def set_output_folder(self, output_folder: Path) -> None:
        """Set the output folder."""
        self._output_folder = output_folder

    def clear_output_folder(self) -> None:
        """Clear the output folder."""
        self._output_folder = None

    def get_output_folder(self) -> Path | None:
        """Return the output folder."""
        return self._output_folder

    def set_output_file(self, output_file: Path) -> None:
        """Set the output file."""
        self._output_file = output_file

    def clear_output_file(self) -> None:
        """Clear the output file."""
        self._output_file = None

    def get_output_file(self) -> Path | None:
        """Return the output file."""
        return self._output_file

    """
    ======== Burnin Data ========
    """

    def load_burnin_data(self, file_info: BurninFileInfo) -> BurninData:
        """Load burnin data from a file."""
        with h5py.File(file_info.file_path, "r") as f:
            time = np.array(f["Time (s)"])
            error = np.array(f["Error (counts)"])

        positive_errors = np.where(error > 0, error, np.nan)
        negative_errors = np.where(error < 0, error, np.nan)

        return BurninData(
            time,
            error,
            positive_errors,
            negative_errors,
            file_info.axis_name or "Unknown",
            file_info.test_number,
        )

    def calculate_moving_average(
        self, array: np.ndarray, window: int = 10000
    ) -> np.ndarray:
        """Calculate centered moving average of the error values, handling NaN.

        Args:
            array: Input array (may contain NaN values)
            window: Size of the moving average window (centered on each point)

        Returns:
            Moving average array of same length as input, with NaN where
            insufficient valid data exists for averaging.

        Note:
            - Uses pure NumPy implementation to avoid heavy dependencies
            - NaN values are excluded from the average calculation
            - Uses cumulative sum approach for O(n) performance
            - Window is centered: for window=5, uses [i-2, i-1, i, i+1, i+2]
            - If window > len(array), uses entire array for all positions
            - Empty arrays return empty results

        """
        valid_mask = ~np.isnan(array)
        arr_filled = np.where(valid_mask, 0, array)

        window_sums = np.convolve(arr_filled, np.ones(window), mode="same")
        window_counts = np.convolve(
            valid_mask.astype(int), np.ones(window), mode="same"
        )

        result = np.full(len(array), np.nan)
        valid_avg = window_counts > 0
        result[valid_avg] = window_sums[valid_avg] / window_counts[valid_avg]

        return result

    """
    ======== Metadata Settings ========
    """

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
                # Convert QDate to Python date for storage
                if k == "test_date" and not isinstance(v, date):
                    v.toPython()
                setattr(self._meta_data, k, v)

    def get_metadata(self) -> Metadata:
        """Return a copy of the current metadata."""
        return Metadata(**asdict(self._meta_data))

    """
    ======== Get States ========
    """

    def get_graph_options_state(self) -> BurninGraphOptions:
        """Return a copy of the current display settings state."""
        return BurninGraphOptions(
            print_stats=self._print_stats_option,
            separate_errors=self._separate_errors_option,
            moving_average=self._moving_average_option,
        )
