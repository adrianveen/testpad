Scripts
=======

This folder contains helper PowerShell scripts to streamline environment setup, running, building, and cleaning the project.

Prerequisites
-------------
- Windows with PowerShell 5+ (or PowerShell 7)
- Conda (Miniconda/Anaconda) on PATH
- Optional: conda-lock (installed automatically for release setup if a lockfile is used)

Execution policy
----------------
If your execution policy blocks running local scripts, enable it for the current session:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Scripts
-------

setup-dev-env.ps1
  - Creates or re-creates the developer environment from `environment.yml`.
  - Prompts if the environment already exists.
  - Installs `pyinstaller` for convenience.
  - Usage:
    - `./scripts/setup-dev-env.ps1`
    - Parameters:
      - `-EnvName 'testpad-dev'` (default)
      - `-EnvironmentFile 'environment.yml'`
      - `-WithPyInstaller:$false` to skip installing PyInstaller

setup-release-env.ps1
  - Creates or re-creates the release environment from `build_config/conda-lock-release.yml` if available, otherwise falls back to `environment.yml`.
  - Prompts if the environment already exists.
  - Ensures `conda-lock` is installed to honor lockfiles.
  - Installs `pyinstaller` for convenience.
  - Usage:
    - `./scripts/setup-release-env.ps1`
    - Parameters:
      - `-EnvName 'testpad-release'` (default)
      - `-LockFile 'build_config/conda-lock-release.yml'`
      - `-FallbackEnvFile 'environment.yml'`
      - `-WithPyInstaller:$false` to skip installing PyInstaller

run.ps1
  - Runs the application in module mode using the developer environment.
  - Usage: `./scripts/run.ps1` (from repo root)
  - Parameters:
    - `-EnvName 'testpad-dev'` (default)
    - `-Module 'testpad.testpad_main'` (default)

build.ps1
  - Builds the application using PyInstaller and the release environment.
  - Usage: `./scripts/build.ps1`
  - Parameters:
    - `-EnvName 'testpad-release'` (default)
    - `-Spec 'build_config/testpad_main.spec'` (default)
    - `-Clean` to remove previous build artifacts before building

clean.ps1
  - Removes build artifacts (`build/`, `dist/`) and `__pycache__/` folders.
  - Usage: `./scripts/clean.ps1`

Tips
----
- Always run scripts from the repo root for consistent paths.
- The VS Code debug configuration can launch the app in module mode; see `.vscode/launch.json`.
- If you require cross‑platform shells, consider adding analogous `.sh` scripts for Git Bash/CI.

