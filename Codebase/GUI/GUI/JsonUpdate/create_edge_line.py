import tkinter as tk

from Codebase.GUI.GUI.Draw.get_node_center import get_node_center


def create_edge_line(self, src_key: str, dst_key: str) -> None:
    """Draw a new arrow from src -> dst unless it already exists."""
    # Don't create duplicates
    for edge in self.edge_items:
        if edge.get("src") == src_key and edge.get("dst") == dst_key:
            return

    if src_key not in self.node_items or dst_key not in self.node_items:
        return

    x1, y1 = get_node_center(self, src_key)
    x2, y2 = get_node_center(self, dst_key)
    line = self.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=2)
    self.edge_items.append({"src": src_key, "dst": dst_key, "line": line})