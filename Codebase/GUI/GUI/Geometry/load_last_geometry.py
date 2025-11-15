from pathlib import Path
import tkinter as tk

def load_last_geometry(root: tk.Tk, geom_file: Path) -> bool:
    """
    If geom_file exists, read it and apply geometry to 'root'.
    Returns True if loaded, False otherwise.
    """
    try:
        if geom_file.is_file():
            geo = geom_file.read_text(encoding="utf-8").strip()
            if geo:
                root.geometry(geo)
                return True
    except Exception as e:
        print(f"Warning: could not load geometry from {geom_file}: {e}")
    return False