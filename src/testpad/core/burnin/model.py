"""Model for burnin tab."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import TYPE_CHECKING, final

from PySide6.QtCore import QDate

from testpad.core.burnin.config import DEFAULT_TEST_DATE

if TYPE_CHECKING:
    from datetime import date
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
class BurninSettings:
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
class BurninFileSettings:
    """Settings for the burnin file and output.

    Attributes:
        burnin_file: Path to the burnin file.
        output_folder: Folder to save the output.
        output_file: File to save the output.

    """

    burnin_file_path: list[Path]
    output_folder: Path | None = None
    output_file: Path | None = None


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
        self._burnin_file_paths: list[Path] = []
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

    def set_burnin_file(self, burnin_file_path: list[Path]) -> BurninFileSettings:
        """Set the burnin file path."""
        self._burnin_file_paths = burnin_file_path
        return self.get_files_settings_state()

    def clear_burning_file(self) -> BurninFileSettings:
        """Clear the burnin file path."""
        self._burnin_file_paths = []
        return self.get_files_settings_state()

    def get_burnin_file(self) -> list[Path]:
        """Return the burnin file path."""
        return self._burnin_file_paths

    """
    ======== Output Settings ========
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
                if k == "test_date" and isinstance(v, QDate):
                    v = v.toPython()
                setattr(self._meta_data, k, v)

    def get_metadata(self) -> Metadata:
        """Return a copy of the current metadata."""
        return Metadata(**asdict(self._meta_data))

    def get_files_settings_state(self) -> BurninFileSettings:
        """Return a copy of the current file settings state."""
        return BurninFileSettings(
            burnin_file_path=self._burnin_file_paths,
            output_folder=self._output_folder,
            output_file=self._output_file,
        )
