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

# --- Central path config ------------------------------------
from Codebase.Core.Pathing.project_paths import ProjectPaths, add_to_sys_path

# Make sure project_root / Codebase are on sys.path even if launched oddly
add_to_sys_path()

# --- Project imports ----------------------------------------
from Codebase.GUI.GUI.dag_canvas import DAGCanvas
from Codebase.GUI.Logic.dag_builder import build_dag
from Codebase.GUI.GUI.gui_profile import (
    DAG_GEOM_FILE,
    load_last_geometry,
    center_on_current_monitor,
    save_geometry,
    bind_escape_to_close,
)

# Only for type checking / IDEs; NOT run at runtime
if TYPE_CHECKING:
    # If/when you actually create this module, this will type-check nicely.
    # Until then, you can comment this out; it's not required to run.
    from Codebase.Model.task_node import TaskNode


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

    # Geometry: load last if present, else center once
    if not load_last_geometry(root, DAG_GEOM_FILE):
        center_on_current_monitor(root)

    # Close behavior (WM + ESC)
    def on_close() -> None:
        save_geometry(root, DAG_GEOM_FILE)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    canvas = DAGCanvas(root, nodes, width=1000, height=700)
    canvas.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
