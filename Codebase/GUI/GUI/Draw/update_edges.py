from Codebase.GUI.GUI.Draw.get_node_center import get_node_center


def update_edges(self) -> None:
    """
    Update all edge line coordinates based on node positions.
    """
    for edge in self.edge_items:
        src = edge["src"]
        dst = edge["dst"]
        line_id = edge["line"]
        if src not in self.node_items or dst not in self.node_items:
            continue
        x1, y1 = get_node_center(self, src)
        x2, y2 = get_node_center(self, dst)
        self.coords(line_id, x1, y1, x2, y2)