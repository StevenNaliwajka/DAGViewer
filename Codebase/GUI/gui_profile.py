#!/usr/bin/env python3
"""
Common GUI helpers for window geometry, UserData profile paths, and global keybinds.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None

# ---- Paths shared by all GUIs ----
SCRIPT_DIR = Path(__file__).resolve().parent      # .../Codebase/GUI
CODEBASE_DIR = SCRIPT_DIR.parent                  # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                # .../
USERDATA_DIR = PROJECT_ROOT / "UserData"          # .../UserData

# Geometry files per-window
TASK_GEOM_FILE = USERDATA_DIR / ".task_gui_geometry"
DAG_GEOM_FILE = USERDATA_DIR / ".dag_viewer_geometry"


def ensure_userdata_dir() -> None:
    USERDATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def center_on_current_monitor(win: tk.Tk) -> None:
    """
    Center the Tk window on the monitor where the mouse pointer currently is.
    Falls back to centering on the virtual screen if screeninfo is unavailable.
    """
    win.update_idletasks()

    window_width = win.winfo_width()
    window_height = win.winfo_height()

    # Fallback: just center on the virtual screen
    if get_monitors is None:
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        win.geometry(f"{window_width}x{window_height}+{x}+{y}")
        return

    # Get pointer (mouse) position in global coordinates
    pointer_x = win.winfo_pointerx()
    pointer_y = win.winfo_pointery()

    # Find the monitor that contains the pointer
    monitors = get_monitors()
    current = None
    for m in monitors:
        if (m.x <= pointer_x < m.x + m.width and
                m.y <= pointer_y < m.y + m.height):
            current = m
            break

    if current is None:
        current = monitors[0]  # fallback to first monitor

    # Center inside that monitor
    x = current.x + (current.width - window_width) // 2
    y = current.y + (current.height - window_height) // 2
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")


def load_last_geometry(win: tk.Tk, geom_file: Path) -> bool:
    """
    Try to load the last saved geometry from geom_file.
    Returns True if applied, False otherwise.
    """
    try:
        if geom_file.exists():
            geom = geom_file.read_text(encoding="utf-8").strip()
            if geom:
                win.geometry(geom)  # e.g. "1000x700+100+100"
                return True
    except OSError:
        pass
    return False


def save_geometry(win: tk.Tk, geom_file: Path) -> None:
    """
    Save the current window geometry to geom_file.
    """
    try:
        ensure_userdata_dir()
        geom = win.geometry()
        geom_file.write_text(geom, encoding="utf-8")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Keybind helpers
# ---------------------------------------------------------------------------

def bind_escape_to_close(root: tk.Tk, on_close) -> None:
    """
    Bind ESCAPE globally to immediately call on_close() and stop further handling.
    """

    def _on_escape(event=None):
        on_close()
        return "break"

    root.bind_all("<Escape>", _on_escape)


def bind_submit_on_enter(root: tk.Tk, can_submit, submit_callback) -> None:
    """
    Bind ENTER globally so that, if can_submit() returns True, submit_callback()
    is called and further handling is suppressed.

    can_submit: callable returning bool
    submit_callback: callable taking no args
    """

    def _maybe_submit(event=None):
        if can_submit():
            submit_callback()
            return "break"

    root.bind_all("<Return>", _maybe_submit)
