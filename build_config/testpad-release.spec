# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for release (one-directory) bundle.

Build command:
    pyinstaller build_config/testpad-release.spec --clean

Output:
    dist/testpad/             (directory containing executable and dependencies)
    dist/testpad/testpad.exe  (main executable)

This build is suitable for:
- Creating Windows installers (e.g., with Inno Setup)
- Distribution as a zip file with all dependencies
- Users who prefer faster startup times (vs single-file)

The workflow will rename this directory to testpad-v{VERSION} for packaging.
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
print_build_info("release", VERSION)

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
    optimize=0,  
)

pyz = PYZ(a.pure)

# Create executable (part of one-directory bundle)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Dependencies go in separate directory
    name='testpad',  # Output: testpad.exe
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

# Collect all files into directory
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='testpad',  # Output directory: dist/testpad/
)

print(f"\n[OK] Release build configuration complete")
print(f"   Output directory: dist/testpad/")
print(f"   Main executable:  dist/testpad/testpad.exe")
print(f"   Version: {VERSION}")
print(f"   Note: Workflow will rename to testpad-v{VERSION}/ during packaging\n")
