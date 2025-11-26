"""Delegates for the Degasser Tab."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QStyledItemDelegate, QWidget

if TYPE_CHECKING:
    from PySide6.QtCore import (
        QAbstractItemModel,
        QModelIndex,
        QPersistentModelIndex,
    )
    from PySide6.QtWidgets import QStyleOptionViewItem

from testpad.ui.tabs.degasser_tab.config import (
    DO_PHYSICAL_BOUNDS,
    DS50_DECIMAL_PRECISION,
    DS50_PHYSICAL_BOUNDS,
    MEASURED_COL_INDEX,
    ROW_SPEC_MAPPING,
)
from testpad.ui.tabs.degasser_tab.widgets.table_widgets import (
    ColumnMajorNavigationMixin,
)
from testpad.utils.lineedit_validators import FixupDoubleValidator, ValidatedLineEdit


class MeasuredValueDelegate(ColumnMajorNavigationMixin, QStyledItemDelegate):
    """Delegate that appends units for measured values in the test table."""

    def __init__(
        self,
        units_by_row: dict[int, str],
        specs_by_row: dict[int, tuple[float | None, float | None]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._units_by_row = units_by_row
        self._specs_by_row = specs_by_row

    def initStyleOption(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Append units to measured values for display.

        Args:
            option: Style options to modify
            index: Model index of the cell being styled

        """
        super().initStyleOption(option, index)

        if index.column() != MEASURED_COL_INDEX:
            return

        unit = self._units_by_row.get(index.row())
        if not unit:
            return

        # Cast to Any to access text attribute (exists at runtime but not in stubs)
        opt = cast("Any", option)
        text = opt.text
        if text and not text.endswith(unit):
            opt.text = f"{text} {unit}"

    def createEditor(
        self,
        parent: QWidget | None,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create editor widget with row-specific validation.

        Qt calls this method when a cell begins editing. Creates a
        ValidatedLineEdit with FixupDoubleValidator configured for the
        row's physical bounds (not spec ranges) and decimal precision.

        Physical bounds reject non-physical values (e.g., positive vacuum pressure,
        negative time). Spec ranges are used by the presenter to determine pass/fail.

        Args:
            parent: Parent widget for the editor (the table viewport)
            option: Style options for the editor (unused but required by Qt)
            index: Model index of the cell being edited

        Returns:
            ValidatedLineEdit widget with event filter installed for
            column-major navigation

        """
        _ = option  # Unused
        # Get the row from the index
        row = index.row()

        # Look up the spec key for this row
        spec_key = ROW_SPEC_MAPPING[row]

        # Get the decimal precision from config
        precision = DS50_DECIMAL_PRECISION.get(spec_key, 2)

        # Get physical bounds from config (not spec ranges)
        physical_bounds = DS50_PHYSICAL_BOUNDS.get(spec_key, (0.0, 10000.0))
        min_bound, max_bound = physical_bounds

        # Create validated line edit with fixup double validator
        editor = ValidatedLineEdit(parent)
        validator = FixupDoubleValidator(min_bound, max_bound, precision, editor)
        editor.setValidator(validator)
        editor.setPlaceholderText("Enter number")

        # Install event filter for column-major navigation
        # (This is handled by the mixin, but we do it explicitly here since
        # we're creating a custom editor rather than calling super().createEditor())
        editor.installEventFilter(self)

        return editor

    def setModelData(
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Set model data from editor, rejecting invalid values.

        Args:
            editor: The editor widget (ValidatedLineEdit)
            model: The model to update
            index: Model index of the cell being edited

        """
        # Only commit if input is acceptable according to validator
        if isinstance(editor, ValidatedLineEdit) and editor.hasAcceptableInput():
            # Valid input - commit to model
            super().setModelData(editor, model, index)
        else:
            # Invalid input - clear the cell
            model.setData(index, "", Qt.ItemDataRole.EditRole)


class TimeSeriesValueDelegate(QStyledItemDelegate):
    """Delegate for validating dissolved oxygen measurements in time series table.

    Validates oxygen levels to reasonable physical values (0-30 mg/L) with
    2 decimal places. Applied to row 1 (dissolved oxygen measurements).
    """

    def createEditor(
        self,
        parent: QWidget | None,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create editor widget with dissolved oxygen validation.

        Args:
            parent: Parent widget for the editor
            _option: Style options (unused but required by Qt)
            _index: Model index of the cell being edited (unused)

        Returns:
            ValidatedLineEdit with validator for dissolved oxygen
            (physical bounds from config, 2 decimals)

        """
        _ = _option  # Unused
        _ = _index  # Unused
        # Create validated line edit for dissolved oxygen measurements
        editor = ValidatedLineEdit(parent)
        # Get physical bounds from config (shared with test table DO measurements)
        min_bound, max_bound = DO_PHYSICAL_BOUNDS
        # Use QDoubleValidator (not FixupDoubleValidator) to reject invalid values
        # instead of clamping them to the maximum
        validator = QDoubleValidator(min_bound, max_bound, 2, editor)
        editor.setValidator(validator)
        editor.setPlaceholderText("0.00")

        return editor

    def setModelData(
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Set model data from editor, clearing cell if value is invalid.

        Args:
            editor: The editor widget (ValidatedLineEdit)
            model: The model to update
            index: Model index of the cell being edited

        """
        # Check if editor has acceptable input
        if isinstance(editor, ValidatedLineEdit) and editor.hasAcceptableInput():
            # Valid input - commit to model
            super().setModelData(editor, model, index)
        else:
            # Invalid input - clear the cell
            model.setData(index, "", Qt.ItemDataRole.EditRole)
