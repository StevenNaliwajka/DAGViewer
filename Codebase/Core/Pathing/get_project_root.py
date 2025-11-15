# e.g. put this in Codebase/common/paths.py (or anywhere you like)
from pathlib import Path

def get_project_root() -> Path:
    """
    Return the project root directory.

    For a file located at:
        <project-root>/Codebase/GUI/GUI/...

    project root is 3 levels up from this file.
    """
    return Path(__file__).resolve().parents[3]
