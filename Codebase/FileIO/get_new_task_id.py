#!/usr/bin/env python3
"""
Utility to generate the next task ID number for a given group.

Conventions:
- Task files live under: <project_root>/Tasks/
- Filenames are of the form: <GROUP><NUMBER>.json
  e.g. "AAAA1.json", "AAAA2.json", "EEEE12123.json"
"""

from __future__ import annotations

from pathlib import Path
import re

# Paths relative to this file
SCRIPT_DIR = Path(__file__).resolve().parent       # .../Codebase/FileIO
CODEBASE_DIR = SCRIPT_DIR.parent                   # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                 # .../DAGViewer
TASKS_DIR = PROJECT_ROOT / "Tasks"                 # .../DAGViewer/Tasks


def get_new_task_id(group: str) -> int:
    """
    Determine the next numeric ID for a given group.

    Example:
        Tasks/
          AAAA1.json
          AAAA2.json
          BBBB10.json

        get_new_task_id("AAAA") -> 3
        get_new_task_id("BBBB") -> 11
        get_new_task_id("CCCC") -> 1  (no files yet)
    """
    group = group.strip()
    if not group:
        raise ValueError("group must be a non-empty string of letters")

    group_norm = group.upper()

    if not TASKS_DIR.exists():
        return 1

    # Match filenames like "AAAA123.json" (case-insensitive)
    pattern = re.compile(rf'^{re.escape(group_norm)}(\d+)\.json$', re.IGNORECASE)

    max_id = 0
    for path in TASKS_DIR.iterdir():
        if not path.is_file():
            continue
        m = pattern.match(path.name)
        if not m:
            continue
        try:
            num = int(m.group(1))
        except ValueError:
            continue
        if num > max_id:
            max_id = num

    return max_id + 1 if max_id > 0 else 1


if __name__ == "__main__":
    test_group = "EEEE"
    print(f"Next ID for group {test_group}: {get_new_task_id(test_group)}")
