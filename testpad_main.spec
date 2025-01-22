import os

# Get the current working directory (where PyInstaller is run)
base_dir = os.getcwd()

a = Analysis(
    ['testpad_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(base_dir, "matching_box", "cap_across_load.jpg"), "matching_box"),
        (os.path.join(base_dir, "matching_box", "cap_across_source.jpg"), "matching_box"),
        (os.path.join(base_dir, "images"), "images"),  # Add the entire images directory
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={
        "matplotlib": {
            "backends": "all",  # collect all backends
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
    name='testpad_main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='testpad_main',
)
