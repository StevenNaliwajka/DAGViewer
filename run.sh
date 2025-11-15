#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------
# Paths
# ---------------------------------------
# This script lives in the project root: DAGViewer/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

CODEBASE_DIR="$PROJECT_ROOT/Codebase"
RUN_DIR="$CODEBASE_DIR"

# bind_hotkey.sh lives next to run.sh in project root
BIND_HOTKEY="$CODEBASE_DIR/Core/Setup/bind_hotkey.sh"

# These live under Codebase/Run
CREATE_TASK="$RUN_DIR/create_task.sh"
VIEW_DAG="$RUN_DIR/view_dag.sh"

# UserData matches ProjectPaths.userdata (ProjectRoot/UserData)
USERDATA_DIR="$PROJECT_ROOT/UserData"
PREFS_FILE="$USERDATA_DIR/.run_prefs"

mkdir -p "$USERDATA_DIR"

# Default prefs
SHOW_INTRO=1

# Load prefs if present
if [[ -f "$PREFS_FILE" ]]; then
    # shellcheck source=/dev/null
    source "$PREFS_FILE"
fi

# ---------------------------------------
# Helper to run a script (auto-chmod if needed)
# ---------------------------------------
run_script() {
    local path="$1"
    local label="$2"

    if [[ ! -f "$path" ]]; then
        echo "Error: $label script not found at:"
        echo "  $path"
        exit 1
    fi

    if [[ ! -x "$path" ]]; then
        echo "$label script is not executable. Making it executable..."
        chmod +x "$path"
    fi

    "$path"
}

# ---------------------------------------
# Intro text
# ---------------------------------------
if [[ "${SHOW_INTRO:-1}" -eq 1 ]]; then
    cat <<'EOF'
===================== DAGViewer =====================

DAGViewer is a small toolkit for managing "Tasks" and
visualizing them as a Directed Acyclic Graph (DAG).

You can use it in three main ways:

  1) bind_hotkey.sh (recommended)
     - Sets up a global hotkey (via xbindkeys) that
       launches the "Create Task" GUI.
     - This gives you a commandless, quick-entry
       workflow: press the hotkey, make a task, done.

  2) create_task.sh
     - Launches the "Create Task" GUI directly.
     - Lets you create a new Task JSON in Tasks/.

  3) view_dag.sh
     - Launches the DAG viewer.
     - Discovers Tasks/*.json and plots them so you
       can inspect and interact with your task graph.

You can also run those scripts manually:

  ./bind_hotkey.sh          (project root)
  Codebase/Run/create_task.sh
  Codebase/Run/view_dag.sh

=====================================================
EOF
    echo
fi

# ---------------------------------------
# Menu
# ---------------------------------------
echo "What would you like to do?"
echo "  1) Bind global hotkey (recommended)"
echo "  2) Create a task"
echo "  3) View DAG"
echo "  q) Quit"
echo

read -rp "Enter choice [1/2/3/q]: " choice

case "$choice" in
    1)
        run_script "$BIND_HOTKEY" "bind_hotkey.sh"
        ;;
    2)
        run_script "$CREATE_TASK" "create_task.sh"
        ;;
    3)
        run_script "$VIEW_DAG" "view_dag.sh"
        ;;
    q|Q)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Unknown choice: $choice"
        exit 1
        ;;
esac

echo

# ---------------------------------------
# Ask whether to hide intro next time
# ---------------------------------------
if [[ "${SHOW_INTRO:-1}" -eq 1 ]]; then
    echo "If you want to skip the long explanation next time,"
    echo "type '1' now. Press Enter to keep seeing it."
    read -rp "Skip intro in future? [1 = yes / Enter = no]: " skip

    if [[ "$skip" == "1" ]]; then
        echo "SHOW_INTRO=0" > "$PREFS_FILE"
        echo "Okay, intro will be skipped next time."
    else
        echo "SHOW_INTRO=1" > "$PREFS_FILE"
    fi
fi
