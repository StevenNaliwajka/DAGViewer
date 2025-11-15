#!/usr/bin/env python3
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ============================
# Relative imports (within Codebase.GUI.GUI)
# ============================

from .Draw.draw_graph import draw_graph
from .Interaction.on_button_motion import on_button_motion
from .Interaction.on_button_press import on_button_press
from .Interaction.on_button_release import on_button_release
from .Interaction.on_double_click import on_double_click
from .Interaction.on_mousewheel import on_mousewheel
from .Interaction.on_right_button_motion import on_right_button_motion
from .Interaction.on_right_button_press import on_right_button_press
from .Interaction.on_right_button_release import on_right_button_release
from .Style.init_group_styles import init_group_styles


# ============================
# Data model
# ============================

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


# ============================
# Canvas widget
# ============================

class DAGCanvas(tk.Canvas):
    """
    Tkinter Canvas subclass for drawing and interacting with the DAG.

    All heavy logic is delegated to helper modules under:
      - GUI/Draw
      - GUI/Interaction
      - GUI/Style

    This class also renders a group legend in the top-right corner:
      - Colored square + group name
      - Clicking the square toggles visibility of that group
    """

    def __init__(self, master, nodes: Dict[str, TaskNode], **kwargs):
        super().__init__(master, **kwargs)

        # Core DAG data
        self.nodes: Dict[str, TaskNode] = nodes

        # Group color + visibility (by task "group" string)
        # Filled by init_group_styles(self)
        self.group_colors: Dict[str, str] = {}
        self.group_visible: Dict[str, bool] = {}

        # Canvas items:
        #   key -> {'rect': int, 'text': int}
        self.node_items: Dict[str, Dict[str, int]] = {}
        #   list of edges: {'src': key, 'dst': key, 'line': int}
        self.edge_items: List[Dict[str, object]] = []

        # Legend items: group -> {'rect': item_id, 'text': item_id}
        self.group_legend_items: Dict[str, Dict[str, int]] = {}

        # Drag state for left-button node dragging
        self._drag_data = {
            "node_key": None,
            "x": 0,
            "y": 0,
        }

        # State for right-button edge creation (used by Interaction helpers)
        self._connect_data = {
            "src_key": None,
            "line_id": None,
        }

        self.configure(background="white")

        # ---------------------------------------------------
        # Mouse bindings (use function imports with self passed in)
        # ---------------------------------------------------

        # Left-click: drag nodes
        self.bind("<ButtonPress-1>", lambda e: on_button_press(self, e))
        self.bind("<B1-Motion>", lambda e: on_button_motion(self, e))
        self.bind("<ButtonRelease-1>", lambda e: on_button_release(self, e))
        self.bind("<Double-1>", lambda e: on_double_click(self, e))

        # Right-click: create dependency edges
        self.bind("<ButtonPress-3>", lambda e: on_right_button_press(self, e))
        if on_right_button_motion is not None:
            self.bind("<B3-Motion>", lambda e: on_right_button_motion(self, e))
        self.bind("<ButtonRelease-3>", lambda e: on_right_button_release(self, e))

        # Optional scroll wheel (vertical)
        self.bind("<MouseWheel>", lambda e: on_mousewheel(self, e))
        self.bind("<Button-4>", lambda e: on_mousewheel(self, e))  # some Linux
        self.bind("<Button-5>", lambda e: on_mousewheel(self, e))

        # Initialize group styles and draw the graph
        init_group_styles(self)
        draw_graph(self)
        # If you have a legend helper, you can call it here after draw_graph

__all__ = ["DAGCanvas", "TaskNode"]
