#!/usr/bin/env python3
"""
Interactive DAG viewer for Task JSONs.

- Discovers Tasks/*.json
- Each JSON is one node
- Uses 'depends_on' list to create edges
- Displays nodes on a Tkinter Canvas
- Nodes are draggable; edges update in real time

Expected layout:

    DAGViewer/
      Codebase/
        GUI/
          dag_viewer.py   (this file)
      Tasks/
        AAAA1.json
        EEEE2.json
        ...

"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import tkinter as tk
from tkinter import ttk, messagebox

from Codebase.GUI.gui_profile import (
    DAG_GEOM_FILE,
    center_on_current_monitor,
    load_last_geometry,
    save_geometry,
    bind_escape_to_close,
)


# ---------------------------------------------------------------------------
# Path discovery
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent      # .../Codebase/GUI
CODEBASE_DIR = SCRIPT_DIR.parent                  # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                # .../

# Try both Codebase/Tasks and PROJECT_ROOT/Tasks
CANDIDATE_TASK_DIRS = [
    CODEBASE_DIR / "Tasks",
    PROJECT_ROOT / "Tasks",
]

TASKS_DIR: Optional[Path] = None
for c in CANDIDATE_TASK_DIRS:
    if c.is_dir():
        TASKS_DIR = c
        break

if TASKS_DIR is None:
    raise SystemExit(
        f"Could not find a Tasks folder in any of: "
        f"{', '.join(str(p) for p in CANDIDATE_TASK_DIRS)}"
    )

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TaskNode:
    key: str                      # e.g. filename stem like "EEEE1"
    label: str                    # human label, from "task" field
    file_path: Path
    depends_on_raw: List[str] = field(default_factory=list)
    group: Optional[str] = None
    id: Optional[int] = None

    # Filled later
    deps_resolved: List[str] = field(default_factory=list)   # keys this node depends on
    children: List[str] = field(default_factory=list)        # outgoing edges (this -> child)
    level: int = 0                                           # layout layer


def load_task_nodes(tasks_dir: Path) -> Dict[str, TaskNode]:
    """
    Load all *.json under tasks_dir and return key -> TaskNode.

    key is filename stem, e.g. "EEEE1" from EEEE1.json
    """
    nodes: Dict[str, TaskNode] = {}

    for json_file in sorted(tasks_dir.glob("*.json")):
        try:
            data = json.loads(json_file.read_text())
        except Exception as e:
            print(f"Warning: could not read {json_file}: {e}")
            continue

        key = json_file.stem
        label = data.get("task", key)
        group = data.get("group")
        node_id = data.get("id")

        depends_on = data.get("depends_on", [])
        if not isinstance(depends_on, list):
            depends_on = []

        nodes[key] = TaskNode(
            key=key,
            label=label,
            file_path=json_file,
            depends_on_raw=depends_on,
            group=group,
            id=node_id,
        )

    print(f"Loaded {len(nodes)} tasks from {tasks_dir}")
    return nodes


def resolve_dependencies(nodes: Dict[str, TaskNode]) -> None:
    """
    For each TaskNode, map depends_on_raw (strings) to actual node keys.

    We try several interpretations:
    - exact match of filename stem (key)
    - match of 'task' label
    - match of group+id string
    """
    label_to_keys: Dict[str, List[str]] = {}
    groupid_to_key: Dict[str, str] = {}

    for key, node in nodes.items():
        label_to_keys.setdefault(node.label, []).append(key)
        if node.group is not None and node.id is not None:
            groupid_to_key[f"{node.group}{node.id}"] = key

    for key, node in nodes.items():
        resolved: List[str] = []
        for dep_str in node.depends_on_raw:
            dep_key: Optional[str] = None

            # 1) direct key match (e.g. "EEEE1")
            if dep_str in nodes:
                dep_key = dep_str

            # 2) match by group+id (e.g. "EEEE1")
            if dep_key is None:
                maybe = groupid_to_key.get(dep_str)
                if maybe is not None:
                    dep_key = maybe

            # 3) match by label (task name)
            if dep_key is None:
                candidates = label_to_keys.get(dep_str, [])
                if candidates:
                    dep_key = candidates[0]   # pick first if multiple

            if dep_key is not None and dep_key in nodes:
                resolved.append(dep_key)
            else:
                print(
                    f"Warning: for node {key}, dependency '{dep_str}' "
                    f"could not be resolved."
                )

        node.deps_resolved = resolved

    # Fill children (reverse edges)
    for key, node in nodes.items():
        for dep_key in node.deps_resolved:
            if dep_key in nodes:
                nodes[dep_key].children.append(key)


def compute_levels(nodes: Dict[str, TaskNode]) -> None:
    """
    Assign an integer 'level' to each node using a simple longest-path-from-sources
    algorithm on the DAG.
    """
    # indegree based on deps_resolved edges (dep -> node)
    indegree = {k: 0 for k in nodes}
    for node in nodes.values():
        for dep_key in node.deps_resolved:
            if dep_key in indegree:
                indegree[node.key] += 1

    # Kahn's algorithm with level propagation
    queue = [k for k, deg in indegree.items() if deg == 0]
    for k in queue:
        nodes[k].level = 0

    while queue:
        cur = queue.pop(0)
        cur_level = nodes[cur].level
        for child in nodes[cur].children:
            if child not in indegree:
                continue
            indegree[child] -= 1
            # Update child's level as max of all predecessors + 1
            nodes[child].level = max(nodes[child].level, cur_level + 1)
            if indegree[child] == 0:
                queue.append(child)

# ---------------------------------------------------------------------------
# Canvas + interaction
# ---------------------------------------------------------------------------

class DAGCanvas(tk.Canvas):
    """
    Tkinter Canvas subclass for drawing and interacting with the DAG.
    """

    def __init__(self, master, nodes: Dict[str, TaskNode], **kwargs):
        super().__init__(master, **kwargs)

        self.nodes = nodes

        # key -> {'rect': int, 'text': int}
        self.node_items: Dict[str, Dict[str, int]] = {}

        # list of edges: {'src': key, 'dst': key, 'line': int}
        self.edge_items: List[Dict[str, object]] = []

        # Drag state
        self._drag_data = {
            "node_key": None,
            "x": 0,
            "y": 0,
        }

        self.configure(background="white")

        # Mouse bindings
        self.bind("<ButtonPress-1>", self._on_button_press)
        self.bind("<B1-Motion>", self._on_button_motion)
        self.bind("<ButtonRelease-1>", self._on_button_release)
        self.bind("<Double-1>", self._on_double_click)

        # Optional scroll wheel (vertical)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", self._on_mousewheel)  # some Linux
        self.bind("<Button-5>", self._on_mousewheel)

        self.draw_graph()

    # -------------------------
    # Layout & drawing
    # -------------------------

    def draw_graph(self) -> None:
        """
        Compute initial layout and draw nodes + edges.
        """
        self.delete("all")
        self.node_items.clear()
        self.edge_items.clear()

        # Group nodes by level
        level_to_keys: Dict[int, List[str]] = {}
        for key, node in self.nodes.items():
            level_to_keys.setdefault(node.level, []).append(key)

        # Simple grid layout
        x_spacing = 180
        y_spacing = 120
        node_width = 140
        node_height = 50
        y_start = 80
        x_margin = 100

        max_x = 0
        max_y = 0

        for level in sorted(level_to_keys.keys()):
            keys = level_to_keys[level]
            count = len(keys)
            # center them in a row
            row_width = (count - 1) * x_spacing
            x0 = x_margin

            y = y_start + level * y_spacing

            for i, key in enumerate(keys):
                x = x0 + i * x_spacing

                x1 = x - node_width / 2
                y1 = y - node_height / 2
                x2 = x + node_width / 2
                y2 = y + node_height / 2

                rect = self.create_rectangle(
                    x1, y1, x2, y2,
                    outline="black",
                    fill="#f0f0ff",
                    width=2,
                    tags=("node", key),
                )
                text = self.create_text(
                    x,
                    y,
                    text=self.nodes[key].label,
                    tags=("label", key),
                )

                self.node_items[key] = {"rect": rect, "text": text}

                max_x = max(max_x, x2 + 50)
                max_y = max(max_y, y2 + 50)

        # Draw edges after all nodes are positioned
        self._draw_edges()

        # Set scroll region
        self.config(scrollregion=(0, 0, max_x, max_y))

    def _draw_edges(self) -> None:
        self.edge_items.clear()
        for key, node in self.nodes.items():
            # edges from dep -> node.key
            for dep_key in node.deps_resolved:
                if dep_key not in self.node_items or key not in self.node_items:
                    continue

                src_center = self._get_node_center(dep_key)
                dst_center = self._get_node_center(key)

                line = self.create_line(
                    *src_center,
                    *dst_center,
                    arrow=tk.LAST,
                    width=2,
                )
                self.edge_items.append({"src": dep_key, "dst": key, "line": line})

    def _update_edges(self) -> None:
        """
        Update all edge line coordinates based on node positions.
        """
        for edge in self.edge_items:
            src = edge["src"]
            dst = edge["dst"]
            line_id = edge["line"]
            if src not in self.node_items or dst not in self.node_items:
                continue
            x1, y1 = self._get_node_center(src)
            x2, y2 = self._get_node_center(dst)
            self.coords(line_id, x1, y1, x2, y2)

    def _get_node_center(self, key: str) -> Tuple[float, float]:
        rect_id = self.node_items[key]["rect"]
        x1, y1, x2, y2 = self.coords(rect_id)
        return (x1 + x2) / 2.0, (y1 + y2) / 2.0

    # -------------------------
    # Interaction handlers
    # -------------------------

    def _find_node_key_from_item(self, item_id: int) -> Optional[str]:
        tags = self.gettags(item_id)
        # we tagged each node and label with the node key
        for t in tags:
            if t in self.nodes:
                return t
        return None

    def _on_button_press(self, event):
        # what item did we click?
        item = self.find_closest(event.x, event.y)
        if not item:
            return
        item_id = item[0]

        key = self._find_node_key_from_item(item_id)
        if key is None:
            return

        self._drag_data["node_key"] = key
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_button_motion(self, event):
        key = self._drag_data["node_key"]
        if key is None:
            return

        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        rect_id = self.node_items[key]["rect"]
        text_id = self.node_items[key]["text"]

        self.move(rect_id, dx, dy)
        self.move(text_id, dx, dy)

        # update connected edges
        self._update_edges()

    def _on_button_release(self, event):
        self._drag_data["node_key"] = None

    def _on_double_click(self, event):
        item = self.find_closest(event.x, event.y)
        if not item:
            return
        item_id = item[0]
        key = self._find_node_key_from_item(item_id)
        if key is None:
            return

        node = self.nodes[key]
        info = [
            f"Key: {node.key}",
            f"Label: {node.label}",
            f"File: {node.file_path.name}",
            f"Group: {node.group}",
            f"ID: {node.id}",
            "",
            f"Depends on: {', '.join(node.deps_resolved) if node.deps_resolved else '(none)'}",
            f"Children: {', '.join(node.children) if node.children else '(none)'}",
        ]
        messagebox.showinfo("Task info", "\n".join(info))

    def _on_mousewheel(self, event):
        # Windows / most Linux: event.delta; some X11 use Button-4/5 with delta fixed
        if event.num == 4 or event.delta > 0:
            self.yview_scroll(-2, "units")
        else:
            self.yview_scroll(2, "units")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    nodes = load_task_nodes(TASKS_DIR)
    if not nodes:
        print(f"No task JSON files found in {TASKS_DIR}")
        return

    resolve_dependencies(nodes)
    compute_levels(nodes)

    root = tk.Tk()
    root.title("DAG Viewer")

    # Default size (used for the very first run)
    root.geometry("1000x700")

    # Geometry: load last if present, else center once
    if not load_last_geometry(root, DAG_GEOM_FILE):
        center_on_current_monitor(root)

    # Close behavior (WM + ESC)
    def on_close():
        save_geometry(root, DAG_GEOM_FILE)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    bind_escape_to_close(root, on_close)

    canvas = DAGCanvas(root, nodes, width=1000, height=700)
    canvas.pack(fill="both", expand=True)

    root.mainloop()



if __name__ == "__main__":
    main()
