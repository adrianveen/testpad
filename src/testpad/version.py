"""Version information for testpad application.

Reads version from VERSION file in repository root.
Supports development, PyInstaller bundled, and CI/CD environments.
"""

import os
import sys
from pathlib import Path

__version__ = "1.11.0-dev"  # Fallback - should be overwritten below

if os.environ.get("BUILD_VERSION"):
    __version__ = os.environ["BUILD_VERSION"]
else:
    try:
        with Path.open(Path(__file__).parent.parent.parent / "VERSION") as f:
            __version__ = f.read().strip()

    except (FileNotFoundError, OSError, PermissionError):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            try:
                with Path.open(Path(meipass) / "VERSION") as f:
                    __version__ = f.read().strip()
            except (FileNotFoundError, OSError, PermissionError):
                pass
