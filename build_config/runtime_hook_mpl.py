"""Matplotlib runtime hook to speed up first use.

Points MPLCONFIGDIR to a writable per-user cache, optionally seeded from a pre-baked
cache shipped under resources/mpl_cache.

Behavior:
- If resources/mpl_cache contains fontlist-*.json, copy them to a
  per-user cache folder (e.g., %LOCALAPPDATA%/testpad_mpl_cache or temp).
- Set MPLCONFIGDIR to that per-user cache folder before Matplotlib loads.
- Force the Qt backend to avoid auto-detection work.
"""

from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
from pathlib import Path


def _app_base_dir() -> str:
    # For PyInstaller: _MEIPASS points to the bundle root (onefile temp or onedir)
    base = getattr(sys, "_MEIPASS", None)
    if base and Path(base).is_dir():
        return base
    # Fallback to directory containing the executable (onedir) or script
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).parent)
    return str(Path(__file__).resolve().parent)


def _user_cache_dir(app_name: str = "testpad_mpl_cache") -> str:
    # Prefer LOCALAPPDATA on Windows; else use user home or temp
    base = os.getenv("LOCALAPPDATA") or str(Path.home()) or tempfile.gettempdir()
    path = Path(base) / app_name
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Last resort: temp dir
        path = Path(tempfile.gettempdir()) / app_name
        path.mkdir(parents=True, exist_ok=True)
    return str(path)


def _seed_mpl_cache(src_dir: str, dst_dir: str) -> None:
    src_path = Path(src_dir)
    if not src_path.is_dir():
        return
    # Copy over fontlist-*.json files if they don't exist in destination
    dst_path = Path(dst_dir)
    for src in src_path.glob("fontlist-*.json"):
        dst = dst_path / src.name
        if not dst.exists():
            with contextlib.suppress(OSError):
                shutil.copy2(src, dst)


def _configure_matplotlib() -> None:
    # Set fixed backend to avoid probing
    os.environ.setdefault("MPLBACKEND", "qtagg")
    os.environ.setdefault("QT_API", "PySide6")

    # Prepare config dir
    base = _app_base_dir()
    shipped_cache = str(Path(base) / "resources" / "mpl_cache")
    user_cache = _user_cache_dir()
    _seed_mpl_cache(shipped_cache, user_cache)
    os.environ.setdefault("MPLCONFIGDIR", user_cache)


_configure_matplotlib()
