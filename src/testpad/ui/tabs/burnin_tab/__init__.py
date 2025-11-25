import traceback
from pathlib import Path
from typing import TYPE_CHECKING

from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH
from testpad.core.burnin.burnin_presenter import BurninPresenter
from testpad.core.burnin.model import BurninModel
from testpad.ui.tabs.burnin_tab import BurninTab

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


def create_burnin_tab(parent: "QWidget | None" = None) -> BurninTab:
    """Create and initialize burnin tab with factory method."""
    try:
        logo_exists = Path(DEFAULT_FUS_LOGO_PATH).exists()

        if not logo_exists:
            print("[Burnin Tab][WARN] Logo file not found at expected path.")

    except OSError as e:
        print(f"[Burnin Tab][ERROR] Failed to check for logo file: {e}")

    try:
        model = BurninModel()

        view = BurninTab(parent)

        presenter = BurninPresenter(model, view=view)

        view.presenter = presenter

        presenter.initialize()

    except Exception as e:
        print(f"[Burnin Tab][ERROR] Failed to create Burnin Tab: {e}")

        traceback.print_exc()
        raise

    else:
        return view


__all__ = ["create_burnin_tab"]
