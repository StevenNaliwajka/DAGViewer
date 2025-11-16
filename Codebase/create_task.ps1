#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# This script lives in: <project-root>\Codebase
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

$VenvDir   = Join-Path $ProjectRoot ".venv"
$ScriptsDir = Join-Path $VenvDir "Scripts"
$PythonBin = Join-Path $ScriptsDir "python.exe"

if (-not (Test-Path $PythonBin)) {
    Write-Host "Error: virtual environment not found at:" -ForegroundColor Red
    Write-Host "  $VenvDir"
    Write-Host "Run .\setup.ps1 (or your venv setup) first to create it."
    exit 1
}

Set-Location $ProjectRoot

# Ensure Codebase is importable
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"
} else {
    $env:PYTHONPATH = $ProjectRoot
}

Write-Host "PROJECT_ROOT: $ProjectRoot"
Write-Host "Using python: $PythonBin"
Write-Host "PYTHONPATH:   $env:PYTHONPATH"
Write-Host ""

# ✅ Use dotted module path, not slashes
# If your file is at Codebase\GUI\task_create_gui.py:
#   use "Codebase.GUI.task_create_gui"
# If it's at Codebase\GUI\Run\task_create_gui.py:
#   use "Codebase.GUI.Run.task_create_gui"
$Module = "Codebase.GUI.task_create_gui"

& $PythonBin -m $Module
exit $LASTEXITCODE
