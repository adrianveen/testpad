Param(
    [string]$EnvName = 'testpad-dev',
    [string]$Module = 'testpad.testpad_main'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Conda {
    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        throw "Conda is not available on PATH. Install Miniconda/Anaconda and restart your shell."
    }
}

Assert-Conda

# Run from repo root to keep paths predictable
Push-Location (Join-Path $PSScriptRoot '..')
try {
    Write-Host "Running module '$Module' in env '$EnvName'..." -ForegroundColor Cyan
    conda run -n $EnvName python -m $Module
} finally {
    Pop-Location
}
