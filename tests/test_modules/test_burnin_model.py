"""Tests for the burnin core model.

This test module covers:
- BurninFileInfo filename parsing
- Graph options and state snapshots
- Burnin file and output path management
- Metadata defaults and updates
- HDF5 data loading and error handling
- Moving average calculation with NaN handling
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import h5py
import numpy as np
import pytest

from testpad.config.defaults import DEFAULT_EXPORT_DIR
from testpad.core.burnin.model import BurninFileInfo, BurninModel

if TYPE_CHECKING:
    from pathlib import Path


def _ref_moving_average(array: np.ndarray, window: int) -> np.ndarray:
    """Provide reference implementation for centered moving average.

    Mirrors the intended semantics of BurninModel.calculate_moving_average:
    - Centered window with truncation at array boundaries
    - NaN values ignored in the average
    - Positions with no valid (non-NaN) samples remain NaN
    """
    n = len(array)
    result = np.full(n, np.nan)
    half = window // 2

    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half + 1)
        window_values = array[start:end]
        valid = window_values[~np.isnan(window_values)]
        if valid.size > 0:
            result[i] = float(valid.mean())

    return result


# ====================================================================================
# FILE INFO PARSING TESTS
# ====================================================================================
class TestBurninFileInfoParsing:
    """Tests for BurninFileInfo filename parsing."""

    def test_axis_and_test_number_from_path(self, tmp_path: Path) -> None:
        """Axis A and test number should be parsed from filename."""
        path = tmp_path / "rk300_axis_A_error_3.h5"

        info = BurninFileInfo.from_path(path)

        assert info.file_path == path
        assert info.axis_name == "A"
        assert info.test_number == 3

    def test_axis_b_from_path(self, tmp_path: Path) -> None:
        """Axis B should be parsed from filename."""
        path = tmp_path / "rk300_axis_B_error_10.h5"

        info = BurninFileInfo.from_path(path)

        assert info.axis_name == "B"
        assert info.test_number == 10

    def test_unknown_axis_and_missing_test_number(self, tmp_path: Path) -> None:
        """Missing axis marker returns None; missing test number returns -1."""
        path = tmp_path / "rk300_burnin_data.h5"

        info = BurninFileInfo.from_path(path)

        assert info.axis_name is None
        assert info.test_number == -1


# ====================================================================================
# GRAPH OPTION / STATE TESTS
# ====================================================================================
class TestGraphOptionsState:
    """Tests for graph options toggling and state snapshot."""

    def test_default_graph_options_are_false(self) -> None:
        """All graph options should default to False."""
        model = BurninModel()

        assert model.get_print_stats_option() is False
        assert model.get_separate_errors_option() is False
        assert model.get_moving_average_option() is False

        options = model.get_graph_options_state()
        assert options.print_stats is False
        assert options.separate_errors is False
        assert options.moving_average is False

    def test_toggle_graph_options_updates_state(self) -> None:
        """Toggling graph options should be reflected in state dataclass."""
        model = BurninModel()

        model.set_print_stats_option()
        model.set_separate_errors_option()
        model.set_moving_average_option()

        assert model.get_print_stats_option() is True
        assert model.get_separate_errors_option() is True
        assert model.get_moving_average_option() is True

        options = model.get_graph_options_state()
        assert options.print_stats is True
        assert options.separate_errors is True
        assert options.moving_average is True


# ====================================================================================
# BURNIN FILE / OUTPUT PATH TESTS
# ====================================================================================
class TestBurninFileManagement:
    """Tests for setting and clearing burnin files on the model."""

    def test_set_and_clear_burnin_files(self, tmp_path: Path) -> None:
        """Model should store burnin files and report presence correctly."""
        model = BurninModel()
        file_a = BurninFileInfo.from_path(tmp_path / "rk300_axis_A_error_1.h5")
        file_b = BurninFileInfo.from_path(tmp_path / "rk300_axis_B_error_2.h5")

        model.set_burnin_files([file_a, file_b])
        files = model.get_burnin_file()

        assert files == [file_a, file_b]
        assert model.has_burnin_file() is True

        model.clear_burnin_file()
        assert model.get_burnin_file() == []
        assert model.has_burnin_file() is False


class TestOutputPathManagement:
    """Tests for output folder and file management."""

    def test_default_output_folder_is_export_dir(self) -> None:
        """Output folder should default to DEFAULT_EXPORT_DIR."""
        model = BurninModel()

        assert model.get_output_folder() == DEFAULT_EXPORT_DIR

    def test_set_and_clear_output_folder(self, tmp_path: Path) -> None:
        """Setting and clearing the output folder should update model state."""
        model = BurninModel()
        new_dir = tmp_path / "exports"

        model.set_output_folder(new_dir)
        assert model.get_output_folder() == new_dir

        model.clear_output_folder()
        assert model.get_output_folder() is None

    def test_set_output_folder_requires_absolute_path(self) -> None:
        """Relative output folder paths should be rejected."""
        model = BurninModel()

        with pytest.raises(ValueError, match="must be absolute"):
            model.set_output_folder("relative/path")

    def test_set_and_clear_output_file(self, tmp_path: Path) -> None:
        """Model should store and clear output file path."""
        model = BurninModel()
        output_file = tmp_path / "burnin_report.pdf"

        model.set_output_file(output_file)
        assert model.get_output_file() == output_file

        model.clear_output_file()
        assert model.get_output_file() is None


# ====================================================================================
# METADATA TESTS
# ====================================================================================
class TestMetadataHandling:
    """Tests for burnin metadata handling."""

    def test_metadata_has_default_date(self) -> None:
        """Metadata should initialize with a non-null date."""
        model = BurninModel()

        metadata = model.get_metadata()
        assert metadata.test_date is not None
        assert isinstance(metadata.test_date, date)

    def test_update_metadata_fields(self) -> None:
        """Updating metadata fields should be reflected in the model."""
        model = BurninModel()
        new_date = date(2024, 1, 1)

        model.update_metadata(
            {
                "tested_by": "Alice",
                "test_date": new_date,
                "rk300_serial": "RK300-1234",
                "test_name": "Burn-in Qualification",
            }
        )

        metadata = model.get_metadata()
        assert metadata.tested_by == "Alice"
        assert metadata.test_date == new_date
        assert metadata.rk300_serial == "RK300-1234"
        assert metadata.test_name == "Burn-in Qualification"

    def test_update_metadata_ignores_unknown_keys(self) -> None:
        """Unknown metadata keys should be ignored without error."""
        model = BurninModel()

        model.update_metadata({"unknown_field": "value"})

        metadata = model.get_metadata()
        assert "unknown_field" not in metadata.__dict__


# ====================================================================================
# HDF5 DATA LOAD TESTS
# ====================================================================================
class TestLoadBurninData:
    """Tests for HDF5 burnin data loading."""

    def test_load_burnin_data_splits_positive_and_negative_errors(
        self,
        tmp_path: Path,
    ) -> None:
        """Load data and verify positive/negative error separation and metadata."""
        file_path = tmp_path / "rk300_axis_A_error_3.h5"
        time = np.array([0.0, 1.0, 2.0, 3.0], dtype=float)
        error = np.array([-1.0, 0.0, 2.0, -3.0], dtype=float)

        with h5py.File(file_path, "w") as f:
            f.create_dataset("Time (s)", data=time)
            f.create_dataset("Error (counts)", data=error)

        file_info = BurninFileInfo.from_path(file_path)
        model = BurninModel()

        data = model.load_burnin_data(file_info)

        # Basic arrays
        assert np.array_equal(data.time, time)
        assert np.array_equal(data.error, error)
        assert data.axis_name == "A"
        assert data.test_number == 3

        # Positive / negative separation
        assert np.isnan(data.positive_errors[0])
        assert np.isnan(data.positive_errors[1])
        assert data.positive_errors[2] == pytest.approx(2.0)
        assert np.isnan(data.positive_errors[3])

        assert data.negative_errors[0] == pytest.approx(-1.0)
        assert np.isnan(data.negative_errors[1])
        assert np.isnan(data.negative_errors[2])
        assert data.negative_errors[3] == pytest.approx(-3.0)

    def test_load_burnin_data_missing_error_dataset_raises_keyerror(
        self,
        tmp_path: Path,
    ) -> None:
        """Missing error dataset should raise an error (negative path)."""
        file_path = tmp_path / "rk300_axis_A_error_1.h5"
        time = np.array([0.0, 1.0], dtype=float)

        with h5py.File(file_path, "w") as f:
            f.create_dataset("Time (s)", data=time)
            # Intentionally omit "Error (counts)"

        file_info = BurninFileInfo.from_path(file_path)
        model = BurninModel()

        with pytest.raises(KeyError):
            model.load_burnin_data(file_info)


# ====================================================================================
# MOVING AVERAGE TESTS
# ====================================================================================
class TestMovingAverage:
    """Tests for moving average calculation."""

    def test_moving_average_constant_array(self) -> None:
        """Constant arrays should remain constant after averaging."""
        model = BurninModel()
        array = np.ones(10, dtype=float)

        result = model.calculate_moving_average(array, window=3)

        assert result.shape == array.shape
        assert np.allclose(result, np.ones_like(array))

    def test_moving_average_handles_nans(self) -> None:
        """NaN values should be ignored in the average."""
        model = BurninModel()
        array = np.array([1.0, np.nan, 3.0, np.nan, 5.0], dtype=float)

        result = model.calculate_moving_average(array, window=3)
        expected = _ref_moving_average(array, window=3)

        assert result.shape == expected.shape
        assert np.allclose(result, expected, equal_nan=True)

    def test_moving_average_all_nan_returns_all_nan(self) -> None:
        """All-NaN arrays should produce all-NaN averages."""
        model = BurninModel()
        array = np.array([np.nan, np.nan, np.nan], dtype=float)

        result = model.calculate_moving_average(array, window=3)

        assert np.all(np.isnan(result))
