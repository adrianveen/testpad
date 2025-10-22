Scripts
=======

This folder contains helper PowerShell scripts to streamline environment setup, running, building, and cleaning the project.

Prerequisites
-------------
**Modern (uv-based):**
- Python 3.12
- uv package manager (`pip install uv` or see https://docs.astral.sh/uv/)
- Usage: `uv pip install -e ".[dev]"` from repo root

**Legacy (conda-based PowerShell scripts):**
- Windows with PowerShell 5+ (or PowerShell 7)
- Conda (Miniconda/Anaconda) on PATH
- Optional: conda-lock (installed automatically for release setup if a lockfile is used)
- Note: The PowerShell scripts below are legacy. Consider using uv for modern Python development.

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
  - Usage examples:
    - `./scripts/build.ps1 -Target release`   → one-dir windowed app (zip/installer)
    - `./scripts/build.ps1 -Target portable`  → one-file portable .exe (windowed)
    - `./scripts/build.ps1 -Target dev`       → one-dir with console (debug)
  - Parameters:
    - `-EnvName 'testpad-release'` (default)
    - `-Target {dev|release|portable}` (default: release)
    - `-Clean` to remove previous build artifacts before building

build-dev.ps1
  - Shortcut for dev builds (one-dir, console). Uses `testpad_main-dev.spec`.
  - Usage: `./scripts/build-dev.ps1 -Clean`

build-release.ps1
  - Shortcut for release builds (one-dir, windowed). Uses `testpad_main-release.spec`.
  - Usage: `./scripts/build-release.ps1 -Clean`

build-portable.ps1
  - Shortcut for portable builds (one-file, windowed). Uses `testpad_main-portable.spec`.
  - Usage: `./scripts/build-portable.ps1 -Clean`

clean.ps1
  - Removes build artifacts (`build/`, `dist/`) and `__pycache__/` folders.
  - Usage: `./scripts/clean.ps1`

bump_version.py
  - Automates version bumping and local tag creation for Gitflow releases (custom implementation, no dependencies).
  - Updates VERSION file, creates git commit with conventional format, creates local annotated tag.
  - **Does NOT auto-push** - Manual push required to trigger release workflow.
  - **Safety checks**: Clean git status, branch name validation (release/*, hotfix/*), tag existence.
  - Usage:
    - `python scripts/bump_version.py` → Interactive mode (prompts for bump type and dry-run)
    - `python scripts/bump_version.py patch` → Bug fix release (1.11.0 → 1.11.1)
    - `python scripts/bump_version.py minor` → Feature release (1.11.0 → 1.12.0)
    - `python scripts/bump_version.py major` → Breaking change (1.11.0 → 2.0.0)
    - `python scripts/bump_version.py patch --dry-run` → Preview changes without applying
  - **After running**: Review with `git log -1 --stat`, then push with `git push origin <branch> --follow-tags`
  - **Rollback before push**: `git tag -d v1.x.x && git reset --hard HEAD~1`
  - **Recommended for most users** - Simple, no dependencies, safe defaults.

version_bump_bumpversion.py
  - Alternative version bumping using the `bump-my-version` library (requires installation).
  - Same functionality as `bump_version.py` but uses an industry-standard library.
  - Requires: `uv pip install -e ".[dev]"` or `pip install bump-my-version`
  - Usage (identical to bump_version.py):
    - `python scripts/version_bump_bumpversion.py patch`
    - `python scripts/version_bump_bumpversion.py minor`
    - `python scripts/version_bump_bumpversion.py major`
  - Configuration in `.bumpversion.toml`
  - **Choose if you need** pre-release versions or prefer using standard tools.
  - See `docs/VERSION_BUMP_COMPARISON.md` for detailed comparison.

**Release Documentation:**
  - See `docs/RELEASE_WORKFLOW.md` for complete Gitflow release process.
  - See `docs/WORKFLOWS_SUMMARY.md` for GitHub Actions workflow details.
  - See `docs/RELEASE_WORKFLOW_DIAGRAM.md` for visual workflow diagrams.
  - See `docs/WORKFLOW_IMPROVEMENTS.md` for optional enhancements.
  - See `docs/VERSION_BUMP_COMPARISON.md` to choose between version bump scripts.

Modern uv Workflow
------------------
For modern Python development using uv:

**Setup:**
```bash
# Install dependencies and project in editable mode
uv pip install -e ".[dev]"
```

**Run:**
```bash
# Run as module
python -m testpad

# Or use the installed command (if using project.scripts in pyproject.toml)
testpad
```

**Version Bump:**
```bash
# Interactive mode
python scripts/bump_version.py

# Or specify bump type
python scripts/bump_version.py patch --dry-run
python scripts/bump_version.py patch
```

**Build Release:**
```bash
# Uses PyInstaller (installed via dev dependencies)
pyinstaller build_config/testpad_main-release.spec
```

Tips
----
- Always run scripts from the repo root for consistent paths.
- The VS Code debug configuration can launch the app in module mode; see `.vscode/launch.json`.
- If you require cross‑platform shells, consider adding analogous `.sh` scripts for Git Bash/CI.

Windows .bat wrappers (double‑click friendly)
--------------------------------------------
Located in `scripts/win/`. These call the PowerShell scripts with ExecutionPolicy Bypass and keep the window open with `pause`.

- `scripts/win/setup-dev-env.bat` → runs `scripts/setup-dev-env.ps1`
- `scripts/win/setup-release-env.bat` → runs `scripts/setup-release-env.ps1`
- `scripts/win/run.bat` → runs `scripts/run.ps1`
- `scripts/win/build-dev.bat` → runs `scripts/build-dev.ps1 -Clean`
- `scripts/win/build-release.bat` → runs `scripts/build-release.ps1 -Clean`
- `scripts/win/build-portable.bat` → runs `scripts/build-portable.ps1 -Clean`

Note: Remove `-Clean` inside the `.bat` file if you prefer incremental builds by default.
