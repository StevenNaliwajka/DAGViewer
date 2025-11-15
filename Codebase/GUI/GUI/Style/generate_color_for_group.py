import colorsys
import hashlib


def generate_color_for_group(self, group: str) -> str:
    """
    Deterministic 'random' color based on group name.

    Uses SHA1 hash -> hue, so the same group name always
    gets the same color in a session, but different groups
    look nicely distinct.
    """
    h = int(hashlib.sha1(group.encode("utf-8")).hexdigest(), 16)
    hue = (h % 360) / 360.0
    saturation = 0.5
    value = 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"