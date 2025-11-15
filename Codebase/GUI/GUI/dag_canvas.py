#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, List, Tuple, Optional

import tkinter as tk
from tkinter import messagebox

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class DAGCanvas(tk.Canvas):
    """
    Tkinter Canvas subclass for drawing and interacting with the DAG.

    Extracted from dag_viewer.py into a reusable widget. :contentReference[oaicite:8]{index=8}
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
        for t in tags:
            if t in self.nodes:
                return t
        return None

    def _on_button_press(self, event):
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
        if getattr(event, "num", None) == 4 or event.delta > 0:
            self.yview_scroll(-2, "units")
        else:
            self.yview_scroll(2, "units")


    @dataclass
    class TaskNode:
        """
        In-memory representation of a task JSON file.

        - key:   unique key, usually filename stem, e.g. "EEEE1"
        - label: display label, from "task" field in the JSON
        """
        key: str
        label: str
        file_path: Path
        depends_on_raw: List[str] = field(default_factory=list)
        group: Optional[str] = None
        id: Optional[int] = None

        # Resolved DAG fields (filled after loading)
        deps_resolved: List[str] = field(default_factory=list)   # keys this node depends on
        children: List[str] = field(default_factory=list)        # outgoing edges (this -> child)
        level: int = 0                                           # layout layer
