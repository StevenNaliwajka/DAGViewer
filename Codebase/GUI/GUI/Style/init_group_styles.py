from Codebase.GUI.GUI.Style.generate_color_for_group import generate_color_for_group


def init_group_styles(self) -> None:
    """
    Collect all non-empty node.groups and assign each one a color
    and initial visibility=True.
    """
    groups = set()
    for node in self.nodes.values():
        g = getattr(node, "group", None)
        if g:  # only real groups; ungrouped nodes stay default color
            groups.add(g)

    for g in sorted(groups):
        self.group_colors[g] = generate_color_for_group(self, g)
        self.group_visible[g] = True