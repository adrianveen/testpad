import os
import sys

# Get the current working directory (where PyInstaller is run)
base_dir = os.getcwd()  # repo root (build scripts set CWD to repo root)
sys.path.insert(0, os.path.join(base_dir, 'src'))
from testpad.version import __version__ as VERSION

# Release build (one-dir, windowed). Suitable for zipping or packaging into an installer.
a = Analysis(
    [os.path.join(base_dir, 'src', 'testpad', 'testpad_main.py')],
    pathex=[os.path.join(base_dir, 'src')],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_load.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_source.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'resources'), 'resources'),  # bundle resources/
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={
        'matplotlib': {
            # Only the Qt backend needed by PySide6
            'backends': ['qtagg'],
        },
    },
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f'testpad_v{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # windowed app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(base_dir, 'src', 'testpad', 'resources', 'fus_icon_transparent.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=f'testpad_v{VERSION}',
)
