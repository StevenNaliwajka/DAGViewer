#!/usr/bin/env bash
set -euo pipefail

# This script lives in: <project-root>/Codebase/Run
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

export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "Using python: $PYTHON_BIN"
echo "PYTHONPATH:   $PYTHONPATH"
echo

MODULE="Codebase.GUI.GUI.task_create_gui"

"$PYTHON_BIN" -m Codebase.GUI.Run.task_create_gui