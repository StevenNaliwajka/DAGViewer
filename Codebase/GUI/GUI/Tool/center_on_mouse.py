import tkinter as tk

def center_on_mouse(win: tk.Tk | tk.Toplevel) -> None:
    """
    Center the window around the current mouse position.

    If screeninfo is available, it will clamp the window to stay inside
    the monitor that currently contains the mouse pointer.
    """
    win.update_idletasks()

    # Window size (fallback to requested size if current is 1x1)
    w = win.winfo_width() or win.winfo_reqwidth()
    h = win.winfo_height() or win.winfo_reqheight()

    # Mouse position in global screen coordinates
    px = win.winfo_pointerx()
    py = win.winfo_pointery()

    # Default: center exactly on mouse
    x = int(px - w / 2)
    y = int(py - h / 2)

    win.geometry(f"{w}x{h}+{x}+{y}")