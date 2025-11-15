#!/usr/bin/env bash
set -euo pipefail

# This script lives in: <project-root>/Codebase/Run
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project root: go up two levels: Codebase/Run -> Codebase -> DAGViewer
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

echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "Using python: $PYTHON_BIN"
echo "PYTHONPATH:   $PYTHONPATH"
echo

# Run the DAG viewer Run as a module
"$PYTHON_BIN" -m Codebase.GUI.Run.dag_viewer
