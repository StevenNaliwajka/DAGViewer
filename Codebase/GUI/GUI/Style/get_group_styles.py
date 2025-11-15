from typing import Dict, Tuple


def get_group_styles(self) -> Dict[str, Tuple[str, bool]]:
    """
    Return mapping: group -> (color, visible_flag)
    for the right-hand legend / toggles.
    """
    return {
        group: (self.group_colors[group], self.group_visible.get(group, True))
        for group in self.group_colors
    }
