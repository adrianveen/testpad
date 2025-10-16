"""Degasser tab package.

This subpackage wires together the model / presenter / view trio exposed to the
tab registry. Importing the package re-exports the QWidget subclass so the
lazy-loader can resolve it without knowing the internal layout.
"""

from .view import DegasserTab
from testpad.utils import plot_config

__all__ = ["DegasserTab", "plot_config"]
