import os
import sys
import glob

# Get the current working directory (where PyInstaller is run)
base_dir = os.getcwd()  # repo root (build scripts set CWD to repo root)
sys.path.insert(0, os.path.join(base_dir, 'src'))
from testpad.version import __version__ as VERSION
from PySide6.QtCore import __file__ as PYSIDE6_QTCORE_FILE, QLibraryInfo

# Minimal Qt plugin paths (Windows) — robust discovery across Conda/venv installs
def _find_qt_plugins_root() -> str:
    try:
        p = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
        if p and os.path.exists(p):
            return p
    except Exception:
        pass
    candidates = [
        os.path.join(sys.prefix, 'Library', 'plugins'),  # Conda on Windows
        os.path.join(sys.prefix, 'plugins'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins'),
        os.path.join(os.path.dirname(os.path.dirname(PYSIDE6_QTCORE_FILE)), 'plugins'),
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, 'platforms')):
            return c
    return candidates[0]

qt_plugins_src = _find_qt_plugins_root()

def _find_platform_plugin(root: str, name: str = 'qwindows'):
    roots = [
        os.path.join(root, 'platforms'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'Qt', 'plugins', 'platforms'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins', 'platforms'),
        os.path.join(sys.prefix, 'Library', 'plugins', 'platforms'),
        os.path.join(sys.prefix, 'plugins', 'platforms'),
    ]
    for r in roots:
        cand = os.path.join(r, f'{name}.dll')
        if os.path.exists(cand):
            return cand
        gl = glob.glob(os.path.join(r, f'{name}*.dll'))
        if gl:
            return gl[0]
    return None

def _find_image_plugin(root: str, name: str):
    roots = [
        os.path.join(root, 'imageformats'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'Qt', 'plugins', 'imageformats'),
        os.path.join(os.path.dirname(PYSIDE6_QTCORE_FILE), 'plugins', 'imageformats'),
        os.path.join(sys.prefix, 'Library', 'plugins', 'imageformats'),
        os.path.join(sys.prefix, 'plugins', 'imageformats'),
    ]
    for r in roots:
        cand = os.path.join(r, f'{name}.dll')
        if os.path.exists(cand):
            return cand
        gl = glob.glob(os.path.join(r, f'{name}*.dll'))
        if gl:
            return gl[0]
    return None

qwindows_path = _find_platform_plugin(_find_qt_plugins_root(), 'qwindows')
qt_platforms = [(qwindows_path, 'qt_plugins/platforms')] if qwindows_path else []
qt_imageformats_files = ['qico.dll', 'qpng.dll', 'qjpeg.dll']
qt_imageformats = []
for f in qt_imageformats_files:
    found = _find_image_plugin(qt_plugins_src, f.split('.')[0])
    if found:
        qt_imageformats.append((found, 'qt_plugins/imageformats'))

# Release build (one-dir, windowed). Suitable for zipping or packaging into an installer.
a = Analysis(
    [os.path.join(base_dir, 'src', 'testpad', 'testpad_main.py')],
    pathex=[os.path.join(base_dir, 'src')],
    binaries=[],
    datas=[
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_load.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'core', 'matching_box', 'cap_across_source.jpg'), 'matching_box'),
        (os.path.join(base_dir, 'src', 'testpad', 'resources'), 'resources'),  # bundle resources/
        (os.path.join(base_dir, 'build_config', 'qt.conf'), '.'),
    ] + qt_platforms + qt_imageformats,
    hiddenimports=[
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
    ],
    hookspath=[],
    hooksconfig={
        'matplotlib': {
            # Only the Qt backend needed by PySide6
            'backends': ['qtagg'],
        },
    },
    runtime_hooks=[
        os.path.join(base_dir, 'build_config', 'runtime_hook_qt.py'),
        os.path.join(base_dir, 'build_config', 'runtime_hook_mpl.py'),
    ],
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
