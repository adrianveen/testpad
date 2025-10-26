"""Degasser tab package.

This subpackage wires together the model / presenter / view trio exposed to the
tab registry. Importing the package re-exports the QWidget subclass so the
lazy-loader can resolve it without knowing the internal layout.
"""

from .view import DegasserTab
from .model import DegasserModel
from .presenter import DegasserPresenter
from testpad.config import plotting

def create_degasser_tab(parent=None) -> DegasserTab:
    """Factory function to create a fully initialized Degasser tab."""
    print("[degasser_tab] Creating degasser tab instance...")

    # Debug: Check if resources are accessible
    try:
        from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH
        import os
        logo_exists = os.path.exists(DEFAULT_FUS_LOGO_PATH)
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

        view._presenter = presenter
        print("[degasser_tab]   ✅ Presenter assigned to view")

        presenter.initialize()
        print("[degasser_tab]   ✅ Presenter initialized")

        print("[degasser_tab] Degasser tab created successfully ✅")
        return view
    except Exception as e:
        print(f"[degasser_tab] ❌ ERROR creating tab: {e}")
        import traceback
        traceback.print_exc()
        raise

__all__ = ["create_degasser_tab", "plotting"]
