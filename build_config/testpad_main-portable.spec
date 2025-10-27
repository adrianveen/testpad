# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for portable (single-file) executable.

Build command:
    pyinstaller build_config/testpad_main-portable.spec --clean

Output:
    dist/testpad_main.exe  (single executable with everything bundled)

This build is suitable for:
- Quick distribution without installer
- Running from USB drives or shared folders
- Users who prefer standalone executables
"""

import os
import sys

# Add build_config to path for imports
build_config_path = os.path.join(os.getcwd(), 'build_config')
sys.path.insert(0, build_config_path)
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
# Remove from path to prevent PyInstaller from auto-discovering runtime hooks
sys.path.remove(build_config_path)

# Get configuration
base_dir = get_base_dir()
VERSION = get_version()

# Validate all required files exist
validate_build_files(base_dir)

# Print build information
print_build_info("portable", VERSION)

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
    optimize=0,  # Maximum bytecode optimization for production
)

pyz = PYZ(a.pure)

# Single-file executable (onefile mode)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='testpad_main',  # Output: testpad_main.exe (workflow expects this name)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX disabled for compatibility
    console=False,  # Windowed application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=get_icon_path(base_dir),
)

print(f"\n[OK] Portable build configuration complete")
print(f"   Output will be: dist/testpad_main.exe")
print(f"   Version: {VERSION}\n")
