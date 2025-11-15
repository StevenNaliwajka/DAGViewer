from tkinter import messagebox

from Codebase.GUI.GUI.Interaction.find_node_key_from_item import find_node_key_from_item


def on_double_click(self, event):
    item = self.find_closest(event.x, event.y)
    if not item:
        return
    item_id = item[0]
    key = find_node_key_from_item(self, item_id)
    if key is None:
        return

    node = self.nodes[key]
    info = [
        f"Key: {node.key}",
        f"Label: {node.label}",
        f"File: {node.file_path.name}",
        f"Group: {node.group}",
        f"ID: {node.id}",
        "",
        f"Depends on: {', '.join(node.deps_resolved) if node.deps_resolved else '(none)'}",
        f"Children: {', '.join(node.children) if node.children else '(none)'}",
    ]
    messagebox.showinfo("Task info", "\n".join(info))