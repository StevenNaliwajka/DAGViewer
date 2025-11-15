from Codebase.GUI.GUI.Draw.get_node_center import get_node_center


def on_right_button_motion(self, event):
    """While right-dragging, update the temporary connection line."""
    src_key = self._connect_data.get("src_key")
    line_id = self._connect_data.get("line_id")
    if src_key is None or line_id is None:
        return

    x0, y0 = get_node_center(self, src_key)
    self.coords(line_id, x0, y0, event.x, event.y)