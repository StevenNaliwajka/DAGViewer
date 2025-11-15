#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Path to this file: .../DAGViewer/Codebase/Core/Pathing/project_paths.py
_THIS_FILE = Path(__file__).resolve()


_DEFAULT_PROJECT_ROOT = _THIS_FILE.parents[3]


class ProjectPaths:
    """
    Central, in-memory path config for the project.

    These class attributes are what you access everywhere else, e.g.:

        from Codebase.Core.Pathing.project_paths import ProjectPaths
        tasks_dir = ProjectPaths.tasks
    """

    # Defaults based on this file's location
    project_root: Path = _DEFAULT_PROJECT_ROOT
    codebase: Path = _DEFAULT_PROJECT_ROOT / "Codebase"
    tasks: Path = _DEFAULT_PROJECT_ROOT / "Tasks"
    userdata: Path = _DEFAULT_PROJECT_ROOT / "UserData"

    # Optional JSON override file at project root
    config_path: Path = _DEFAULT_PROJECT_ROOT / "project_paths.json"

    @classmethod
    def load_from_config(cls, config_path: Path | None = None) -> None:
        """
        Optionally override paths from a JSON config like:

        {
          "project_root": "/some/other/root",
          "codebase": "/some/other/root/Codebase",
          "tasks": "/some/other/root/Tasks",
          "userdata": "/some/other/root/UserData"
        }
        """
        path = config_path or cls.config_path
        if not path.is_file():
            return

        try:
            data: Dict[str, Any] = json.loads(path.read_text())
        except Exception as e:  # pragma: no cover
            print(f"[ProjectPaths] Warning: failed to read {path}: {e}")
            return

        root = Path(data.get("project_root", cls.project_root)).expanduser().resolve()

        cls.project_root = root
        cls.codebase = Path(data.get("codebase", root / "Codebase")).expanduser().resolve()
        cls.tasks = Path(data.get("tasks", root / "Tasks")).expanduser().resolve()
        cls.userdata = Path(data.get("userdata", root / "UserData")).expanduser().resolve()
        cls.config_path = path


def add_to_sys_path() -> None:
    """
    Ensure project_root and Codebase are on sys.path.
    Call this early in entrypoint scripts.
    """
    for p in (ProjectPaths.project_root, ProjectPaths.codebase):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


# Load optional config overrides at import time
ProjectPaths.load_from_config()
