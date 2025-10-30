from pathlib import Path
# Import here to avoid circular imports during package initialization
from testpad.core.burnin.model import BurninModel
from testpad.core.burnin.burnin_presenter import BurninPresenter
from testpad.ui.tabs.burnin_widget import BurninTab

def create_burnin_tab(parent=None) -> BurninTab:
    """Factory method to create and initialize BurninTab."""

    try:
        from testpad.config.defaults import DEFAULT_FUS_LOGO_PATH

        logo_exists = Path(DEFAULT_FUS_LOGO_PATH).exists()
        print(f"[Burnin Tab] Logo file check: {DEFAULT_FUS_LOGO_PATH}")
        print(f"[Burnin Tab] Logo file exists: {logo_exists}")
        if not logo_exists:
            print("[Burnin Tab][WARN] Logo file not found at expected path.")

    except Exception as e:
        print(f"[Burnin Tab][ERROR] Failed to check for logo file: {e}")

    try:
        model = BurninModel()
        print("[Burnin Tab] Model created.")

        view = BurninTab(parent, model=model, presenter=None)
        print("[Burnin Tab] Tab created.")

        presenter = BurninPresenter(model, view=view)
        print("[Burnin Tab] Presenter created.")

        view._presenter = presenter
        print("[Burnin Tab] Presenter assigned to tab.")

        presenter.initialize()
        print("[Burnin Tab] Presenter initialized.")

        print("[Burnin Tab] Burnin Tab created successfully.")

        return view

    except Exception as e:
        print(f"[Burnin Tab][ERROR] Failed to create Burnin Tab: {e}")
        import traceback

        traceback.print_exc()
        raise


__all__ = ["create_burnin_tab"]
