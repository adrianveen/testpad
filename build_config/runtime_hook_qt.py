"""Qt runtime hook to restrict plugin search paths to the packaged minimal set.

- Sets QT_QPA_PLATFORM_PLUGIN_PATH to our bundled platforms dir
- Sets QT_PLUGIN_PATH to our bundled qt_plugins root so imageformats are found

This reduces Qt scanning of system/plugin directories during startup.
"""

import os
import sys
from pathlib import Path


def _set_qt_plugin_env() -> None:
    base = getattr(sys, "_MEIPASS", None) or Path(sys.executable).parent
    qt_plugins = str(Path(base) / "qt_plugins")
    platforms = str(Path(qt_plugins) / "platforms")
    # Point directly to our minimal plugin bundle, only if present
    if Path(platforms).is_dir():
        if not os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platforms
        if not os.environ.get("QT_PLUGIN_PATH") and Path(qt_plugins).is_dir():
            os.environ["QT_PLUGIN_PATH"] = qt_plugins


_set_qt_plugin_env()
