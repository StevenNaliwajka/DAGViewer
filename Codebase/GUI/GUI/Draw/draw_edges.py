import tkinter as tk

from Codebase.GUI.GUI.Draw.get_node_center import get_node_center
from Codebase.GUI.GUI.Style.is_group_visable_for_key import is_group_visible_for_key


def draw_edges(self) -> None:
    self.edge_items.clear()
    for key, node in self.nodes.items():
        # edges from dep -> node.key
        for dep_key in node.deps_resolved:
            if dep_key not in self.node_items or key not in self.node_items:
                continue

            # Skip edges where either node's group is hidden
            if not is_group_visible_for_key(self, dep_key):
                continue
            if not is_group_visible_for_key(self, key):
                continue

            src_center = get_node_center(self, dep_key)
            dst_center = get_node_center(self, key)

            line = self.create_line(
                *src_center,
                *dst_center,
                arrow=tk.LAST,
                width=2,
            )
            self.edge_items.append({"src": dep_key, "dst": key, "line": line})