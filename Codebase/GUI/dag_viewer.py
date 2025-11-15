#!/usr/bin/env python3
"""
Interactive DAG viewer for Task JSONs.

This module is a thin entrypoint that wires together:

- Paths:    Codebase.Core.Pathing.project_paths.ProjectPaths
- IO:       Codebase.GUI.IO.task_loader
- Logic:    Codebase.GUI.Logic.dag_builder
- GUI:      Codebase.GUI.GUI.dag_canvas + gui_profile
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, TYPE_CHECKING
import tkinter as tk

from Codebase.Core.Pathing.get_project_root import get_project_root
# --- Central path config ------------------------------------
from Codebase.Core.Pathing.project_paths import ProjectPaths, add_to_sys_path
from Codebase.GUI.GUI.Bind.bind_escape_to_close import bind_escape_to_close
from Codebase.GUI.GUI.Geometry.load_last_geometry import load_last_geometry
from Codebase.GUI.GUI.Geometry.save_geometry import save_geometry
from Codebase.GUI.GUI.Style.get_group_styles import get_group_styles
from Codebase.GUI.GUI.Style.set_group_visible import set_group_visible
from Codebase.GUI.GUI.Tool.center_on_current_monitor import center_on_current_monitor

# Make sure project_root / Codebase are on sys.path even if launched oddly
add_to_sys_path()

# --- Project imports ----------------------------------------
from Codebase.GUI.GUI.dag_canvas import DAGCanvas
from Codebase.GUI.Logic.dag_builder import build_dag


def main() -> None:
    # Use the central path definition for Tasks
    tasks_dir: Path = ProjectPaths.tasks

    if not tasks_dir.is_dir():
        print(f"[DAGViewer] Tasks directory not found at:\n  {tasks_dir}")
        print("Create it, or adjust ProjectPaths.tasks / project_paths.json.")
        return

    # Mapping of node_id -> TaskNode
    # (TaskNode is only needed for typing; at runtime this is just a dict)
    nodes: Dict[str, "TaskNode"] = build_dag(tasks_dir)

    if not nodes:
        print(f"[DAGViewer] No task JSON files found in {tasks_dir}")
        return

    root = tk.Tk()
    root.title("DAG Viewer")

    # Default size
    root.geometry("1000x700")

    proj_root = get_project_root()
    dag_geometry_file = proj_root/"UserData"/".dag_geom_file"

    # Geometry: load last if present, else center once
    if not load_last_geometry(root, dag_geometry_file):
        center_on_current_monitor(root)

    # Close behavior (WM + ESC)
    def on_close() -> None:
        save_geometry(root, dag_geometry_file)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    # ---- Main layout: canvas + right-side group filters ----
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Canvas on the left
    canvas = DAGCanvas(main_frame, nodes, width=1000, height=700)
    canvas.pack(side="left", fill="both", expand=True)

    # Sidebar on the right for group toggles
    sidebar = tk.Frame(main_frame, padx=8, pady=8, relief="groove", borderwidth=2)
    sidebar.pack(side="right", fill="y")

    tk.Label(
        sidebar,
        text="Groups",
        font=("TkDefaultFont", 10, "bold"),
    ).pack(anchor="nw", pady=(0, 4))

    group_styles = get_group_styles(canvas)
    group_vars: dict[str, tk.BooleanVar] = {}

    def on_toggle(group: str) -> None:
        visible = group_vars[group].get()
        set_group_visible(canvas, group, visible)

    # One row per group: color swatch + checkbox
    for group, (color, visible) in sorted(group_styles.items()):
        row = tk.Frame(sidebar)
        row.pack(fill="x", anchor="nw", pady=2)

        swatch = tk.Label(
            row,
            width=2,
            background=color,
            relief="solid",
            borderwidth=1,
        )
        swatch.pack(side="left", padx=(0, 4))

        var = tk.BooleanVar(value=visible)
        group_vars[group] = var

        cb = tk.Checkbutton(
            row,
            text=group,
            variable=var,
            command=lambda g=group: on_toggle(g),
            anchor="w",
        )
        cb.pack(side="left", fill="x", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
