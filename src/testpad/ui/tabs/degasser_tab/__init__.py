"""Degasser tab package.

This subpackage wires together the model / presenter / view trio exposed to the
tab registry. Importing the package re-exports the QWidget subclass so the
lazy-loader can resolve it without knowing the internal layout.
"""

from .view import DegasserTab
from .model import DegasserModel
from .presenter import DegasserPresenter
from testpad.config import plotting

def create_degasser_tab(parent=None):
    model = DegasserModel()
    view = DegasserTab(parent, model=model, presenter=None)
    presenter = DegasserPresenter(model, view)
    view._presenter = presenter
    presenter.initialize()
    return view

__all__ = ["create_degasser_tab", "plotting"]
