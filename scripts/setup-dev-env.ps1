Param(
    [string]$EnvName = 'testpad-dev',
    [string]$EnvironmentFile = 'environment.yml',
    [switch]$WithPyInstaller = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Conda {
    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        throw "Conda is not available on PATH. Install Miniconda/Anaconda and restart your shell."
    }
}

function Test-EnvExists([string]$name) {
    $j = conda env list --json | ConvertFrom-Json
    return ($j.envs | ForEach-Object { Split-Path $_ -Leaf } | Where-Object { $_ -eq $name } | Measure-Object).Count -gt 0
}

function New-Or-Recreate-Env {
    param([string]$name, [string]$file)

    if (Test-EnvExists $name) {
        $resp = Read-Host "Environment '$name' exists. Re-create it? (y/N)"
        if ($resp -match '^(y|yes)$') {
            Write-Host "Removing environment '$name'..." -ForegroundColor Yellow
            conda env remove -n $name -y | Out-Null
        } else {
            Write-Host "Keeping existing environment '$name'." -ForegroundColor Green
            return
        }
    }

    Write-Host "Creating environment '$name' from '$file'..." -ForegroundColor Cyan
    conda env create -n $name -f $file -y | Out-Null
}

Assert-Conda

if (-not (Test-Path $EnvironmentFile)) {
    throw "Environment file not found: $EnvironmentFile"
}

New-Or-Recreate-Env -name $EnvName -file $EnvironmentFile

if ($WithPyInstaller) {
    Write-Host "Installing build tooling (pip, pyinstaller) into '$EnvName'..." -ForegroundColor Cyan
    conda run -n $EnvName python -m pip install --upgrade pip | Out-Null
    conda run -n $EnvName python -m pip install --upgrade pyinstaller | Out-Null
}

Write-Host "Done. Activate with: conda activate $EnvName" -ForegroundColor Green
