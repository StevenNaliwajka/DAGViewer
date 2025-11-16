#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# This script lives in: <project-root>\Codebase\Run
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

$VenvDir    = Join-Path $ProjectRoot ".venv"
$PythonBin  = Join-Path $VenvDir "Scripts/python.exe"

if (-not (Test-Path $PythonBin)) {
    Write-Host "Error: virtual environment not found at:" -ForegroundColor Red
    Write-Host "  $VenvDir"
    Write-Host "Run .\setup.ps1 (or your venv setup) first to create it."
    exit 1
}

# Run everything from project root
Set-Location $ProjectRoot

# Ensure PYTHONPATH includes the project root
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"
} else {
    $env:PYTHONPATH = $ProjectRoot
}

Write-Host "PROJECT_ROOT: $ProjectRoot"
Write-Host "Using python: $PythonBin"
Write-Host "PYTHONPATH:   $env:PYTHONPATH"
Write-Host ""

# ---------------------------------
# Correct module for VIEW DAG
# ---------------------------------
$Module = "Codebase.GUI.dag_viewer"

Write-Host "Running module: $Module"
& $PythonBin -m $Module
$exitCode = $LASTEXITCODE
Write-Host "Python exited with code $exitCode"
exit $exitCode
