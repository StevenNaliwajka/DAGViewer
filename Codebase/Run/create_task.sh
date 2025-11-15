#!/usr/bin/env bash
set -euo pipefail

# Location of this script (project root: DAGViewer)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Error: virtual environment not found at:"
    echo "  $VENV_DIR"
    echo "Run ./setup.sh first to create it."
    exit 1
fi

cd "$PROJECT_ROOT"

# Make sure the project root is on PYTHONPATH so 'Codebase' can be imported
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Run the GUI as a module
exec "$PYTHON_BIN" -m Codebase.GUI.task_create_gui "$@"
