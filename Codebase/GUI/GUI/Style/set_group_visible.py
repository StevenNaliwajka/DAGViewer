from Codebase.GUI.GUI.Style.redraw_all import redraw_all


def set_group_visible(self, group: str, visible: bool) -> None:
    """
    Toggle visibility for a group and redraw the graph.
    """
    self.group_visible[group] = visible
    redraw_all(self)