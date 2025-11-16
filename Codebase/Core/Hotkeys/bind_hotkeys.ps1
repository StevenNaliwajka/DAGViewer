#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------
# Resolve project paths
# This script lives in: <project-root>\Codebase\Core\Hotkeys
# ---------------------------------------------------
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path   # ...\Codebase\Core\Hotkeys
$CoreDir     = Split-Path -Parent $ScriptDir                     # ...\Codebase\Core
$CodebaseDir = Split-Path -Parent $CoreDir                       # ...\Codebase
$ProjectRoot = Split-Path -Parent $CodebaseDir                   # ...\DAGViewer

Write-Host "PROJECT_ROOT: $ProjectRoot"
Write-Host "CODEBASE_DIR: $CodebaseDir"
Write-Host ""

# ---------------------------------------------------
# Find .ps1 scripts directly under Codebase\
# ---------------------------------------------------
$scriptFiles = Get-ChildItem -Path $CodebaseDir -Filter *.ps1 -File | Sort-Object Name

if (-not $scriptFiles -or $scriptFiles.Count -eq 0) {
    Write-Host "No .ps1 scripts found directly under:" -ForegroundColor Yellow
    Write-Host "  $CodebaseDir"
    exit 0
}

Write-Host "Available PowerShell scripts in Codebase\:"
Write-Host ""

for ($i = 0; $i -lt $scriptFiles.Count; $i++) {
    $idx = $i + 1
    $relPath = $scriptFiles[$i].Name
    Write-Host ("[{0}] {1}" -f $idx, $relPath)
}

Write-Host ""
Write-Host "Enter the scripts you want to bind to hotkeys."
Write-Host "  - Use numbers (e.g. 1,3,4)"
Write-Host "  - Or 'a' for all scripts"
Write-Host "  - Press Enter to cancel."
Write-Host ""

$selection = Read-Host "Selection"

if ([string]::IsNullOrWhiteSpace($selection)) {
    Write-Host "No selection made. Exiting."
    exit 0
}

$indices = @()

if ($selection.Trim().ToLower() -eq 'a') {
    $indices = 1..$scriptFiles.Count
} else {
    $tokens = $selection -split '[,\s]+' | Where-Object { $_ -ne "" }
    foreach ($t in $tokens) {
        $num = 0
        if ([int]::TryParse($t, [ref]$num)) {
            if ($num -ge 1 -and $num -le $scriptFiles.Count) {
                $indices += $num
            }
        }
    }
    $indices = $indices | Sort-Object -Unique
}

if ($indices.Count -eq 0) {
    Write-Host "No valid selections. Exiting."
    exit 0
}

Write-Host ""
Write-Host "You selected:"
foreach ($i in $indices) {
    $file = $scriptFiles[$i-1]
    Write-Host ("  [{0}] {1}" -f $i, $file.Name)
}
Write-Host ""

# ---------------------------------------------------
# Choose host: pwsh.exe (preferred) or powershell.exe
# ---------------------------------------------------
$pwsh = Get-Command pwsh.exe -ErrorAction SilentlyContinue
if ($pwsh) {
    $HostExe = $pwsh.Source
} else {
    $ps = Get-Command powershell.exe -ErrorAction SilentlyContinue
    if (-not $ps) {
        Write-Host "ERROR: Neither pwsh.exe nor powershell.exe found in PATH." -ForegroundColor Red
        exit 1
    }
    $HostExe = $ps.Source
}

# ---------------------------------------------------
# Prepare Start Menu folder + COM object
# ---------------------------------------------------
$ShortcutFolder = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\DAGViewer"
if (-not (Test-Path $ShortcutFolder)) {
    New-Item -ItemType Directory -Path $ShortcutFolder -Force | Out-Null
}

$WScriptShell = New-Object -ComObject WScript.Shell

# ---------------------------------------------------
# For each selected script, ask for hotkey and create shortcut
# ---------------------------------------------------
Write-Host "Now assign a hotkey for each selected script."
Write-Host "Examples: CTRL+ALT+D, CTRL+SHIFT+F, CTRL+ALT+WIN+X"
Write-Host "Leave blank to skip binding that script."
Write-Host ""

foreach ($i in $indices) {
    $file = $scriptFiles[$i-1]
    $name = $file.Name
    $base = $file.BaseName
    $full = $file.FullName

    Write-Host "Script [$i]: $name"
    $inputHotkey = Read-Host "  Hotkey for this script (blank = skip)"

    if ([string]::IsNullOrWhiteSpace($inputHotkey)) {
        Write-Host "  Skipping $name (no hotkey)."
        Write-Host ""
        continue
    }

    $hotkey = $inputHotkey.Trim().ToUpper()

    $shortcutName = "DAGViewer - $base.lnk"
    $shortcutPath = Join-Path $ShortcutFolder $shortcutName

    $Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath       = $HostExe
    $Shortcut.Arguments        = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$full`""
    $Shortcut.WorkingDirectory = $ProjectRoot
    $Shortcut.WindowStyle      = 1
    $Shortcut.Description      = "DAGViewer hotkey for $name"
    $Shortcut.Hotkey           = $hotkey
    $Shortcut.Save()

    Write-Host "  Bound $name to hotkey: $hotkey"
    Write-Host "  Shortcut: $shortcutPath"
    Write-Host ""
}

Write-Host "----------------------------------------"
Write-Host " Hotkey binding complete"
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "You can re-run this script anytime to add/change bindings:"
Write-Host "  Codebase\Core\Hotkeys\bind_hotkeys.ps1"
Write-Host ""

exit 0
