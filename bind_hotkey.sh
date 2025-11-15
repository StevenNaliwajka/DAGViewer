#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# Settings / paths
# -------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"

# Put the xbindkeys config under project-root/UserData:
USERDATA_DIR="$SCRIPT_DIR/UserData"
XBINDSRC="$USERDATA_DIR/.xbindkeysrc"

# Ensure UserData exists
mkdir -p "$USERDATA_DIR"

# -------------------------------
# Sanity checks
# -------------------------------
if [[ ! -f "$RUN_SCRIPT" ]]; then
    echo "Error: run.sh not found next to bind_hotkey.sh."
    echo "Expected here: $RUN_SCRIPT"
    exit 1
fi

if [[ ! -x "$RUN_SCRIPT" ]]; then
    echo "run.sh is not executable. Making it executable..."
    chmod +x "$RUN_SCRIPT"
fi

if ! command -v xbindkeys >/dev/null 2>&1; then
    echo "xbindkeys is not installed."
    read -rp "Install xbindkeys with sudo apt install xbindkeys? [y/N] " ans
    ans="${ans:-n}"
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        sudo apt update
        sudo apt install -y xbindkeys
    else
        echo "Cannot continue without xbindkeys."
        exit 1
    fi
fi

# -------------------------------
# Ask for key combo
# -------------------------------
cat <<EOF
Enter the key combination to bind to run.sh.

Examples (xbindkeys format):
  "Control+Alt + r"
  "Mod4 + r"           (Super/Windows key + r)
  "Shift+Control + F12"

NOTE:
- The part before '+' are modifiers (Control, Shift, Alt, Mod4, etc).
- The last token after '+' is the main key (r, F12, etc).

EOF

read -rp "Key combination: " HOTKEY

if [[ -z "${HOTKEY// }" ]]; then
    echo "No key combination entered. Aborting."
    exit 1
fi

# -------------------------------
# Append binding to project UserData/.xbindkeysrc
# -------------------------------
echo
echo "Adding binding to $XBINDSRC ..."
{
    echo
    echo "# Launch run.sh from DAGViewer"
    echo "\"$RUN_SCRIPT\""
    echo "  $HOTKEY"
} >> "$XBINDSRC"

# -------------------------------
# Restart xbindkeys with this config
# -------------------------------
echo "Restarting xbindkeys with config: $XBINDSRC"

# Kill any existing xbindkeys
if pgrep -x xbindkeys >/dev/null 2>&1; then
    pkill xbindkeys || true
fi

# Start xbindkeys using this specific config file
xbindkeys -f "$XBINDSRC" &

echo
echo "Done!"
echo "Key combination '$HOTKEY' is now bound to:"
echo "  $RUN_SCRIPT"
echo
echo "Config is stored at:"
echo "  $XBINDSRC"
echo
echo "If it doesn’t work, make sure:"
echo "  - You are using X11 (xbindkeys does not work on Wayland)."
echo "  - xbindkeys is running (this script just started it)."
