#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class TaskNode:
    """
    In-memory representation of a task JSON file.

    - key:   unique key, usually filename stem, e.g. "EEEE1"
    - label: display label, from "task" field in the JSON
    """
    key: str
    label: str
    file_path: Path
    depends_on_raw: List[str] = field(default_factory=list)
    group: Optional[str] = None
    id: Optional[int] = None

    # Resolved DAG fields (filled after loading)
    deps_resolved: List[str] = field(default_factory=list)   # keys this node depends on
    children: List[str] = field(default_factory=list)        # outgoing edges (this -> child)
    level: int = 0                                           # layout layer
