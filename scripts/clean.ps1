Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location (Join-Path $PSScriptRoot '..')
try {
    $targets = @('build', 'dist')
    foreach ($t in $targets) {
        if (Test-Path $t) {
            Write-Host "Removing '$t'..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $t
        }
    }

    # Remove Python bytecode caches
    Get-ChildItem -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "Removing '$($_.FullName)'..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $_.FullName
    }
    Write-Host "Clean complete." -ForegroundColor Green
} finally {
    Pop-Location
}
