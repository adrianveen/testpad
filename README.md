Testpad
=======

Desktop application for generating calibration, analysis, and visualization outputs for FUS transducers and related workflows. The repository is structured for developers; end‑users typically receive a packaged installer or executable.

This README focuses on developer setup, project structure, and build/distribution guidance.


Overview
--------
Testpad is a PySide6 (Qt) desktop app with modular tabs for:

- Matching box calculations and CSV plotting
- Transducer calibration reports (sweeps, field, and line plots)
- Transducer linear graphs
- RFB (Radiation Force Balance) analysis
- Sweep graphs
- Burn‑in visualization and stats
- Hydrophone analysis
- Temperature analysis
- Vol2Press sweep analysis and YAML generation

Major dependencies: PySide6, NumPy/SciPy, Matplotlib, h5py, pandas, PyYAML.


Project Structure
-----------------
The codebase uses a “src/” layout and separates UI and non‑UI logic.

```
testpad/                 # repo root
├─ src/
│  └─ testpad/
│     ├─ testpad_main.py           # entry point (module: testpad.testpad_main)
│     ├─ version.py
│     ├─ resources/                # icons, static resources
│     │  ├─ fus_icon_transparent.ico
│     │  └─ ...
│     ├─ ui/
│     │  └─ tabs/                  # all tab widgets (Qt Widgets)
│     │     ├─ matching_box_tab.py
│     │     ├─ transducer_calibration_tab.py
│     │     ├─ transducer_linear_tab.py
│     │     └─ ...
│     ├─ core/                     # non‑UI logic (calculations, I/O)
│     │  ├─ matching_box/
│     │  ├─ transducer/            # calibration + plotting utilities
│     │  └─ ...
│     └─ utils/                    # validators, helpers
│
├─ build_config/                   # PyInstaller specs, build assets
├─ tests/                          # test suite (pytest suggested)
├─ environment.yml                 # dev environment (conda)
├─ pyproject.toml                  # packaging / build config
└─ .vscode/launch.json             # debug configurations
```


Getting Started (Developers)
---------------------------

Prerequisites
- Python 3.12 (recommended)
- Conda (Miniconda/Anaconda) recommended for native deps (NumPy/h5py/etc.)
- VS Code (optional) with Python extension

Setup
1) Clone the repository.
2) Create the environment (includes PySide6 6.7.x and libraries):
   - `conda env create -f environment.yml`
3) Activate it:
   - `conda activate testpad-dev`

Run
- From repo root (recommended):
  - `python -m testpad.testpad_main`

VS Code
- Preferred debug config (module mode):
  - module: `testpad.testpad_main`
  - cwd: `${workspaceFolder}/src`

Packaging / Distribution
------------------------
We use PyInstaller specs under `build_config/` to generate an executable.

- Ensure the environment is active, then install PyInstaller if needed:
  - `pip install pyinstaller`
- Build using the provided spec:
  - `pyinstaller build_config/testpad_main.spec`

Notes
- The spec bundles:
  - `src/testpad/resources` → collected as `resources/` at runtime
  - Matching box schematic images from `src/testpad/core/matching_box/`
- The application resolves the app icon from package resources and also when frozen (via `_MEIPASS`).


Key Conventions
---------------
- Code style: PEP 8 (auto‑formatters optional), with type hints where practical.
- UI (Qt Widgets) lives under `src/testpad/ui/tabs/`.
- Non‑UI logic belongs in `src/testpad/core/` (pure functions, I/O, plotting backends).
- Shared helpers live in `src/testpad/utils/`.
- Avoid heavy work in `__init__` for long‑running classes; prefer explicit `run()` methods.


Transducer Calibration API (Developers)
--------------------------------------
The calibration module provides a typed API while preserving legacy usage.

- Preferred:
  - `from testpad.core.transducer.combined_calibration_figures_python import CombinedCalibration, CombinedCalibrationConfig`
  - Build a `CombinedCalibrationConfig` and pass it to `CombinedCalibration(config, textbox)`; then call `getGraphs()`.
- Legacy wrapper (still available):
  - `from testpad.core.transducer.combined_calibration_figures_python import combined_calibration`
  - Call `combined_calibration(var_list, textbox).getGraphs()`.


Testing
-------
- Test suite placeholder in `tests/`. We recommend `pytest`.
- Philosophy: unit test core modules (in `src/testpad/core/`); keep UI tests light.


Troubleshooting
---------------
- `ModuleNotFoundError: No module named 'testpad'`
  - Run from the project root using module mode: `python -m testpad.testpad_main`, or set `PYTHONPATH=src`.
- Qt plugin errors when frozen
  - Ensure PyInstaller spec is used; it collects Qt plugins and Matplotlib backends.
- Missing DLLs (BLAS/HDF5)
  - Use the provided conda environment; it ensures compatible native libs.


Contributing
------------
- Use feature branches and pull requests.
- Keep changes focused; document any user‑visible behavior updates.
- Prefer typed, testable code in `core/`; keep UI layers thin.


License
-------
If a license is required, add it here. Otherwise, the code is proprietary to its author(s) and/or organization.
