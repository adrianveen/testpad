Param(
    [string]$EnvName = 'testpad-dev',
    [string]$LockFile = 'build_config/conda-lock-dev.yml',
    [string]$FallbackEnvFile = 'environment-dev.yml',
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

function Remove-Env([string]$name) {
    if (Test-EnvExists $name) {
        $resp = Read-Host "Environment '$name' exists. Re-create it? (y/N)"
        if ($resp -match '^(y|yes)$') {
            Write-Host "Removing environment '$name'..." -ForegroundColor Yellow
            conda env remove -n $name -y | Out-Null
        } else {
            Write-Host "Keeping existing environment '$name'." -ForegroundColor Green
            return $false
        }
    }
    return $true
}

Assert-Conda

# Operate from repo root so relative paths resolve reliably
Push-Location (Join-Path $PSScriptRoot '..')
try {
    $shouldCreate = Remove-Env -name $EnvName
    if ($shouldCreate) {
        if (Test-Path $LockFile -PathType Leaf -ErrorAction SilentlyContinue) {
            if (Get-Command conda-lock -ErrorAction SilentlyContinue) {
                Write-Host "Creating environment '$EnvName' from lockfile '$LockFile'..." -ForegroundColor Cyan
                conda-lock install -n $EnvName $LockFile | Out-Null
            } else {
                Write-Host "conda-lock is not installed. Installing into base to use lockfile..." -ForegroundColor Yellow
                conda install -n base -c conda-forge conda-lock -y | Out-Null
                Write-Host "Creating environment '$EnvName' from lockfile '$LockFile'..." -ForegroundColor Cyan
                conda-lock install -n $EnvName $LockFile | Out-Null
            }
        } else {
            # Resolve fallback env file: prefer provided, then environment-dev.yml, then environment.yml
            if (-not (Test-Path $FallbackEnvFile)) {
                if (Test-Path 'environment-dev.yml') {
                    $FallbackEnvFile = 'environment-dev.yml'
                } elseif (Test-Path 'environment.yml') {
                    $FallbackEnvFile = 'environment.yml'
                } else {
                    throw "No lockfile or fallback environment file found (looked for $LockFile, environment-dev.yml, environment.yml)."
                }
            }
            Write-Host "Lockfile not found. Creating from '$FallbackEnvFile'..." -ForegroundColor Cyan
            conda env create -n $EnvName -f $FallbackEnvFile -y | Out-Null
        }
    }

    if ($WithPyInstaller) {
        Write-Host "Installing build tooling (pip, pyinstaller) into '$EnvName'..." -ForegroundColor Cyan
        conda run -n $EnvName python -m pip install --upgrade pip | Out-Null
        conda run -n $EnvName python -m pip install --upgrade pyinstaller | Out-Null
    }

    Write-Host "Done. Activate with: conda activate $EnvName" -ForegroundColor Green
} finally {
    Pop-Location
}
