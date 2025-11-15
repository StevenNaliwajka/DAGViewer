import tkinter as tk
from pathlib import Path


def save_geometry(root: tk.Tk, geom_file: Path) -> None:
    """
    Save the current geometry of 'root' into geom_file.
    """
    try:
        geom_file.write_text(root.winfo_geometry(), encoding="utf-8")
    except Exception as e:
        print(f"Warning: could not save geometry to {geom_file}: {e}")
