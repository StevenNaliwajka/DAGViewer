#!/usr/bin/env python3
"""
Interactive DAG viewer for Task JSONs.

This module is a thin entrypoint that wires together:

- IO:       Codebase.GUI.IO.tasks_dir / task_loader
- Logic:    Codebase.GUI.Logic.dag_builder
- GUI:      Codebase.GUI.GUI.dag_canvas + gui_profile
- Run:      Codebase.GUI.Run.dag_viewer (this file)
"""
from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk


# -------------------------------------------------
# Support BOTH:
#   - python -m Codebase.GUI.Run.dag_viewer   (package mode)
#   - python Codebase/GUI/Run/dag_viewer.py   (script mode)
# -------------------------------------------------
if __name__ == "__main__" and __package__ is None:
    # Running as a plain script -> add project root to sys.path
    SCRIPT_DIR = Path(__file__).resolve().parent          # .../Codebase/GUI/Run
    PROJECT_ROOT = SCRIPT_DIR.parents[2]                  # .../ (DAGViewer)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    # Use absolute imports when run as a script
    from Codebase.GUI.IO.tasks_dir import find_tasks_dir
    from Codebase.GUI.IO.task_loader import load_task_nodes
else:
    # Normal package execution ('python -m Codebase.GUI.Run.dag_viewer')
    from ..IO.tasks_dir import find_tasks_dir
    from ..IO.task_loader import load_task_nodes

# Now your other imports are safe
from Codebase.GUI.Model.task_node import TaskNode
from Codebase.GUI.GUI.dag_canvas import DAGCanvas
from Codebase.GUI.Logic.dag_builder import build_dag
from Codebase.GUI.GUI.gui_profile import *

def main() -> None:
    try:
        tasks_dir: Path = find_tasks_dir()
    except RuntimeError as e:
        print(e)
        return

    nodes = build_dag(tasks_dir)
    if not nodes:
        print(f"No task JSON files found in {tasks_dir}")
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
