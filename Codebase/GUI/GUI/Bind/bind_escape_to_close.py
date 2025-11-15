import tkinter as tk
from typing import Callable, Optional


def bind_escape_to_close(root: tk.Tk, on_close: Optional[Callable[[], None]] = None) -> None:
    """
    Bind ESC so that pressing it anywhere closes the window.

    If 'on_close' is provided, it will be called.
    If it is None, we fall back to root.destroy().
    """
    def _handler(event):
        if on_close is not None:
            on_close()
        else:
            # Fallback behavior: just close the window
            root.destroy()

    # Bind on the toplevel AND globally inside it
    root.bind("<Escape>", _handler)
    root.bind_all("<Escape>", _handler)
