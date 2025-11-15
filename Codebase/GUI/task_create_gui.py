#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox

from Codebase.FileIO.create_task_file import create_task_file
from Codebase.GUI.GUI.Bind.bind_submit_on_enter import bind_submit_on_enter
from Codebase.GUI.GUI.Bind.bind_escape_to_close import bind_escape_to_close


def task_factory(name: str, description: str, group: str) -> dict:
    return {
        "task": name,
        "description": description,
        "group": group,
    }


def build_task_create_window(root: tk.Tk):
    """
    Build the 'Create Task' UI inside root and return a small view model
    (entries + button handlers).
    """

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

    def on_create():
        name = entry_task.get().strip()
        desc = entry_description.get().strip()
        grp = entry_group.get().strip()

        # Task required; Group required; Description can be blank. :contentReference[oaicite:13]{index=13}
        if not name:
            messagebox.showerror("Missing Task", "Please enter a task name.")
            entry_task.focus_set()
            return

        if not grp:
            messagebox.showerror("Missing Group", "Please enter a group.")
            entry_group.focus_set()
            return

        t = task_factory(name, desc, grp)
        path = create_task_file(t)
        print(f"Task file created at: {path}")

        entry_task.delete(0, tk.END)
        entry_description.delete(0, tk.END)
        entry_task.focus_set()

    create_button = ttk.Button(main_frame, text="Create", command=on_create)
    create_button.grid(row=3, column=0, columnspan=2, pady=(15, 0))

    entry_task.focus_set()

    def can_submit():
        return bool(entry_task.get().strip() and entry_group.get().strip())

    bind_submit_on_enter(root, can_submit, on_create)

    return {
        "entry_task": entry_task,
        "entry_description": entry_description,
        "entry_group": entry_group,
        "on_create": on_create,
    }


def main():
    root = tk.Tk()
    root.title("Create Task")
    root.resizable(False, False)

    build_task_create_window(root)




    on_close = None
    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    root.mainloop()


if __name__ == "__main__":
    main()

