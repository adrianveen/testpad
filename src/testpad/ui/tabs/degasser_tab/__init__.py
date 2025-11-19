"""Degasser tab package.

This subpackage wires together the model / presenter / view trio exposed to the
tab registry. Importing the package re-exports the QWidget subclass so the
lazy-loader can resolve it without knowing the internal layout.
"""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from testpad.config import plotting
from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH

from .model import DegasserModel

# Defer Qt imports to avoid issues during testing
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from .view import DegasserTab


def create_degasser_tab(parent: QWidget | None = None) -> DegasserTab:
    """Create factory function initializing Degasser Tab."""
    # Import here to avoid Qt dependencies during module import (for testing)
    from .presenter import DegasserPresenter  # noqa: PLC0415
    from .view import DegasserTab  # noqa: PLC0415

    # Debug: Check if resources are accessible
    try:
        logo_exists = Path(DEFAULT_FUS_LOGO_PATH).exists()
        # TODO: Convert to logging
        if not logo_exists:
            print("[degasser_tab]   ⚠️  Logo file not found at expected path")
    except OSError as e:
        print(f"[degasser_tab]   ⚠️  Could not check logo: {e}")

    try:
        model = DegasserModel()
        view = DegasserTab(parent, model=model, presenter=None)
        presenter = DegasserPresenter(model, view)

        view.presenter = presenter
        presenter.initialize()

    except Exception as e:
        print(f"[degasser_tab] ❌ ERROR creating tab: {e}")

        traceback.print_exc()
        raise

    else:
        return view


__all__ = ["create_degasser_tab", "plotting"]
