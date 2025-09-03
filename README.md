Testpad
=======

Desktop application for generating calibration, analysis, and visualization outputs for FUS transducers and related workflows. The application is built with PySide6 (Qt) and provides modular tabs for common lab and production tasks.

This README covers setup, usage, and build/distribution for developers.

## Table of Contents

- [Testpad](#testpad)
  - [Table of Contents](#table-of-contents)
  - [About the Project](#about-the-project)
    - [Key Features](#key-features)
    - [Built With](#built-with)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Launching The App](#launching-the-app)
    - [Common Workflows](#common-workflows)
    - [Building/Packaging](#buildingpackaging)
  - [Contributing](#contributing)
  - [Troubleshooting](#troubleshooting)
  - [Example Dataset](#example-dataset)
  - [License](#license)
  - [Contact](#contact)

---

## About the Project

Testpad is a PySide6 desktop app with modular tabs to support calibration, plotting, and analysis for FUS transducers and related workflows.

### Key Features
- Tabbed workflows for:
  - Matching box calculations and CSV plotting
  - Transducer calibration reports (sweeps, field, line plots)
  - Transducer linear graphs
  - Radiation Force Balance (RFB) analysis
  - Sweep graphs and burn-in visualization
  - Hydrophone and temperature analysis
  - Vol2Press sweep analysis and YAML generation
- Lazy-loaded tabs for faster startup and responsive UI
- Packaged builds for distribution (one-dir and one-file)

### Built With
- Python 3.12
- PySide6 (Qt 6)
- NumPy, SciPy, pandas
- Matplotlib, Pillow
- h5py, PyYAML

---

## Getting Started

Follow these steps to set up the project locally for use or development.

### Prerequisites
- Python 3.12
- Conda (Miniconda/Anaconda) for environment management
- Windows PowerShell recommended for helper scripts (cross-platform Python run is still supported)

### Installation

1) Clone the repository
```bash
git clone <this-repo-url>
cd testpad
```

2) Create the developer environment (includes PySide6 and libraries)
- Recommended (uses lockfile if available):
```powershell
./scripts/setup-dev-env.ps1
```
- Manual:
```powershell
conda env create -f environment-dev.yml
```

3) Activate the environment
```powershell
conda activate testpad-dev
```

---

## Usage

### Launching The App
- Using helper script (from repo root):
```powershell
./scripts/run.ps1
```
- Manually from `src/`:
```powershell
cd src
python -m testpad.testpad_main
```
- Or from repo root by setting `PYTHONPATH`:
```powershell
$env:PYTHONPATH = "src"
python -m testpad.testpad_main
```

VS Code (optional)
- Module: `testpad.testpad_main`
- CWD: `${workspaceFolder}/src`
- Optional env: `PYTHONPATH=${workspaceFolder}/src`

### Common Workflows
- Transducer Calibration Report
  - Open the “Transducer Calibration Report” tab.
  - Provide required inputs and generate the sweep/field/line plots; export figures as needed.
- Matching Box Calculator
  - Open the “Matching Box” tab.
  - Import/load CSV data and compute LC circuit values; visualize CSV graphs.
- Sweep Analysis / Burn-in / Hydrophone / Temperature
  - Open the corresponding tab, load relevant data files, and generate plots/exports as needed.

### Building/Packaging
We use PyInstaller specs under `build_config/` to generate executables.

1) Prepare a release environment
```powershell
./scripts/setup-release-env.ps1
```
2) Build variants
```powershell
# One-dir, windowed
./scripts/build-release.ps1 -Clean

# One-file portable .exe
./scripts/build-portable.ps1 -Clean

# One-dir, console (dev)
./scripts/build-dev.ps1 -Clean

# Aggregator
./scripts/build.ps1 -Target release   -Clean
./scripts/build.ps1 -Target portable  -Clean
./scripts/build.ps1 -Target dev       -Clean
```
Manual equivalent:
```powershell
conda run -n testpad-release pyinstaller build_config/testpad_main-release.spec --noconfirm
```

Notes
- Specs bundle `src/testpad/resources` as `resources/` at runtime and include matching-box schematics.
- Runtime hooks collect Qt plugins and Matplotlib backends: `build_config/runtime_hook_qt.py`, `build_config/runtime_hook_mpl.py`.

---

## Contributing

Please make new contributions under a feature branch and open a pull request for review.

1) Create a feature branch
```bash
git checkout -b prefix/feature-name
```
2) Commit your changes
```bash
git commit -m "Add feature-name"
```
3) Push the branch
```bash
git push origin prefix/feature-name
```
4) Open a pull request

Branch name prefixes: `new_feat/` or `bug/` are suggested.

---

## Troubleshooting
- `ModuleNotFoundError: No module named 'testpad'`
  - Run from `src/` (e.g., `cd src; python -m testpad.testpad_main`) or set `PYTHONPATH=src` from the repo root. The helper script `./scripts/run.ps1` runs in module mode for you.
- Qt plugin errors when frozen
  - Ensure you build using the PyInstaller specs; runtime hooks collect Qt plugins and Matplotlib backends.
- Missing DLLs (BLAS/HDF5)
  - Use the provided conda environments (`environment-*.yml`) or lockfiles.
- PowerShell execution policy blocks scripts
  - Enable for the current session:
    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

---

## Example Dataset
No public example datasets are bundled with this repository. If you need sample data for testing or demos, contact your team or use internal lab datasets.

---

## License

If a license is required, add it here. Otherwise, the code is proprietary to its author(s) and/or organization.

---

## Contact

- Open an issue in this repository for bugs and feature requests.
- For internal support, contact your FUS Instruments team/maintainer.
- Maintainer: Adrian Veenhoven — adrian.veen@gmail.com

