#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Dict

# This file is Codebase.GUI.Logic.dag_builder
# so we import siblings via relative imports from Codebase.GUI
from ..IO.task_loader import load_task_nodes


def resolve_dependencies(nodes: Dict[str, TaskNode]) -> None:
    """
    Map depends_on_raw strings to actual node keys,
    and populate deps_resolved / children.

    Extracted from dag_viewer.py. :contentReference[oaicite:6]{index=6}
    """
    label_to_keys: Dict[str, list[str]] = {}
    groupid_to_key: Dict[str, str] = {}

    # Build lookup maps
    for key, node in nodes.items():
        label_to_keys.setdefault(node.label, []).append(key)
        if node.group is not None and node.id is not None:
            groupid_to_key[f"{node.group}{node.id}"] = key

    # Resolve each node's dependencies
    for key, node in nodes.items():
        resolved: list[str] = []
        for dep_str in node.depends_on_raw:
            dep_key: str | None = None

            # 1) direct key match (e.g. "EEEE1")
            if dep_str in nodes:
                dep_key = dep_str

            # 2) match by group+id
            if dep_key is None:
                maybe = groupid_to_key.get(dep_str)
                if maybe is not None:
                    dep_key = maybe

            # 3) match by label (task name)
            if dep_key is None:
                candidates = label_to_keys.get(dep_str, [])
                if candidates:
                    dep_key = candidates[0]  # first match

            if dep_key is not None and dep_key in nodes:
                resolved.append(dep_key)
            else:
                print(
                    f"Warning: for node {key}, dependency '{dep_str}' "
                    f"could not be resolved."
                )

        node.deps_resolved = resolved

    # Fill children based on deps_resolved
    for key, node in nodes.items():
        node.children.clear()

    for key, node in nodes.items():
        for dep_key in node.deps_resolved:
            if dep_key in nodes:
                nodes[dep_key].children.append(key)


def compute_levels(nodes: Dict[str, TaskNode]) -> None:
    """
    Assign an integer 'level' to each node using a simple longest-path-from-sources
    algorithm on the DAG. Extracted from dag_viewer.py. :contentReference[oaicite:7]{index=7}
    """
    indegree = {k: 0 for k in nodes}
    for node in nodes.values():
        for dep_key in node.deps_resolved:
            if dep_key in indegree:
                indegree[node.key] += 1

    # Kahn's algorithm with level propagation
    queue = [k for k, deg in indegree.items() if deg == 0]
    for k in queue:
        nodes[k].level = 0

    while queue:
        cur = queue.pop(0)
        cur_level = nodes[cur].level
        for child in nodes[cur].children:
            if child not in indegree:
                continue
            indegree[child] -= 1
            nodes[child].level = max(nodes[child].level, cur_level + 1)
            if indegree[child] == 0:
                queue.append(child)


def build_dag(tasks_dir: Path | None = None) -> Dict[str, TaskNode]:
    """
    Convenience helper:
    - load tasks
    - resolve dependencies
    - compute levels
    """
    nodes = load_task_nodes(tasks_dir)
    resolve_dependencies(nodes)
    compute_levels(nodes)
    return nodes
