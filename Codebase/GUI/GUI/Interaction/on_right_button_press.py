from Codebase.GUI.GUI.Draw.get_node_center import get_node_center
from Codebase.GUI.GUI.Interaction.find_node_key_from_item import find_node_key_from_item


def on_right_button_press(self, event):
    """Start a connection drag from the node under the cursor (right-click)."""
    item = self.find_closest(event.x, event.y)
    if not item:
        return
    item_id = item[0]

    key = find_node_key_from_item(self, item_id)
    if key is None:
        return

    # Start connection from this node
    self._connect_data["src_key"] = key
    x0, y0 = get_node_center(self, key)
    line = self.create_line(
        x0,
        y0,
        event.x,
        event.y,
        dash=(4, 2),
        width=2,
    )
    self._connect_data["line_id"] = line