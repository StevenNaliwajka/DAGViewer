#!/usr/bin/env python3
"""
Shared Run helpers:

- Geometry save/load for multiple windows
- Center-on-monitor logic
- Global ESC to close
- Global ENTER to trigger "submit" when fields are valid

Intended to be imported by:
- Codebase/Run/task_create_gui.py
- Codebase/Run/dag_viewer.py
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None


# -----------------------------
# Paths / geometry files
# -----------------------------

SCRIPT_DIR = Path(__file__).resolve().parent          # .../Codebase/Run
CODEBASE_DIR = SCRIPT_DIR.parent                      # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent.parent.parent                    # .../
USERDATA_DIR = PROJECT_ROOT / "UserData"              # .../UserData

# Make sure UserData exists (safe if already present)
USERDATA_DIR.mkdir(parents=True, exist_ok=True)

# Per-window geometry files
TASK_GEOM_FILE = USERDATA_DIR / ".task_gui_geometry"
DAG_GEOM_FILE = USERDATA_DIR / ".dag_viewer_geometry"


# -----------------------------
# Geometry helpers
# -----------------------------

def load_last_geometry(root: tk.Tk, geom_file: Path) -> bool:
    """
    If geom_file exists, read it and apply geometry to 'root'.
    Returns True if loaded, False otherwise.
    """
    try:
        if geom_file.is_file():
            geo = geom_file.read_text(encoding="utf-8").strip()
            if geo:
                root.geometry(geo)
                return True
    except Exception as e:
        print(f"Warning: could not load geometry from {geom_file}: {e}")
    return False


def save_geometry(root: tk.Tk, geom_file: Path) -> None:
    """
    Save the current geometry of 'root' into geom_file.
    """
    try:
        geom_file.write_text(root.winfo_geometry(), encoding="utf-8")
    except Exception as e:
        print(f"Warning: could not save geometry to {geom_file}: {e}")


def center_on_current_monitor(root: tk.Tk) -> None:
    """
    Center the window on the current monitor.

    - If screeninfo is available, use it to find the primary monitor.
    - Otherwise fallback to Tk's screen size and approximate center.
    """
    root.update_idletasks()  # ensure size info is current

    width = root.winfo_width()
    height = root.winfo_height()
    if width <= 1 or height <= 1:
        # If called before first draw, use a sensible default
        width, height = 800, 600

    if get_monitors:
        try:
            monitors = get_monitors()
            if monitors:
                # Simple choice: primary or first monitor
                mon = next((m for m in monitors if getattr(m, "is_primary", False)), monitors[0])
                screen_w = mon.width
                screen_h = mon.height
                offset_x = mon.x
                offset_y = mon.y
            else:
                screen_w = root.winfo_screenwidth()
                screen_h = root.winfo_screenheight()
                offset_x = 0
                offset_y = 0
        except Exception:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            offset_x = 0
            offset_y = 0
    else:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        offset_x = 0
        offset_y = 0

    x = offset_x + (screen_w - width) // 2
    y = offset_y + (screen_h - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")


# -----------------------------
# Keybind helpers
# -----------------------------

def bind_escape_to_close(root: tk.Tk, on_close) -> None:
    """
    Bind ESC so that pressing it anywhere closes the window immediately.

    'on_close' is typically a function that also saves geometry
    and calls root.destroy().
    """
    def _handler(event):
        on_close()

    # Bind on the toplevel AND globally inside it
    root.bind("<Escape>", _handler)
    root.bind_all("<Escape>", _handler)


def bind_submit_on_enter(root: tk.Tk, can_submit, on_submit) -> None:
    """
    Bind ENTER so that:

    - If can_submit() returns True, call on_submit().
    - Otherwise, let the normal focus/entry behavior happen.

    This is meant to be shared between UIs like the Task Create Run, etc.
    """

    def _handler(event):
        # Only trigger if user has filled in required fields
        try:
            if can_submit():
                on_submit()
                # Prevent default "ding" or focus changes
                return "break"
        except Exception as e:
            print(f"Error in can_submit/on_submit: {e}")
        # else allow normal behavior

    # Global within this application
    root.bind_all("<Return>", _handler)
