"""Runtime debugging hook for PyInstaller builds.

Logs import attempts and helps diagnose missing modules.
"""

import sys
import traceback

# Store original import for debugging
_original_import = __builtins__.__import__


def _debug_import(name, *args, **kwargs) -> object:
    try:
        module = _original_import(name, *args, **kwargs)
        # Uncomment to see ALL imports (very verbose):
        # if name.startswith('testpad'):
        #     print(f"[DEBUG] Successfully imported: {name}")

    except ImportError as e:
        # Log failed imports that might be important
        if name.startswith("testpad") or name in ["fpdf", "matplotlib", "PySide6"]:
            print(f"[DEBUG] [WARN] Failed to import: {name}")
            print(f"[DEBUG]    Error: {e}")
            traceback.print_exc()
        raise
    else:
        return module


# Uncomment to enable import debugging (WARNING: very verbose)
__builtins__.__import__ = _debug_import

# Log environment info at startup
print("=" * 70)
print("PyInstaller Runtime Environment")
print("=" * 70)
print(f"Python version: {sys.version}")
print(f"Frozen: {getattr(sys, 'frozen', False)}")
print(f"Executable: {sys.executable}")
print(f"Base path: {getattr(sys, '_MEIPASS', 'Not frozen')}")
print("=" * 70)

# Check critical imports
print("\n[DEBUG] Checking critical imports...")
critical_imports = [
    "testpad.config",
    "testpad.config.defaults",
    "testpad.ui.tabs.degasser_tab",
    "fpdf",
    "matplotlib",
    "PySide6",
]

for module_name in critical_imports:
    try:
        __import__(module_name)
        print(f"[DEBUG] [OK] {module_name}")
    except ImportError as e:
        print(f"[DEBUG] [FAIL] {module_name}: {e}")

print("=" * 70)
print()
