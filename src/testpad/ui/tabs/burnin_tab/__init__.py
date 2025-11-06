from pathlib import Path

from testpad.core.burnin.burnin_presenter import BurninPresenter
from testpad.core.burnin.model import BurninModel
from testpad.ui.tabs.burnin_widget import BurninTab


def create_burnin_tab(parent=None) -> BurninTab:
    """Create and initialize burnin tab with factory method."""
    try:
        from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH

        logo_exists = Path(DEFAULT_FUS_LOGO_PATH).exists()
        if not logo_exists:
            print("[Burnin Tab][WARN] Logo file not found at expected path.")

    except Exception as e:
        print(f"[Burnin Tab][ERROR] Failed to check for logo file: {e}")

    try:
        model = BurninModel()

        view = BurninTab(parent)

        presenter = BurninPresenter(model, view=view)

        view.presenter = presenter

        presenter.initialize()

        return view

    except Exception as e:
        print(f"[Burnin Tab][ERROR] Failed to create Burnin Tab: {e}")
        import traceback

        traceback.print_exc()
        raise


__all__ = ["create_burnin_tab"]
