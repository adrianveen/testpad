"""Resource path resolution utilities for FUS Instruments Testpad.

Provides functions to locate resources (images, stylesheets, etc.) in both
development and PyInstaller frozen builds.
"""

from __future__ import annotations

import sys
from pathlib import Path


def resolve_resource_path(relative: str) -> str:
    """Resolve a resource path for dev and PyInstaller builds.

    Looks for resources in the following order:
    1. Package location (src/testpad/resources/)
    2. PyInstaller's _MEIPASS temporary directory
    3. Fallback to repo-root layout (development)

    Args:
        relative: Relative path from resources/ directory (e.g., "styles/buttons.qss")

    Returns:
        str: Absolute path to the resource file

    Example:
        >>> logo_path = resolve_resource_path("images/logo.png")
        >>> stylesheet_path = resolve_resource_path("styles/buttons.qss")

    """
    # Try package location first (installed or development)
    base_dir = Path(__file__).parent.parent  # src/testpad
    pkg_path = base_dir / "resources" / relative

    if pkg_path.exists():
        return str(pkg_path)

    # Try PyInstaller's temporary folder
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        meipass_path = Path(meipass) / "resources" / relative
        if meipass_path.exists():
            return str(meipass_path)

    # Fallback to repo-root layout during development
    fallback = Path.cwd() / "src" / "testpad" / "resources" / relative
    return str(fallback)


def load_stylesheet(stylesheet_name: str) -> str:
    """Load a Qt StyleSheet (.qss) file from resources/styles.

    Args:
        stylesheet_name: Name of the stylesheet file (e.g., "buttons.qss")

    Returns:
        str: The stylesheet content as a string, ready for setStyleSheet()

    Raises:
        FileNotFoundError: If the stylesheet file doesn't exist
        OSError: If the file cannot be read

    Example:
        >>> from testpad.utils.resources import load_stylesheet
        >>> button_styles = load_stylesheet("buttons.qss")
        >>> app.setStyleSheet(button_styles)

    """
    stylesheet_path = resolve_resource_path(f"styles/{stylesheet_name}")

    if not Path(stylesheet_path).exists():
        msg = f"Stylesheet not found: {stylesheet_path}"
        raise FileNotFoundError(msg)

    with Path(stylesheet_path).open("r", encoding="utf-8") as f:
        return f.read()


def load_multiple_stylesheets(stylesheet_names: list[str]) -> str:
    """Load and concatenate multiple Qt StyleSheet files.

    Useful for combining base styles with component-specific styles.

    Args:
        stylesheet_names: List of stylesheet file names to load and merge

    Returns:
        str: Combined stylesheet content

    Example:
        >>> combined = load_multiple_stylesheets(["base.qss", "buttons.qss"])
        >>> app.setStyleSheet(combined)

    """
    return "\n\n".join([load_stylesheet(name) for name in stylesheet_names])
