from Codebase.GUI.GUI.Draw.update_edges import update_edges


def on_button_motion(self, event):
    key = self._drag_data["node_key"]
    if key is None:
        return

    dx = event.x - self._drag_data["x"]
    dy = event.y - self._drag_data["y"]
    self._drag_data["x"] = event.x
    self._drag_data["y"] = event.y

    rect_id = self.node_items[key]["rect"]
    text_id = self.node_items[key]["text"]

    self.move(rect_id, dx, dy)
    self.move(text_id, dx, dy)

    update_edges(self)