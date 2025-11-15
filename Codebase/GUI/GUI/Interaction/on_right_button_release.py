from Codebase.GUI.GUI.Interaction.find_node_key_from_item import find_node_key_from_item
from Codebase.GUI.GUI.JsonUpdate.connect_nodes import connect_nodes


def on_right_button_release(self, event):
    """Finish a connection drag; if released on another node, connect them."""
    src_key = self._connect_data.get("src_key")
    line_id = self._connect_data.get("line_id")

    # Remove the temporary line, if any
    if line_id is not None:
        try:
            self.delete(line_id)
        except Exception:
            pass
    self._connect_data["line_id"] = None

    if src_key is None:
        self._connect_data["src_key"] = None
        return

    # Node under the cursor on release
    item = self.find_closest(event.x, event.y)
    dst_key = None
    if item:
        dst_key = find_node_key_from_item(self, item[0])

    self._connect_data["src_key"] = None

    # Must end on another node to create an edge
    if not dst_key or dst_key == src_key:
        return

    # src_key -> dst_key (src is parent, dst is child)
    connect_nodes(self, src_key, dst_key)