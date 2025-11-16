#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# ---------------------------------------
# Location of this script (Codebase/Core/Setup)
# ---------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Project root: go up three levels from Codebase/Core/Setup
#   ProjectRoot/Codebase/Core/Setup
#   -> Setup (1) -> Core (2) -> Codebase (3) -> ProjectRoot
$ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))

# Virtual environment directory
$VenvDir = Join-Path $ProjectRoot ".venv"

# Unified JSON requirements file
$ReqJson = Join-Path $ScriptDir "requirements.json"

Write-Host "Script dir:      $ScriptDir"
Write-Host "Project root:    $ProjectRoot"
Write-Host "Virtualenv dir:  $VenvDir"
Write-Host "Requirements:    $ReqJson"
Write-Host ""

# ---------------------------------------
# Sanity checks
# ---------------------------------------
if (-not (Test-Path $ReqJson)) {
    Write-Host "ERROR: requirements.json not found at: $ReqJson" -ForegroundColor Red
    exit 1
}

# ---------------------------------------
# Find a usable Python executable
# Prefer:
#   1) py
#   2) python (but NOT the WindowsApps store shim)
#   3) python3
# ---------------------------------------
$pythonCmd = $null

foreach ($candidate in @('py', 'python', 'python3')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }

    # If it's the Microsoft Store shim for python.exe, skip it
    if ($candidate -eq 'python' -and $cmd.Path -like '*WindowsApps*') {
        continue
    }

    $pythonCmd = $candidate
    break
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "       Tried: py, python, python3"
    exit 1
}

Write-Host "Using Python command: $pythonCmd"
# Show version (best-effort, don't fail if this errors)
try {
    & $pythonCmd --version
} catch { }

Write-Host ""

# ---------------------------------------
# Create venv if it doesn't exist
# ---------------------------------------
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment (exit code $LASTEXITCODE)." -ForegroundColor Red
        exit $LASTEXITCODE
    }
} else
{
    Write-Host "Virtual environment already exists, reusing it."
}

# Use the venv's Python
$VenvPython = Join-Path $VenvDir "Scripts/python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: Could not find python.exe in the virtual environment:" -ForegroundColor Red
    Write-Host "  $VenvPython"
    exit 1
}

# ---------------------------------------
# Upgrade pip inside venv
# ---------------------------------------
Write-Host "Upgrading pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: pip upgrade failed with exit code $LASTEXITCODE" -ForegroundColor Yellow
}

# ---------------------------------------
# Read requirements.json
# Supports:
#   * { "pip": ["pkg1", "pkg2"] }
#   * { "packages": ["pkg1", "pkg2"] }  # legacy
#   * ["pkg1", "pkg2"]                  # legacy: whole file is list
#   * { "system": ["pkgA", "pkgB"] }
# ---------------------------------------
try {
    $jsonText = Get-Content -Path $ReqJson -Raw -ErrorAction Stop
    $data     = $jsonText | ConvertFrom-Json
} catch {
    Write-Host "ERROR: Failed to parse JSON in $ReqJson" -ForegroundColor Red
    Write-Host $_
    exit 1
}

# ---------------------------------------
# Helper: get pip package list
# ---------------------------------------
$pipPkgs = @()

if ($data -is [System.Collections.IList]) {
    # Entire file is a list -> pip-only
    $pipPkgs = @($data)
} elseif ($data -is [pscustomobject]) {
    $props = $data.PSObject.Properties.Name
    if ($props -contains 'pip') {
        $pipPkgs = @($data.pip)
    } elseif ($props -contains 'packages') {
        $pipPkgs = @($data.packages)
    } else {
        $pipPkgs = @()
    }
} else {
    Write-Host "ERROR: $ReqJson must be a JSON object or array." -ForegroundColor Red
    exit 1
}

$pipPkgs = $pipPkgs | Where-Object { $_ -ne $null } | ForEach-Object { "$_" }

# ---------------------------------------
# Helper: get system package list
# ---------------------------------------
$sysPkgs = @()

if ($data -is [pscustomobject]) {
    if ($data.PSObject.Properties.Name -contains 'system') {
        $sysPkgs = @($data.system) | Where-Object { $_ -ne $null } | ForEach-Object { "$_" }
    }
    # If entire file is a list, treat as pip-only; sysPkgs stays empty
}

# ---------------------------------------
# 1) PIP PACKAGES
# ---------------------------------------
Write-Host "Parsing pip requirements..."

if (-not $pipPkgs -or $pipPkgs.Count -eq 0) {
    Write-Host "No pip packages found; skipping pip install."
} else {
    Write-Host "Installing pip packages:"
    foreach ($pkg in $pipPkgs) {
        Write-Host "  $pkg"
    }

    & $VenvPython -m pip install @pipPkgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pip install failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# ---------------------------------------
# 2) SYSTEM PACKAGES (Windows: manual)
# ---------------------------------------
Write-Host ""
Write-Host "Parsing system requirements..."

if (-not $sysPkgs -or $sysPkgs.Count -eq 0) {
    Write-Host "No system requirements listed."
} else {
    Write-Host "System packages required (for your OS, e.g. via winget/Chocolatey/manual):"
    foreach ($pkg in $sysPkgs) {
        Write-Host "  $pkg"
    }

    Write-Host ""
    Write-Host "NOTE: This script does not auto-install system packages on Windows."
    Write-Host "      Please install them manually using your preferred package manager"
    Write-Host "      (e.g. winget, Chocolatey) or from the official installers."
}

Write-Host ""
Write-Host "Done! To use the environment later in PowerShell, run:"
Write-Host "  & `"$VenvDir\Scripts\Activate.ps1`""
Write-Host ""
Write-Host "Or in cmd.exe:"
Write-Host "  $VenvDir\Scripts\activate.bat"
