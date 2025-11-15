from Codebase.GUI.GUI.Interaction.find_node_key_from_item import find_node_key_from_item


def on_button_press(self, event):
    item = self.find_closest(event.x, event.y)
    if not item:
        return
    item_id = item[0]

    key = find_node_key_from_item(self, item_id)
    if key is None:
        return

    self._drag_data["node_key"] = key
    self._drag_data["x"] = event.x
    self._drag_data["y"] = event.y