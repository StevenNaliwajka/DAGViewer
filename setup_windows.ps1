#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# ---------------------------------------
# Location of this script (project root: DAGViewer)
# ---------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Project root:          $ScriptDir"
Write-Host ""

# ---------------------------------------
# Helper to run a script and check result
# ---------------------------------------
function Invoke-SetupStep {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path $Path)) {
        Write-Host "Error: $Label script not found at:" -ForegroundColor Red
        Write-Host "  $Path"
        exit 1
    }

    Write-Host "Running $Label ..."
    & $Path
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Label failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host ""
}

# ---------------------------------------
# Paths to setup scripts (PowerShell versions)
# ---------------------------------------
$CreateVenvPs1   = Join-Path $ScriptDir "Codebase/Core/Setup/create_venv.ps1"
$MakeFoldersPs1  = Join-Path $ScriptDir "Codebase/Core/Setup/make_folders.ps1"

# ---------------------------------------
# Run setup steps
# ---------------------------------------
Invoke-SetupStep -Path $CreateVenvPs1  -Label "create_venv.ps1"
Invoke-SetupStep -Path $MakeFoldersPs1 -Label "make_folders.ps1"

Write-Host ""
Write-Host "Setup complete."
Write-Host "To activate the virtual environment in PowerShell, run:"
Write-Host "  & `"$ScriptDir\.venv\Scripts\Activate.ps1`""
Write-Host ""
Write-Host "Or in cmd.exe:"
Write-Host "  $ScriptDir\.venv\Scripts\activate.bat"
