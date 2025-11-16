#!/usr/bin/env pwsh
# run_windows.ps1
$ErrorActionPreference = 'Stop'

# ---------------------------------------
# Paths
# ---------------------------------------
# This script lives in the project root: DAGViewer/
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir

$CodebaseDir = Join-Path $ProjectRoot "Codebase"
$RunDir      = Join-Path $CodebaseDir "Run"

# bind_hotkey.ps1 lives under Codebase/Core/Setup
$BindHotkey  = Join-Path $CodebaseDir "Core/Setup/bind_hotkey.ps1"

# These live under Codebase/Run
$CreateTask  = Join-Path $RunDir "create_task.ps1"
$ViewDag     = Join-Path $RunDir "view_dag.ps1"

# UserData matches ProjectPaths.userdata (ProjectRoot/UserData)
$UserDataDir = Join-Path $ProjectRoot "UserData"
$PrefsFile   = Join-Path $UserDataDir ".run_prefs"

if (-not (Test-Path $UserDataDir)) {
    New-Item -ItemType Directory -Path $UserDataDir | Out-Null
}

# ---------------------------------------
# Load prefs
# ---------------------------------------
$ShowIntro = 1
if (Test-Path $PrefsFile) {
    foreach ($line in Get-Content $PrefsFile) {
        if ($line -match 'SHOW_INTRO=(\d)') {
            $ShowIntro = [int]$Matches[1]
        }
    }
}

# ---------------------------------------
# Helper to run a script
# ---------------------------------------
function Invoke-Script {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path $Path)) {
        Write-Host "Error: $Label script not found at:" -ForegroundColor Red
        Write-Host "  $Path"
        exit 1
    }

    & $Path
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Label exited with code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# ---------------------------------------
# Intro text
# ---------------------------------------
if ($ShowIntro -eq 1) {
@'
===================== DAGViewer =====================

DAGViewer is a small toolkit for managing "Tasks" and
visualizing them as a Directed Acyclic Graph (DAG).

You can use it in three main ways:

  1) bind_hotkey.ps1 (recommended)
     - Sets up a global hotkey (via your Windows hotkey
       mechanism, e.g. AutoHotkey or a shortcut) that
       launches the "Create Task" GUI.
     - This gives you a commandless, quick-entry
       workflow: press the hotkey, make a task, done.

  2) create_task.ps1
     - Launches the "Create Task" GUI directly.
     - Lets you create a new Task JSON in Tasks/.

  3) view_dag.ps1
     - Launches the DAG viewer.
     - Discovers Tasks/*.json and plots them so you
       can inspect and interact with your task graph.

You can also run those scripts manually:

  Codebase\Core\Setup\bind_hotkey.ps1
  Codebase\Run\create_task.ps1
  Codebase\Run\view_dag.ps1

=====================================================
'@ | Write-Host
    Write-Host ""
}

# ---------------------------------------
# Menu
# ---------------------------------------
Write-Host "What would you like to do?"
Write-Host "  1) Bind global hotkey (recommended)"
Write-Host "  2) Create a task"
Write-Host "  3) View DAG"
Write-Host "  q) Quit"
Write-Host ""

$choice = Read-Host "Enter choice [1/2/3/q]"

switch ($choice.ToLower()) {
    '1' {
        Invoke-Script -Path $BindHotkey -Label "bind_hotkey.ps1"
    }
    '2' {
        Invoke-Script -Path $CreateTask -Label "create_task.ps1"
    }
    '3' {
        Invoke-Script -Path $ViewDag -Label "view_dag.ps1"
    }
    'q' {
        Write-Host "Exiting."
        exit 0
    }
    default {
        Write-Host "Unknown choice: $choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ---------------------------------------
# Ask whether to hide intro next time
# ---------------------------------------
if ($ShowIntro -eq 1) {
    Write-Host "If you want to skip the long explanation next time,"
    Write-Host "type '1' now. Press Enter to keep seeing it."
    $skip = Read-Host "Skip intro in future? [1 = yes / Enter = no]"

    if ($skip -eq '1') {
        'SHOW_INTRO=0' | Set-Content -Path $PrefsFile -Encoding UTF8
        Write-Host "Okay, intro will be skipped next time."
    } else {
        'SHOW_INTRO=1' | Set-Content -Path $PrefsFile -Encoding UTF8
    }
}
