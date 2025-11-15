#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .tasks_dir import find_tasks_dir  # same package, cleaner import


@dataclass
class TaskNode:
    """
    In-memory representation of a task JSON file.

    key:
        Filename stem, e.g. "EEEE1" from "EEEE1.json".
    label:
        Human-readable label (usually the "task" field in the JSON).
    file_path:
        Full path to the JSON file on disk.
    depends_on_raw:
        Raw list of dependency IDs/keys from the JSON.
    group:
        Optional grouping/category string.
    id:
        Optional explicit ID from the JSON (if present).

    depends_on / children:
        These can be populated later by dag_builder.py to build the graph.
    x, y:
        Coordinates used by the GUI layout / canvas.
    """
    key: str
    label: str
    file_path: Path
    depends_on_raw: List[str]
    group: str | None = None
    id: str | None = None

    # Filled in later by graph-building logic
    depends_on: List["TaskNode"] = field(default_factory=list)
    children: List["TaskNode"] = field(default_factory=list)

    # Layout position for the canvas
    x: float = 0.0
    y: float = 0.0
    # DAG layer for layout
    level: int = 0

def load_task_nodes(tasks_dir: Path | None = None) -> Dict[str, TaskNode]:
    """
    Load all *.json files under tasks_dir and return a dict: key -> TaskNode.

    key is filename stem, e.g. "EEEE1" from EEEE1.json.
    """
    if tasks_dir is None:
        tasks_dir = find_tasks_dir()

    nodes: Dict[str, TaskNode] = {}

    for json_file in sorted(tasks_dir.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: could not read {json_file}: {e}")
            continue

        key = json_file.stem
        label = data.get("task", key)
        group = data.get("group")
        node_id = data.get("id")

        depends_on = data.get("depends_on", [])
        if not isinstance(depends_on, list):
            depends_on = []

        nodes[key] = TaskNode(
            key=key,
            label=label,
            file_path=json_file,
            depends_on_raw=depends_on,
            group=group,
            id=node_id,
        )

    print(f"Loaded {len(nodes)} tasks from {tasks_dir}")
    return nodes
