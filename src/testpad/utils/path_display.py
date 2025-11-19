# testpad/src/testpad/utils/path_display.py
"""Path display utilities for user-facing messages."""

from __future__ import annotations

from pathlib import Path


def truncate_to_testpad(path: str | Path) -> str:
    r"""Truncate path to format: C:\\...\\testpad\\full\\remaining\\tail.

    Shows drive letter, ellipsis, then everything from 'testpad' onward.
    Case-insensitive search for 'testpad'.

    Args:
        path: the file path to truncate

    Returns:
        str: Truncated path like "C:\\...\\testpad\\ui\\splash.py"
             If 'testpad' not found, returns original full path

    Examples:
        >>> truncate_to_testpad(
        ...     "C:\\Users\\UserName\\Documents\\repos\\summer_2024\\testpad\\src\\
        ...         testpad\\ui\\tabs\\degasser_tab\\view.py"
        ... )
        'C:\\...\\testpad\\ui\\tabs\\degasser_tab\\view.py'

        >>> truncate_to_testpad(
        ...     "C:\\Program Files\\FUS Instruments\\Testpad\\core\\config.py"
        ... )
        'C:\\...\\Testpad\\core\\config.py'

        >>> truncate_to_testpad("/home/user/projects/testpad/ui/splash.py")
        '/...\\testpad\\ui\\splash.py'

    """
    path_obj = Path(path)
    parts = path_obj.parts

    # Find "testpad" in the path (case-insensitive)
    anchor_index = None
    for i, part in enumerate(parts):
        if part.lower() == "testpad":
            anchor_index = i
            break

    # If "testpad" not found, return original path
    if anchor_index is None:
        return str(path_obj)

    # Build: drive + ... + testpad + remaining tail
    drive_or_root = parts[0]  # 'C:\\' or '/'
    tail_parts = parts[anchor_index:]  # Evertying from 'testpad' onward

    truncated = Path(drive_or_root) / "..." / Path(*tail_parts)

    return str(truncated)
