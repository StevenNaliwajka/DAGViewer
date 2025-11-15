from Codebase.GUI.GUI.Draw.draw_graph import draw_graph


def redraw_all(self) -> None:
    """
    Convenience wrapper so external code can force a redraw.
    """
    draw_graph(self)