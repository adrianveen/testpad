"""
Matplotlib runtime hook to speed up first use by pointing MPLCONFIGDIR
to a writable per-user cache, optionally seeded from a pre-baked cache
shipped under resources/mpl_cache.

Behavior:
- If resources/mpl_cache contains fontlist-*.json, copy them to a
  per-user cache folder (e.g., %LOCALAPPDATA%/testpad_mpl_cache or temp).
- Set MPLCONFIGDIR to that per-user cache folder before Matplotlib loads.
- Force the Qt backend to avoid auto-detection work.
"""
from __future__ import annotations

import os
import sys
import shutil
import glob
import tempfile


def _app_base_dir() -> str:
    # For PyInstaller: _MEIPASS points to the bundle root (onefile temp or onedir)
    base = getattr(sys, "_MEIPASS", None)
    if base and os.path.isdir(base):
        return base
    # Fallback to directory containing the executable (onedir) or script
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _user_cache_dir(app_name: str = 'testpad_mpl_cache') -> str:
    # Prefer LOCALAPPDATA on Windows; else use user home or temp
    base = os.getenv('LOCALAPPDATA') or os.path.expanduser('~') or tempfile.gettempdir()
    path = os.path.join(base, app_name)
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        # Last resort: temp dir
        path = os.path.join(tempfile.gettempdir(), app_name)
        os.makedirs(path, exist_ok=True)
    return path


def _seed_mpl_cache(src_dir: str, dst_dir: str) -> None:
    if not os.path.isdir(src_dir):
        return
    # Copy over fontlist-*.json files if they don't exist in destination
    for src in glob.glob(os.path.join(src_dir, 'fontlist-*.json')):
        name = os.path.basename(src)
        dst = os.path.join(dst_dir, name)
        if not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass


def _configure_matplotlib():
    # Set fixed backend to avoid probing
    os.environ.setdefault('MPLBACKEND', 'qtagg')
    os.environ.setdefault('QT_API', 'PySide6')

    # Prepare config dir
    base = _app_base_dir()
    shipped_cache = os.path.join(base, 'resources', 'mpl_cache')
    user_cache = _user_cache_dir()
    _seed_mpl_cache(shipped_cache, user_cache)
    os.environ.setdefault('MPLCONFIGDIR', user_cache)


_configure_matplotlib()

