#!/usr/bin/env python3
from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================
# Helper imports (relative)
# ============================

# ---- Draw helpers ----
from .Draw.draw_graph import draw_graph as _draw_graph
from .Draw.update_edges import update_edges as _update_edges
from .Draw.get_node_center import get_node_center as _get_node_center
from .Draw.draw_edges import draw_edges as _draw_edges

# ---- Interaction helpers ----
from .Interaction.on_button_press import on_button_press as _on_button_press
from .Interaction.on_button_motion import on_button_motion as _on_button_motion
from .Interaction.on_button_release import _on_button_release as _on_button_release
from .Interaction.on_double_click import on_double_click as _on_double_click
from .Interaction.on_mousewheel import on_mousewheel as _on_mousewheel
from .Interaction.on_right_button_press import (
    on_right_button_press as _on_right_button_press,
)
from .Interaction.on_right_button_motion import (
    on_right_button_motion as _on_right_button_motion,
)
from .Interaction.on_right_button_release import (
    on_right_button_release as _on_right_button_release,
)

# ---- Style helpers (groups, colors, visibility) ----
from .Style.init_group_styles import init_group_styles as _init_group_styles
from .Style.redraw_all import redraw_all as _redraw_all
from .Style.set_group_visible import set_group_visible as _set_group_visible
from .Style.get_group_styles import get_group_styles as _get_group_styles
from .Style.generate_color_for_group import (
    generate_color_for_group as _generate_color_for_group,
)
from .Style.is_group_visable_for_key import (
    is_group_visible_for_key as _is_group_visible_for_key,
)


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
    """

    def __init__(self, master, nodes: Dict[str, TaskNode], **kwargs):
        super().__init__(master, **kwargs)

        # Core DAG data
        self.nodes: Dict[str, TaskNode] = nodes

        # Group color + visibility (by task "group" string)
        self.group_colors: Dict[str, str] = {}
        self.group_visible: Dict[str, bool] = {}

        # Canvas items:
        #   key -> {'rect': int, 'text': int}
        self.node_items: Dict[str, Dict[str, int]] = {}
        #   list of edges: {'src': key, 'dst': key, 'line': int}
        self.edge_items: List[Dict[str, object]] = []

        # Drag state for left-button node dragging
        self._drag_data = {
            "node_key": None,
            "x": 0,
            "y": 0,
        }

        # State for right-button edge creation (used by Interaction helpers)
        # NOTE: this is what on_right_button_* expects.
        self._connect_data = {
            "src_key": None,
            "line_id": None,
        }

        self.configure(background="white")

        # Mouse bindings
        # Left-click: drag nodes
        self.bind("<ButtonPress-1>", self._on_button_press)
        self.bind("<B1-Motion>", self._on_button_motion)
        self.bind("<ButtonRelease-1>", self._on_button_release)
        self.bind("<Double-1>", self._on_double_click)

        # Right-click: create dependency edges
        self.bind("<ButtonPress-3>", self._on_right_button_press)
        self.bind("<B3-Motion>", self._on_right_button_motion)
        self.bind("<ButtonRelease-3>", self._on_right_button_release)

        # Optional scroll wheel (vertical)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", self._on_mousewheel)  # some Linux
        self.bind("<Button-5>", self._on_mousewheel)

        # Initialize group styles and draw the graph
        self._init_group_styles()
        self.draw_graph()

    # ---------------------------------------------------
    # Draw / layout helpers (thin wrappers)
    # ---------------------------------------------------

    def _init_group_styles(self) -> None:
        _init_group_styles(self)

    def draw_graph(self) -> None:
        """Draw all nodes and edges."""
        _draw_graph(self)

    def draw_edges(self) -> None:
        """(Re)draw all edges explicitly, if helper provides it."""
        _draw_edges(self)

    def update_edges(self) -> None:
        """Update all edge positions after nodes move."""
        _update_edges(self)

    def get_node_center(self, node_key: str) -> Tuple[float, float]:
        """Return (x, y) center of the node's rectangle."""
        return _get_node_center(self, node_key)

    # ---------------------------------------------------
    # Group style / visibility helpers
    # ---------------------------------------------------

    def redraw_all(self) -> None:
        _redraw_all(self)

    def set_group_visible(self, group: str, visible: bool) -> None:
        _set_group_visible(self, group, visible)

    def get_group_styles(self):
        """Return whatever structure get_group_styles defines (e.g., colors/visibility)."""
        return _get_group_styles(self)

    def generate_color_for_group(self, group: str) -> str:
        return _generate_color_for_group(self, group)

    def is_group_visible_for_key(self, node_key: str) -> bool:
        return _is_group_visible_for_key(self, node_key)

    # ---------------------------------------------------
    # Mouse interaction wrappers
    # ---------------------------------------------------

    def _on_button_press(self, event) -> None:
        _on_button_press(self, event)

    def _on_button_motion(self, event) -> None:
        _on_button_motion(self, event)

    def _on_button_release(self, event) -> None:
        _on_button_release(self, event)

    def _on_double_click(self, event) -> None:
        _on_double_click(self, event)

    def _on_mousewheel(self, event) -> None:
        _on_mousewheel(self, event)

    def _on_right_button_press(self, event) -> None:
        _on_right_button_press(self, event)

    def _on_right_button_motion(self, event) -> None:
        _on_right_button_motion(self, event)

    def _on_right_button_release(self, event) -> None:
        _on_right_button_release(self, event)


__all__ = ["DAGCanvas", "TaskNode"]