#!/usr/bin/env python3
"""
Codebase/FileIO/create_task_file.py

Create a task JSON file from a Jinja2 template.

- This file lives at: Codebase/FileIO/create_task_file.py
- Template lives at:  Codebase/Template/task_template.json.j2
- Output lives at:    <project_root>/Tasks/<group><id>.json   (e.g. AAAA1.json)
"""

from __future__ import annotations

from dataclasses import is_dataclass, asdict
from pathlib import Path
from datetime import datetime
import re
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import the ID generator (expects: get_new_task_id(group: str) -> int)
from Codebase.FileIO.get_new_task_id import get_new_task_id


# Determine paths relative to this file
SCRIPT_DIR = Path(__file__).resolve().parent           # .../Codebase/FileIO
CODEBASE_DIR = SCRIPT_DIR.parent                       # .../Codebase
PROJECT_ROOT = CODEBASE_DIR.parent                     # .../
TEMPLATE_DIR = CODEBASE_DIR / "Template"               # .../Codebase/Template
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Tasks"            # .../Tasks


def _now_str() -> str:
    """Simple ISO-like timestamp for logs."""
    return datetime.now().isoformat(timespec="seconds")


def _slugify(text: str) -> str:
    """
    Turn 'Task at Hand' into 'task_at_hand' for filenames.
    (Currently unused for filename, but kept in case you want it later.)
    """
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)   # remove non-word characters
    text = re.sub(r"[\s-]+", "_", text)    # spaces/dashes → underscore
    return text or "task"


def _normalize_obj(obj: Any) -> Dict[str, Any]:
    """
    Convert Update/Attachment-like objects to dicts, preferring .to_dict()
    and falling back to dataclasses / __dict__.
    """
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return obj.to_dict()
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return dict(obj)
    # Generic object with attributes
    return {k: v for k, v in vars(obj).items() if not k.startswith("_")}


def _task_to_context(task: Any) -> dict:
    """
    Convert Task object / dict / dataclass to a context dict for Jinja2.
    Expects keys like: task, description, id, group, owner,
    depends_on (list), updates (list of dicts or objects).
    """
    # Prefer the Task.to_dict() method if it exists
    if hasattr(task, "to_dict") and callable(getattr(task, "to_dict")):
        data = task.to_dict()
        print(f"[{_now_str()}] [create_task_file] Using task.to_dict() for context.")
    elif is_dataclass(task):
        data = asdict(task)
        print(f"[{_now_str()}] [create_task_file] Using asdict() on dataclass Task.")
    elif isinstance(task, dict):
        data = dict(task)
        print(f"[{_now_str()}] [create_task_file] Using dict Task context.")
    else:
        # Generic object with attributes
        data = {k: v for k, v in vars(task).items() if not k.startswith("_")}
        print(f"[{_now_str()}] [create_task_file] Using vars() on generic Task object.")

    # Ensure reasonable defaults
    data.setdefault("depends_on", [])
    data.setdefault("updates", [])

    # Normalize updates & attachments in case they are objects, not dicts
    normalized_updates = []
    for u in data.get("updates", []):
        u_dict = _normalize_obj(u)

        # Normalize attachments inside each update
        attachments = u_dict.get("attachments", [])
        u_dict["attachments"] = [
            _normalize_obj(a) for a in attachments
        ]

        normalized_updates.append(u_dict)

    data["updates"] = normalized_updates

    return data


def create_task_file(task: Any, output_dir: str | Path | None = None) -> Path:
    """
    Render Codebase/Template/task_template.json.j2 using `task`
    and write it to a JSON file.

    Args:
        task:  Task object / dataclass / dict with attributes/keys matching the template
        output_dir: Optional directory to write into.
                    Defaults to <project_root>/Tasks/

    Returns:
        Path to the created JSON file.
    """
    # Resolve output directory
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("json.j2",)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("task_template.json.j2")

    # Build context from Task
    context = _task_to_context(task)

    # Make sure we have a valid group (EEEE letters)
    group = context.get("group")
    if not isinstance(group, str) or not group.strip():
        raise ValueError(
            "[create_task_file] Task context must include a non-empty string 'group' "
            "(e.g. 'AAAA')."
        )
    group = group.strip().upper()
    context["group"] = group  # normalize group in context

    # Get a new unique numeric task ID for this group and force it into the context
    new_task_id = get_new_task_id(group)
    context["id"] = new_task_id

    # Combined task identifier: EEEEID (e.g. AAAA1)
    task_id_str = f"{group}{new_task_id}"

    # Filename is "<group><id>.json" (e.g. AAAA1.json)
    filename = f"{task_id_str}.json"
    output_path = output_dir / filename

    task_name = context.get("task", "task")

    print(
        f"[{_now_str()}] [create_task_file] Rendering task '{task_name}' "
        f"(group={group}, id={new_task_id}) to: {output_path}"
    )

    # Render and write
    rendered = template.render(**context)
    output_path.write_text(rendered + "\n", encoding="utf-8")

    print(f"[{_now_str()}] [create_task_file] Wrote task file: {output_path}")
    return output_path


# Optional: example usage if you run this file directly
if __name__ == "__main__":
    # Minimal mock Task example (you can swap in your real Task class if you want)
    class MockTask:
        def __init__(self):
            self.task = "Task at Hand"
            self.description = "Description of Task"
            # self.id will be overridden by get_new_task_id()
            self.id = None
            self.group = "AAAA"
            self.owner = "Steven"
            self.depends_on = ["clean_data"]
            self.updates = []

    path = create_task_file(MockTask())
    print(f"Created task file at: {path}")
