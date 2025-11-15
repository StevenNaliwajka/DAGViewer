from typing import Tuple


def get_node_center(self, key: str) -> Tuple[float, float]:
    rect_id = self.node_items[key]["rect"]
    x1, y1, x2, y2 = self.coords(rect_id)
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0