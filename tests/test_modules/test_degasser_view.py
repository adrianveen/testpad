"""Tests for Degasser View components."""

import sys
from typing import cast

import pytest
from PySide6.QtWidgets import QApplication

from testpad.ui.tabs.degasser_tab.config import HEADER_ROW_INDEX
from testpad.ui.tabs.degasser_tab.view import ColumnMajorTableWidget


# Check if QApplication already exists to avoid
# "A QApplication instance already exists" error
@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Fixture to provide a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return cast("QApplication", app)


class TestColumnMajorTableWidget:
    """Tests for the custom table widget navigation logic."""

    @pytest.fixture
    def table(self) -> ColumnMajorTableWidget:
        """Create a 7x5 table for testing."""
        return ColumnMajorTableWidget(7, 5)

    def test_navigation_forward_simple(self, table: ColumnMajorTableWidget) -> None:
        """Tab/Enter should move down within a column."""
        # Start at (0,0)
        # HEADER_ROW_INDEX is usually 3.
        # (0,0) -> (1,0)
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            0, 0, forward=True
        )
        assert (next_row, next_col) == (1, 0)

    def test_navigation_skip_header_forward(
        self, table: ColumnMajorTableWidget
    ) -> None:
        """Navigation should skip the header row moving forward."""
        # Assuming HEADER_ROW_INDEX is 3
        # Row 2 -> Row 4 (Skip 3)
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            HEADER_ROW_INDEX - 1, 0, forward=True
        )
        assert next_row == HEADER_ROW_INDEX + 1
        assert next_col == 0

    def test_navigation_column_wrap_forward(
        self, table: ColumnMajorTableWidget
    ) -> None:
        """At bottom of column, wrap to top of next column."""
        rows = table.rowCount()
        # Bottom of col 0 -> Top of col 1
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            rows - 1, 0, forward=True
        )
        assert next_row == 0
        assert next_col == 1

    def test_navigation_table_wrap_forward(self, table: ColumnMajorTableWidget) -> None:
        """At bottom-right, wrap to top-left."""
        rows = table.rowCount()
        cols = table.columnCount()
        # Bottom-right -> Top-left
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            rows - 1, cols - 1, forward=True
        )
        assert (next_row, next_col) == (0, 0)

    def test_navigation_backward_simple(self, table: ColumnMajorTableWidget) -> None:
        """Shift+Tab should move up within a column."""
        # (1,0) -> (0,0)
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            1, 0, forward=False
        )
        assert (next_row, next_col) == (0, 0)

    def test_navigation_skip_header_backward(
        self, table: ColumnMajorTableWidget
    ) -> None:
        """Navigation should skip the header row moving backward."""
        # Row 4 -> Row 2 (Skip 3)
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            HEADER_ROW_INDEX + 1, 0, forward=False
        )
        assert next_row == HEADER_ROW_INDEX - 1
        assert next_col == 0

    def test_navigation_column_wrap_backward(
        self, table: ColumnMajorTableWidget
    ) -> None:
        """At top of column, wrap to bottom of previous column."""
        rows = table.rowCount()
        # Top of col 1 -> Bottom of col 0
        next_row, next_col = table._get_next_cell(  # noqa: SLF001
            0, 1, forward=False
        )
        assert next_row == rows - 1
        assert next_col == 0
