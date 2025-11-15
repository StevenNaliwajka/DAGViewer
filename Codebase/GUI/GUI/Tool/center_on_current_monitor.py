try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None

import tkinter as tk

def center_on_current_monitor(root: tk.Tk) -> None:
    """
    Center the window on the current monitor.

    - If screeninfo is available, use it to find the primary monitor.
    - Otherwise fallback to Tk's screen size and approximate center.
    """
    root.update_idletasks()  # ensure size info is current

    width = root.winfo_width()
    height = root.winfo_height()
    if width <= 1 or height <= 1:
        # If called before first draw, use a sensible default
        width, height = 800, 600

    if get_monitors:
        try:
            monitors = get_monitors()
            if monitors:
                # Simple choice: primary or first monitor
                mon = next((m for m in monitors if getattr(m, "is_primary", False)), monitors[0])
                screen_w = mon.width
                screen_h = mon.height
                offset_x = mon.x
                offset_y = mon.y
            else:
                screen_w = root.winfo_screenwidth()
                screen_h = root.winfo_screenheight()
                offset_x = 0
                offset_y = 0
        except Exception:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            offset_x = 0
            offset_y = 0
    else:
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        offset_x = 0
        offset_y = 0

    x = offset_x + (screen_w - width) // 2
    y = offset_y + (screen_h - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")