from typing import Optional


def find_node_key_from_item(self, item_id: int) -> Optional[str]:
    tags = self.gettags(item_id)
    for t in tags:
        if t in self.nodes:
            return t
    return None