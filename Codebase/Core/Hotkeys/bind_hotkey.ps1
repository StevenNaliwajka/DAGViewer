#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# This script lives in: <project-root>\Codebase\Core\Setup
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$CoreDir     = Split-Path -Parent $ScriptDir
$CodebaseDir = Split-Path -Parent $CoreDir
$ProjectRoot = Split-Path -Parent $CodebaseDir

Write-Host "PROJECT_ROOT: $ProjectRoot"

Write-Host ""
Write-Host "----------------------------------------"
Write-Host " Windows hotkey binding not implemented "
Write-Host " yet for DAGViewer."
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "You pressed menu option 1 (Bind hotkey)."
Write-Host "On Linux this uses xbindkeys; on Windows"
Write-Host "you probably want an AutoHotkey script or"
Write-Host "a separate launcher."
Write-Host ""

exit 0
