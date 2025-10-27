# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for development (one-directory) bundle with debugging enabled.

Build command:
    pyinstaller build_config/testpad_main-dev.spec --clean

Output:
    dist/testpad_main_dev/                      (directory containing executable and dependencies)
    dist/testpad_main_dev/testpad_main_dev.exe  (main executable with console)

This build is suitable for:
- Local development and testing
- Debugging (console output enabled, no optimization)
- Verifying build process before creating release builds

Key differences from release build:
- Console window enabled (shows print() statements and errors)
- No bytecode optimization (easier debugging)
- Different output name to avoid confusion with production builds
"""

import os
import sys

# Add build_config to path for imports
sys.path.insert(0, os.path.join(os.getcwd(), 'build_config'))
from spec_common import (
    get_base_dir,
    get_version,
    validate_build_files,
    get_common_datas,
    get_common_hiddenimports,
    get_runtime_hooks,
    get_icon_path,
    print_build_info,
)

# Get configuration
base_dir = get_base_dir()
VERSION = get_version()

# Validate all required files exist
validate_build_files(base_dir)

# Print build information
print_build_info("development", VERSION)

# Configure Analysis
a = Analysis(
    [os.path.join(base_dir, 'src', 'testpad', 'testpad_main.py')],
    pathex=[os.path.join(base_dir, 'src')],
    binaries=[],
    datas=get_common_datas(base_dir),
    hiddenimports=get_common_hiddenimports(),
    hookspath=[],
    hooksconfig={
        'matplotlib': {
            'backends': ['qtagg'],  # Only Qt backend needed
        },
    },
    runtime_hooks=get_runtime_hooks(base_dir),
    excludes=['PyQt5'],  # Exclude PyQt5 if present
    noarchive=False,
    optimize=0,  # No optimization for easier debugging
)

pyz = PYZ(a.pure)

# Create executable (part of one-directory bundle)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Dependencies go in separate directory
    name='testpad_main_dev',  # Different name to distinguish from release builds
    debug=True,  # Enable debug mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX disabled
    console=True,  # CONSOLE ENABLED for debugging output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=get_icon_path(base_dir),
)

# Collect all files into directory
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='testpad_main_dev',  # Output directory: dist/testpad_main_dev/
)

print(f"\n[OK] Development build configuration complete")
print(f"   Output directory: dist/testpad_main_dev/")
print(f"   Main executable:  dist/testpad_main_dev/testpad_main_dev.exe")
print(f"   Version: {VERSION}")
print(f"   Console: ENABLED (shows debug output)")
print(f"   Optimization: DISABLED (easier debugging)\n")
