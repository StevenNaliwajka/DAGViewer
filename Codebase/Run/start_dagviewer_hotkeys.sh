#!/usr/bin/env bash
set -euo pipefail

# This script lives in: <project-root>/Codebase/Run/start_dagviewer_hotkeys.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
USERDATA_DIR="$PROJECT_ROOT/UserData"
XBINDSRC="$USERDATA_DIR/.xbindkeysrc"

# If xbindkeys isn't installed, just exit quietly
if ! command -v xbindkeys >/dev/null 2>&1; then
    exit 0
fi

# Kill any existing instance so we don't stack them
if pgrep -x xbindkeys >/dev/null 2>&1; then
    pkill xbindkeys || true
fi

# Start xbindkeys with the project's config
exec xbindkeys -f "$XBINDSRC"
