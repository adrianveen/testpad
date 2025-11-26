"""Table widgets for the Degasser Tab."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

import PySide6.QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QWidget

if TYPE_CHECKING:
    from PySide6.QtCore import (
        QEvent,
        QModelIndex,
        QObject,
        QPersistentModelIndex,
    )
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QStyleOptionViewItem

from testpad.ui.tabs.degasser_tab.config import (
    HEADER_ROW_INDEX,
    MEASURED_COL_INDEX,
    PASS_FAIL_COL_INDEX,
)


class ColumnMajorTableWidget(QTableWidget):
    """QTableWidget with column-major tab navigation (top→bottom, left→right).

    Overrides default Qt behavior where Tab moves left→right across columns.
    Instead, Tab moves top→bottom within a column, then wraps to the next column.
    """

    def _get_next_cell(
        self, row: int, col: int, *, forward: bool = True
    ) -> tuple[int, int]:
        """Calculate next cell position in column-major order.

        Restricts navigation to PASS_FAIL_COL_INDEX (1) and MEASURED_COL_INDEX (4).
        Column-major order means: fill cells vertically down a column, then move
        to the next column.
        Skips the HEADER_ROW_INDEX.

        Args:
            row: Current row index (0-based)
            col: Current column index (0-based)
            forward: True to move forward (Tab), False to move backward (Shift+Tab)

        Returns:
            Tuple of (new_row, new_col) representing the next cell position

        """
        if forward:
            return self._get_next_cell_forward(row, col)
        return self._get_next_cell_backward(row, col)

    def _get_next_cell_forward(self, row: int, col: int) -> tuple[int, int]:
        """Calculate next cell position moving forward."""
        rows = self.rowCount()
        new_row, new_col = row, col

        # If not in target column, jump to first target column (Pass/Fail)
        if col not in (PASS_FAIL_COL_INDEX, MEASURED_COL_INDEX):
            new_row = 0
            new_col = PASS_FAIL_COL_INDEX
            if new_row == HEADER_ROW_INDEX:
                new_row += 1
            return new_row, new_col

        # Move down
        new_row += 1

        # Skip header
        if new_row == HEADER_ROW_INDEX:
            new_row += 1

        # If at bottom, switch column or wrap
        if new_row >= rows:
            new_row = 0
            new_col = (
                MEASURED_COL_INDEX
                if col == PASS_FAIL_COL_INDEX
                else PASS_FAIL_COL_INDEX
            )

            # Handle header at row 0 case
            if new_row == HEADER_ROW_INDEX:
                new_row += 1

        return new_row, new_col

    def _get_next_cell_backward(self, row: int, col: int) -> tuple[int, int]:
        """Calculate next cell position moving backward."""
        rows = self.rowCount()
        new_row, new_col = row, col

        # If not in target column, jump to last target column (Measured)
        if col not in (PASS_FAIL_COL_INDEX, MEASURED_COL_INDEX):
            new_row = rows - 1
            new_col = MEASURED_COL_INDEX
            if new_row == HEADER_ROW_INDEX:
                new_row -= 1
            return new_row, new_col

        # Move up
        new_row -= 1

        # Skip header
        if new_row == HEADER_ROW_INDEX:
            new_row -= 1

        # If at top (passed 0), switch column or wrap
        if new_row < 0:
            new_row = rows - 1
            new_col = (
                PASS_FAIL_COL_INDEX if col == MEASURED_COL_INDEX else MEASURED_COL_INDEX
            )

            # Handle header at last row case
            if new_row == HEADER_ROW_INDEX:
                new_row -= 1

        return new_row, new_col

    @override
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Override Qt's default key handling to implement column-major navigation.

        By default, QTableWidget uses row-major Tab navigation (left→right).
        This override intercepts Tab/Enter/Backtab keys and implements column-major
        navigation instead. Other keys are passed to Qt's default handler.
        """
        key = event.key()

        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Tab and Enter both move forward in column-major order
            event.accept()  # Prevent Qt's default row-major navigation
            new_row, new_col = self._get_next_cell(
                self.currentRow(),
                self.currentColumn(),
                forward=True,
            )
            self.setCurrentCell(new_row, new_col)
        elif key == Qt.Key.Key_Backtab:
            # Shift+Tab moves backward in column-major order
            event.accept()  # Prevent Qt's default behavior
            new_row, new_col = self._get_next_cell(
                self.currentRow(),
                self.currentColumn(),
                forward=False,
            )
            self.setCurrentCell(new_row, new_col)
        else:
            # For all other keys (arrows, letters, etc.), use Qt's default handling
            super().keyPressEvent(event)


class ColumnMajorNavigationMixin:
    """Mixin for item delegates to support column-major navigation during cell editing.

    This mixin installs an event filter on editor widgets to intercept Tab/Enter
    keys and forward them to the table's navigation logic. Any delegate class that
    inherits from this mixin will automatically support column-major navigation during
    editing.

    Usage: class MyDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate): ...
    Note: Mixin must come BEFORE QStyledItemDelegate in the inheritance list
    for proper MRO.

    """

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Intercept key events from editor widgets and redirect navigation keys.

        When we detect Tab/Enter, we bypass the editor and send the event directly
        to the table's keyPressEvent for custom handling.

        Args:
            watched: The object being watched (the editor widget)
            event: The QEvent being processed

        Returns:
            True if event was handled (prevents further processing)
            False to allow normal event propagation

        """
        if event.type() == PySide6.QtCore.QEvent.Type.KeyPress:
            # Cast to QKeyEvent to access key()
            key_event: QKeyEvent = event  # type: ignore[assignment]
            if key_event.key() in (
                Qt.Key.Key_Tab,
                Qt.Key.Key_Backtab,
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            ):
                # This is a navigation key - don't let the editor process it
                table = self.parent()  # type: ignore[attr-defined]  # Delegate's parent is the table widget
                if isinstance(table, ColumnMajorTableWidget):
                    # Forward the event to the table's custom navigation handler
                    table.keyPressEvent(key_event)
                    return True  # Event handled, stop propagation
        # Not a navigation key, or not our custom table - use default behavior
        return super().eventFilter(watched, event)  # type: ignore[misc]

    def createEditor(
        self,
        parent: QWidget | None,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create editor widget and install this delegate as an event filter.

        Qt calls this method when a cell begins editing.

        Args:
            parent: Parent widget for the editor (the table viewport)
            option: Style options for the editor
            index: Model index of the cell being edited

        Returns:
            The editor widget with event filter installed

        """
        editor = super().createEditor(parent, option, index)  # type: ignore[misc]
        if editor:
            # Install this delegate as an event filter on the editor
            # Now our eventFilter() method will intercept the editor's key events
            editor.installEventFilter(self)  # type: ignore[attr-defined]
        return editor
