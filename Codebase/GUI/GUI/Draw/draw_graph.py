from typing import Dict, List

from Codebase.GUI.GUI.Draw.draw_edges import draw_edges
from Codebase.GUI.GUI.Style.is_group_visable_for_key import is_group_visible_for_key


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

            # Color by group if available
            node_obj = self.nodes[key]
            group = getattr(node_obj, "group", None)
            if group and group in self.group_colors:
                fill_color = self.group_colors[group]
            else:
                fill_color = "#f0f0ff"  # default for ungrouped

            rect = self.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline="black",
                fill=fill_color,
                width=2,
                tags=("node", key),
            )
            text = self.create_text(
                x,
                y,
                text=node_obj.label,
                tags=("label", key),
            )

            self.node_items[key] = {"rect": rect, "text": text}

            # Apply visibility based on group toggle
            if not is_group_visible_for_key(self,key):
                self.itemconfigure(rect, state="hidden")
                self.itemconfigure(text, state="hidden")

            max_x = max(max_x, x2 + 50)
            max_y = max(max_y, y2 + 50)

    # Draw edges after all nodes are positioned
    draw_edges(self)

    # Set scroll region
    self.config(scrollregion=(0, 0, max_x, max_y))