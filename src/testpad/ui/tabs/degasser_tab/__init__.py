"""Degasser tab package.

This subpackage wires together the model / presenter / view trio exposed to the
tab registry. Importing the package re-exports the QWidget subclass so the
lazy-loader can resolve it without knowing the internal layout.
"""

import traceback
from pathlib import Path

from testpad.config import plotting
from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH

from .model import DegasserModel
from .presenter import DegasserPresenter
from .view import DegasserTab


def create_degasser_tab(parent=None) -> DegasserTab:
    """Create factory function initializing Degasser Tab."""
    print("[degasser_tab] Creating degasser tab instance...")

    # Debug: Check if resources are accessible
    try:
        logo_exists = Path(DEFAULT_FUS_LOGO_PATH).exists()
        # TODO: Convert to logging
        print(f"[degasser_tab] Logo file check: {DEFAULT_FUS_LOGO_PATH}")
        print(f"[degasser_tab]   Exists: {logo_exists}")
        if not logo_exists:
            print("[degasser_tab]   ⚠️  Logo file not found at expected path")
    except Exception as e:
        print(f"[degasser_tab]   ⚠️  Could not check logo: {e}")

    try:
        model = DegasserModel()
        print("[degasser_tab]   ✅ Model created")

        view = DegasserTab(parent, model=model, presenter=None)
        print("[degasser_tab]   ✅ View created")

        presenter = DegasserPresenter(model, view)
        print("[degasser_tab]   ✅ Presenter created")

        view.presenter = presenter
        print("[degasser_tab]   ✅ Presenter assigned to view")

        presenter.initialize()
        print("[degasser_tab]   ✅ Presenter initialized")

        print("[degasser_tab] Degasser tab created successfully ✅")
        return view
    except Exception as e:
        print(f"[degasser_tab] ❌ ERROR creating tab: {e}")

        traceback.print_exc()
        raise


__all__ = ["create_degasser_tab", "plotting"]
