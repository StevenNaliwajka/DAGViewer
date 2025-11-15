#!/usr/bin/env python3
"""
Codebase/TaskMGMT/task.py

Defines the Task data structure and a convenience factory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .update import Update


def _now_str() -> str:
    """
    Returns a simple ISO-like timestamp string for logs.
    """
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Task:
    """
    Core Task object.

    Matches the JSON structure:

    {
      "task": "Task at Hand",
      "description": "Description of Task",
      "id": 1,
      "group": "AAAA",
      "owner": "Steven",
      "depends_on": ["clean_data"],
      "updates": [ ... ]
    }
    """
    task: str                 # Task name/title
    description: str          # Task description
    group: str                # Group identifier

    id: Optional[int] = None  # Can be set by your create_task logic or DAG system
    owner: str = "Steven"
    depends_on: List[str] = field(default_factory=list)
    updates: List[Update] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Log creation of the Task
        print(
            f"[{_now_str()}] [Task] Created: "
            f"task='{self.task}', group='{self.group}', owner='{self.owner}'"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Task into a plain dict suitable for Jinja2 rendering or JSON dumping.
        """
        print(f"[{_now_str()}] [Task] to_dict() called for task='{self.task}'")
        return {
            "task": self.task,
            "description": self.description,
            "id": self.id,
            "group": self.group,
            "owner": self.owner,
            "depends_on": list(self.depends_on),
            "updates": [u.to_dict() for u in self.updates],
        }


# ---------- Convenience factory for the Run ----------

def task(
    name: str,
    description: str,
    group: str,
    owner: str = "Steven",
) -> Task:
    """
    Convenience function so the Run can call:

        t = task(task_name, description, group)

    and get a Task object.
    """
    print(
        f"[{_now_str()}] [TaskFactory] Creating Task from factory: "
        f"name='{name}', group='{group}', owner='{owner}'"
    )
    return Task(
        task=name,
        description=description,
        group=group,
        owner=owner,
    )
