#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox

from Codebase.Object import task
from Codebase.FileIO.create_task_file import create_task_file

from Codebase.GUI.gui_profile import (
    TASK_GEOM_FILE,
    center_on_current_monitor,
    load_last_geometry,
    save_geometry,
    bind_escape_to_close,
    bind_submit_on_enter,
)


def task_factory(name: str, description: str, group: str) -> dict:
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

    # Validation:
    # - Task is required
    # - Group is required
    # - Description is allowed to be blank
    if not name:
        messagebox.showerror("Missing Task", "Please enter a task name.")
        entry_task.focus_set()
        return

    if not grp:
        messagebox.showerror("Missing Group", "Please enter a group.")
        entry_group.focus_set()
        return

    # build Task object
    t = task_factory(name, desc, grp)

    # create file
    path = create_task_file(t)
    print(f"Task file created at: {path}")

    # Clear fields (keep Group if you want)
    entry_task.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    # entry_group.delete(0, tk.END)

    entry_task.focus_set()


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

    # Initial focus on Task field
    entry_task.focus_set()

    # Make window a bit nicer
    root.resizable(False, False)

    # ---- Geometry: load last if present, else center once ----
    if not load_last_geometry(root, TASK_GEOM_FILE):
        center_on_current_monitor(root)

    # ---- Close behavior (WM + ESC) ----
    def on_close():
        save_geometry(root, TASK_GEOM_FILE)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    # ---- Global ENTER: submit when Task & Group filled ----
    def can_submit():
        return bool(entry_task.get().strip() and entry_group.get().strip())

    bind_submit_on_enter(root, can_submit, on_create)

    root.mainloop()
