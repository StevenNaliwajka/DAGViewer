def set_group_visible(self, group: str, visible: bool) -> None:
    """
    Toggle visibility for a group and redraw the graph.
    """
    self.group_visible[group] = visible
    self._redraw_all()