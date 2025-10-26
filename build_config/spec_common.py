"""
Common utilities for PyInstaller spec files.
Provides shared functions for Qt plugin discovery, version management, and build validation.
"""
import os
import sys
import glob
import datetime
from typing import List, Tuple, Optional


def get_base_dir() -> str:
    """Get the repository root directory."""
    return os.getcwd()


def get_version() -> str:
    """
    Get version from VERSION file or environment variable.

    Priority:
    1. BUILD_VERSION environment variable (set by CI/CD)
    2. VERSION file at repo root
    3. Fallback to version.py (for local development)

    Returns:
        Version string (e.g., "1.10.0")
    """
    # First priority: environment variable (CI/CD builds)
    version = os.environ.get('BUILD_VERSION')
    if version:
        print(f"[spec_common] Using version from BUILD_VERSION env var: {version}")
        return version.strip()

    # Second priority: VERSION file (source of truth)
    base_dir = get_base_dir()
    version_file = os.path.join(base_dir, 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            version = f.read().strip()
        print(f"[spec_common] Using version from VERSION file: {version}")
        return version

    # Fallback: version.py module (local development)
    try:
        sys.path.insert(0, os.path.join(base_dir, 'src'))
        from testpad.version import __version__
        print(f"[spec_common] Using version from version.py (fallback): {__version__}")
        return __version__
    except ImportError:
        raise RuntimeError(
            "Could not determine version. Please ensure VERSION file exists "
            "or BUILD_VERSION environment variable is set."
        )


def validate_build_files(base_dir: str) -> None:
    """
    Validate that all required files exist before building.

    Args:
        base_dir: Repository root directory

    Raises:
        FileNotFoundError: If any required file is missing
    """
    required_files = [
        os.path.join(base_dir, 'src', 'testpad', 'testpad_main.py'),
        os.path.join(base_dir, 'src', 'testpad', 'resources', 'fus_icon_transparent.ico'),
        os.path.join(base_dir, 'build_config', 'qt.conf'),
        os.path.join(base_dir, 'build_config', 'runtime_hook_qt.py'),
        os.path.join(base_dir, 'build_config', 'runtime_hook_mpl.py'),
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        raise FileNotFoundError(
            f"Required build files missing:\n" +
            "\n".join(f"  - {f}" for f in missing_files)
        )

    print("[spec_common] All required build files validated ✓")


def get_build_metadata() -> dict:
    """
    Generate build metadata for inclusion in the build.

    Returns:
        Dictionary with build information
    """
    return {
        'version': get_version(),
        'build_date': datetime.datetime.now().isoformat(),
        'git_commit': os.environ.get('GITHUB_SHA', 'unknown'),
        'build_number': os.environ.get('GITHUB_RUN_NUMBER', 'local'),
        'built_by': 'GitHub Actions' if os.environ.get('GITHUB_ACTIONS') else 'local',
    }


# ============================================================================
# Qt Plugin Discovery
# ============================================================================

def find_qt_plugins_root() -> str:
    """
    Find the Qt plugins root directory.
    Supports Conda, venv, and standard installations on Windows.

    Returns:
        Path to Qt plugins directory
    """
    try:
        from PySide6.QtCore import QLibraryInfo
        p = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
        if p and os.path.exists(p):
            print(f"[spec_common] Found Qt plugins via QLibraryInfo: {p}")
            return p
    except Exception as e:
        print(f"[spec_common] QLibraryInfo failed: {e}")

    from PySide6.QtCore import __file__ as PYSIDE6_QTCORE_FILE

    candidates = [
        os.path.join(sys.prefix, 'Library', 'plugins'),  # Conda on Windows
        os.path.join(sys.prefix, 'plugins'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins'),
        os.path.join(os.path.dirname(os.path.dirname(PYSIDE6_QTCORE_FILE)), 'plugins'),
    ]

    for c in candidates:
        if os.path.exists(os.path.join(c, 'platforms')):
            print(f"[spec_common] Found Qt plugins root: {c}")
            return c

    print(f"[spec_common] Qt plugins not found, using default: {candidates[0]}")
    return candidates[0]


def find_platform_plugin(root: str, name: str = 'qwindows') -> Optional[str]:
    """
    Find a Qt platform plugin DLL.

    Args:
        root: Qt plugins root directory
        name: Plugin name (without .dll extension)

    Returns:
        Full path to plugin DLL, or None if not found
    """
    from PySide6.QtCore import __file__ as PYSIDE6_QTCORE_FILE

    roots = [
        os.path.join(root, 'platforms'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'Qt', 'plugins', 'platforms'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins', 'platforms'),
        os.path.join(sys.prefix, 'Library', 'plugins', 'platforms'),
        os.path.join(sys.prefix, 'plugins', 'platforms'),
    ]

    for r in roots:
        # Try exact match
        cand = os.path.join(r, f'{name}.dll')
        if os.path.exists(cand):
            return cand
        # Try wildcard match
        gl = glob.glob(os.path.join(r, f'{name}*.dll'))
        if gl:
            return gl[0]

    return None


def find_image_plugin(root: str, name: str) -> Optional[str]:
    """
    Find a Qt image format plugin DLL.

    Args:
        root: Qt plugins root directory
        name: Plugin name (without .dll extension)

    Returns:
        Full path to plugin DLL, or None if not found
    """
    from PySide6.QtCore import __file__ as PYSIDE6_QTCORE_FILE

    roots = [
        os.path.join(root, 'imageformats'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'Qt', 'plugins', 'imageformats'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins', 'imageformats'),
        os.path.join(sys.prefix, 'Library', 'plugins', 'imageformats'),
        os.path.join(sys.prefix, 'plugins', 'imageformats'),
    ]

    for r in roots:
        # Try exact match
        cand = os.path.join(r, f'{name}.dll')
        if os.path.exists(cand):
            return cand
        # Try wildcard match
        gl = glob.glob(os.path.join(r, f'{name}*.dll'))
        if gl:
            return gl[0]

    return None


def get_qt_binaries() -> List[Tuple[str, str]]:
    """
    Get all required Qt plugin binaries for bundling.

    Returns:
        List of (source_path, dest_dir) tuples for PyInstaller datas
    """
    qt_plugins_root = find_qt_plugins_root()
    binaries = []

    # Platform plugins (required for Windows)
    qwindows_path = find_platform_plugin(qt_plugins_root, 'qwindows')
    if qwindows_path:
        binaries.append((qwindows_path, 'qt_plugins/platforms'))
        print(f"[spec_common] Added platform plugin: {qwindows_path}")
    else:
        print("[spec_common] WARNING: qwindows.dll not found!")

    # Image format plugins
    image_formats = ['qico', 'qpng', 'qjpeg']
    for fmt in image_formats:
        plugin_path = find_image_plugin(qt_plugins_root, fmt)
        if plugin_path:
            binaries.append((plugin_path, 'qt_plugins/imageformats'))
            print(f"[spec_common] Added image format plugin: {plugin_path}")

    return binaries


# ============================================================================
# Common Data Files
# ============================================================================

def get_common_datas(base_dir: str) -> List[Tuple[str, str]]:
    """
    Get common data files that should be included in all builds.

    Args:
        base_dir: Repository root directory

    Returns:
        List of (source_path, dest_dir) tuples for PyInstaller datas
    """
    datas = [
        # Application data files
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_load.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_source.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'resources'), 'resources'),

        # Qt configuration
        (os.path.join(base_dir, 'build_config', 'qt.conf'), '.'),
    ]

    # Add Qt binaries
    datas.extend(get_qt_binaries())

    return datas


# ============================================================================
# Common Hidden Imports
# ============================================================================

def get_common_hiddenimports() -> List[str]:
    """
    Get list of modules that need to be explicitly imported.
    These are dynamically loaded at runtime and PyInstaller won't detect them.

    Returns:
        List of module names
    """
    return [
        # UI tabs - dynamically imported at runtime
        'testpad.ui.tabs.matching_box_tab',
        'testpad.ui.tabs.transducer_calibration_tab',
        'testpad.ui.tabs.transducer_linear_tab',
        'testpad.ui.tabs.rfb_tab',
        'testpad.ui.tabs.vol2press_tab',
        'testpad.ui.tabs.burnin_tab',
        'testpad.ui.tabs.nanobubbles_tab',
        'testpad.ui.tabs.temp_analysis_tab',
        'testpad.ui.tabs.hydrophone_tab',
        'testpad.ui.tabs.sweep_plot_tab',
    ]


# ============================================================================
# Runtime Hooks
# ============================================================================

def get_runtime_hooks(base_dir: str) -> List[str]:
    """
    Get paths to runtime hook scripts.

    Args:
        base_dir: Repository root directory

    Returns:
        List of runtime hook script paths
    """
    return [
        os.path.join(base_dir, 'build_config', 'runtime_hook_qt.py'),
        os.path.join(base_dir, 'build_config', 'runtime_hook_mpl.py'),
    ]


# ============================================================================
# Icon Path
# ============================================================================

def get_icon_path(base_dir: str) -> str:
    """
    Get path to application icon.

    Args:
        base_dir: Repository root directory

    Returns:
        Path to icon file
    """
    return os.path.join(base_dir, 'src', 'testpad', 'resources', 'fus_icon_transparent.ico')


# ============================================================================
# Print Build Info
# ============================================================================

def print_build_info(build_type: str, version: str) -> None:
    """
    Print build information banner.

    Args:
        build_type: Type of build (e.g., "portable", "release", "dev")
        version: Version string
    """
    metadata = get_build_metadata()

    print("=" * 70)
    print(f"PyInstaller Build Configuration - {build_type.upper()}")
    print("=" * 70)
    print(f"Version:      {version}")
    print(f"Build Date:   {metadata['build_date']}")
    print(f"Git Commit:   {metadata['git_commit']}")
    print(f"Build Number: {metadata['build_number']}")
    print(f"Built By:     {metadata['built_by']}")
    print("=" * 70)
