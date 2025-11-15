#!/usr/bin/env bash
set -euo pipefail

# Location of this script (Codebase/Setup)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root: go up two levels from Codebase/Setup
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"

# Virtual environment directory
VENV_DIR="$PROJECT_ROOT/.venv"

# Unified JSON requirements file
REQ_JSON="$SCRIPT_DIR/requirements.json"

echo "Script dir:      $SCRIPT_DIR"
echo "Project root:    $PROJECT_ROOT"
echo "Virtualenv dir:  $VENV_DIR"
echo "Requirements:    $REQ_JSON"
echo

# Sanity checks
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed or not in PATH."
    exit 1
fi

if [ ! -f "$REQ_JSON" ]; then
    echo "ERROR: requirements.json not found at: $REQ_JSON"
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists, reusing it."
fi

# Activate venv
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

#######################################
# Helper: read pip list from JSON
# - Accepts formats:
#   * {"pip": ["pkg1", "pkg2"]}
#   * {"packages": ["pkg1", "pkg2"]}   (legacy)
#   * ["pkg1", "pkg2"]                 (legacy: whole file is list)
#######################################
read_pip_list() {
    REQ_JSON="$REQ_JSON" python3 << 'PY'
import json, os, sys, pathlib

path = pathlib.Path(os.environ["REQ_JSON"])

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

pip_list = []

if isinstance(data, list):
    pip_list = data
elif isinstance(data, dict):
    if "pip" in data:
        pip_list = data["pip"]
    elif "packages" in data:
        pip_list = data["packages"]
    else:
        pip_list = []
else:
    print(f"ERROR: {path} must be a list or object.", file=sys.stderr)
    sys.exit(1)

if not isinstance(pip_list, list):
    print(f"ERROR: 'pip'/'packages' must be a list.", file=sys.stderr)
    sys.exit(1)

print("\n".join(str(p) for p in pip_list))
PY
}

#######################################
# Helper: read system list from JSON
# - Uses top-level "system": [...]
#######################################
read_system_list() {
    REQ_JSON="$REQ_JSON" python3 << 'PY'
import json, os, sys, pathlib

path = pathlib.Path(os.environ["REQ_JSON"])

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

sys_list = []

if isinstance(data, dict):
    sys_list = data.get("system", [])
elif isinstance(data, list):
    # If entire file is a list, treat it as pip-only; no system deps
    sys_list = []
else:
    print(f"ERROR: {path} must be a list or object.", file=sys.stderr)
    sys.exit(1)

if not isinstance(sys_list, list):
    print(f"ERROR: 'system' must be a list if present.", file=sys.stderr)
    sys.exit(1)

print("\n".join(str(p) for p in sys_list))
PY
}

#######################################
# 1) PIP PACKAGES
#######################################
echo "Parsing pip requirements..."
PIP_PKGS="$(read_pip_list || true)"

if [ -z "${PIP_PKGS:-}" ]; then
    echo "No pip packages found; skipping pip install."
else
    echo "Installing pip packages:"
    printf '  %s\n' $PIP_PKGS
    # shellcheck disable=SC2086
    pip install $PIP_PKGS
fi

#######################################
# 2) SYSTEM PACKAGES (APT, WITH PROMPT)
#######################################
echo
echo "Parsing system requirements..."
SYS_PKGS="$(read_system_list || true)"

if [ -z "${SYS_PKGS:-}" ]; then
    echo "No system (apt) requirements listed."
else
    echo "System packages required:"
    printf '  %s\n' $SYS_PKGS
    echo

    if command -v apt-get >/dev/null 2>&1; then
        # Ask user for permission before sudo install
        read -r -p "Attempt to install these packages with sudo apt-get now? [y/N] " reply
        case "$reply" in
            [yY][eE][sS]|[yY])
                echo "Installing system packages via apt-get..."
                sudo apt-get update
                # shellcheck disable=SC2086
                sudo apt-get install -y $SYS_PKGS
                ;;
            *)
                echo "Skipping automatic system package installation."
                echo "You can install them manually with:"
                echo "  sudo apt-get update"
                echo "  sudo apt-get install $SYS_PKGS"
                ;;
        esac
    else
        echo "NOTE: 'apt-get' not found; automatic system install is not supported on this OS."
        echo "Please install these packages manually using your system's package manager."
    fi
fi

echo
echo "Done! To use the environment later, run:"
echo "  source \"$VENV_DIR/bin/activate\""
