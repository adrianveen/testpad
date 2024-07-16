# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['testpad_main.py'],
    pathex=[],
    binaries=[],
    datas=[(r"C:\Users\RKPC\Documents\summer_2024\testpad\matching_box\cap_across_load.jpg", "matching_box"), \
    (r"C:\Users\RKPC\Documents\summer_2024\testpad\matching_box\cap_across_source.jpg", "matching_box")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={"matplotlib": {
            # "backends": "auto",  # auto-detect; the default behavior
            "backends": "all",  # collect all backends
            # "backends": "TkAgg",  # collect a specific backend
            # "backends": ["TkAgg", "Qt5Agg"],  # collect multiple backends
        },},
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
