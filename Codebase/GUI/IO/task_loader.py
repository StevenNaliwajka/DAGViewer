#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ..Model.task_node import TaskNode
from ..IO.tasks_dir import find_tasks_dir


def load_task_nodes(tasks_dir: Path | None = None) -> Dict[str, TaskNode]:
    """
    Load all *.json files under tasks_dir and return a dict: key -> TaskNode.

    key is filename stem, e.g. "EEEE1" from EEEE1.json.
    Mirrors the logic from dag_viewer.py. :contentReference[oaicite:5]{index=5}
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
