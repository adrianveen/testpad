import os
import sys

base_dir = os.getcwd()
sys.path.insert(0, os.path.join(base_dir, 'src'))
from testpad.version import __version__ as VERSION

# Developer build (one-dir, console enabled for debugging)
a = Analysis(
    ['src/testpad/testpad_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_load.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_source.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'resources'), 'resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={
        'matplotlib': {
            'backends': 'all',
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
    name=f'testpad_dev_{VERSION}',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # console for debugging output
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
    name=f'testpad_dev_{VERSION}',
)
