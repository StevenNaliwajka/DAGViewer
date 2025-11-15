#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from Codebase.Object import task
from Codebase.FileIO.create_task_file import create_task_file

try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None


# ---- Geometry save/load config ----
SCRIPT_DIR = Path(__file__).resolve().parent      # .../Codebase/GUI
CODEBASE_DIR = SCRIPT_DIR.parent                  # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                # .../ (DAGViewer)
USERDATA_DIR = PROJECT_ROOT / "UserData"          # .../UserData
GEOM_FILE = USERDATA_DIR / ".task_gui_geometry"   # stored in UserData



def task(name: str, description: str, group: str) -> dict:
    """
    Factory for a task object.
    """
    return {
        "task": name,
        "description": description,
        "group": group,
    }


def on_create():
    name = entry_task.get().strip()
    desc = entry_description.get().strip()
    grp = entry_group.get().strip()

    # Optionally: basic validation
    if not name:
        messagebox.showerror("Missing Task", "Please enter a task name.")
        entry_task.focus_set()
        return

    # build Task object
    t = task(name, desc, grp)

    # create file
    path = create_task_file(t)
    print(f"Task file created at: {path}")

    # Clear fields (keep Group if you want)
    entry_task.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    # entry_group.delete(0, tk.END)

    entry_task.focus_set()


def maybe_submit(event=None):
    """
    If all three fields have text, act like the Create button was pressed.
    Triggered on ANY Enter keypress in the window.
    """
    if (
        entry_task.get().strip()
        and entry_description.get().strip()
        and entry_group.get().strip()
    ):
        on_create()
        return "break"  # stop further handling (prevents bell / default behavior)


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


def load_last_geometry(win: tk.Tk) -> bool:
    """
    Try to load the last saved geometry from GEOM_FILE (in UserData/).
    Returns True if applied, False if not.
    """
    try:
        if GEOM_FILE.exists():
            geom = GEOM_FILE.read_text(encoding="utf-8").strip()
            if geom:
                win.geometry(geom)  # "300x150+100+100"
                return True
    except OSError:
        pass
    return False


def save_geometry(win: tk.Tk) -> None:
    """
    Save the current window geometry to GEOM_FILE (in UserData/).
    """
    try:
        USERDATA_DIR.mkdir(parents=True, exist_ok=True)
        geom = win.geometry()
        GEOM_FILE.write_text(geom, encoding="utf-8")
    except OSError:
        pass


if __name__ == "__main__":
    # Root window
    root = tk.Tk()
    root.title("Create Task")

    # Main frame
    main_frame = ttk.Frame(root, padding=20)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Labels + entries
    ttk.Label(main_frame, text="Task:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
    entry_task = ttk.Entry(main_frame, width=40)
    entry_task.grid(row=0, column=1, sticky="w", pady=5, padx=5)

    ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
    entry_description = ttk.Entry(main_frame, width=40)
    entry_description.grid(row=1, column=1, sticky="w", pady=5, padx=5)

    ttk.Label(main_frame, text="Group:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
    entry_group = ttk.Entry(main_frame, width=40)
    entry_group.grid(row=2, column=1, sticky="w", pady=5, padx=5)

    # Create button
    create_button = ttk.Button(main_frame, text="Create", command=on_create)
    create_button.grid(row=3, column=0, columnspan=2, pady=(15, 0))

    # Global Enter binding: if all fields filled, act like Create
    root.bind_all("<Return>", maybe_submit)

    # Initial focus on Task field
    entry_task.focus_set()

    # Make window a bit nicer
    root.resizable(False, False)

    # ---- Apply geometry: load last if present, else center once ----
    if not load_last_geometry(root):
        center_on_current_monitor(root)

    # ---- Save geometry on close ----
    def on_close():
        save_geometry(root)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # ---- ESCAPE closes instantly, anywhere ----
    def on_escape(event=None):
        on_close()
        return "break"

    root.bind_all("<Escape>", on_escape)

    root.mainloop()
