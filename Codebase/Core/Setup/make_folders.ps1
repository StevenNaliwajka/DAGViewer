#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# ---------------------------------------
# Figure out PROJECT_ROOT based on this script's location:
# .../DAGViewer/Codebase/Core/Setup/make_folders.ps1
# -> Setup (1) -> Core (2) -> Codebase (3) -> ProjectRoot
# ---------------------------------------
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))

# ---------------------------------------
# DIR locations
# ---------------------------------------
$TasksDir = Join-Path $ProjectRoot "Tasks"

function New-DirIfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Name
    )

    if (-not (Test-Path $Path)) {
        Write-Host "Creating $Name folder at: $Path"
        New-Item -ItemType Directory -Path $Path | Out-Null
    } else {
        Write-Host "$Name folder already exists at: $Path, reusing it."
    }
}

# Create required folders
New-DirIfMissing -Path $TasksDir -Name "Tasks"
