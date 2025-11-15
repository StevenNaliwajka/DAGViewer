def is_group_visible_for_key(self, key: str) -> bool:
    """
    Check whether the node with this key is visible based on its group.
    Ungrouped nodes are always visible.
    """
    node = self.nodes.get(key)
    if node is None:
        return True
    g = getattr(node, "group", None)
    if not g:
        return True  # no group -> can't be toggled off
    return self.group_visible.get(g, True)