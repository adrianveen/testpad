Param(
    [string]$EnvName = 'testpad-release',
    [ValidateSet('dev','release','portable')]
    [string]$Target = 'release',
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

    switch ($Target) {
        'dev' { $Spec = 'build_config/testpad_main-dev.spec' }
        'release' { $Spec = 'build_config/testpad_main-release.spec' }
        'portable' { $Spec = 'build_config/testpad_main-portable.spec' }
        default { throw "Unknown target: $Target" }
    }

    if (-not (Test-Path $Spec)) { throw "Spec not found: $Spec" }

    Write-Host "Building [$Target] with PyInstaller using env '$EnvName' and spec '$Spec'..." -ForegroundColor Cyan
    conda run -n $EnvName pyinstaller $Spec --noconfirm
    Write-Host "Build complete. See 'dist/' and 'build/' folders." -ForegroundColor Green
} finally {
    Pop-Location
}
