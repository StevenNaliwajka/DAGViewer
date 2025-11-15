#!/usr/bin/env python3
"""
Locate the folder that holds task JSON files.

Current convention:

    <project_root>/Tasks

We also support a few fallbacks (legacy paths), but the
project-root Tasks folder is preferred.
"""

from __future__ import annotations

from pathlib import Path


# This file lives at: Codebase/GUI/IO/tasks_dir.py
SCRIPT_DIR = Path(__file__).resolve().parent      # .../Codebase/GUI/IO
GUI_DIR = SCRIPT_DIR.parent                       # .../Codebase/GUI
CODEBASE_DIR = GUI_DIR.parent                     # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                # .../


def find_tasks_dir() -> Path:
    """
    Return the directory that contains task JSON files.

    Search order (first existing match wins):

    1. <project_root>/Tasks
    2. <project_root>/Task        (fallback)
    3. <Codebase>/Tasks           (legacy)
    4. <Codebase>/GUI/Tasks       (legacy)
    """
    candidate_dirs = [
        PROJECT_ROOT / "Tasks",
        PROJECT_ROOT / "Task",
        CODEBASE_DIR / "Tasks",
        GUI_DIR / "Tasks",
    ]

    for d in candidate_dirs:
        if d.is_dir():
            return d

    # If nothing matched, raise with a helpful message
    raise RuntimeError(
        "Could not find a Tasks folder in any of: "
        + ", ".join(str(p) for p in candidate_dirs)
    )
