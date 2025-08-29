Param(
    [string]$EnvName = 'testpad-release',
    [switch]$Clean
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Conda {
    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        throw "Conda is not available on PATH. Install Miniconda/Anaconda and restart your shell."
    }
}

Assert-Conda

Push-Location (Join-Path $PSScriptRoot '..')
try {
    if ($Clean) {
        Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
        ./scripts/clean.ps1
    }

    $Spec = 'build_config/testpad_main-portable.spec'
    if (-not (Test-Path $Spec)) { throw "Spec not found: $Spec" }

    Write-Host "Building [portable] with env '$EnvName' and spec '$Spec'..." -ForegroundColor Cyan
    # Use python -m PyInstaller to ensure the interpreter from the env is used
    conda run -n $EnvName python -m PyInstaller $Spec --noconfirm
    Write-Host "Portable build complete. See 'dist/' folder for single .exe." -ForegroundColor Green
} finally {
    Pop-Location
}
