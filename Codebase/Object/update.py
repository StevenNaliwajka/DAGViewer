#!/usr/bin/env python3
"""
Codebase/TaskMGMT/update.py

Defines the Update data structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from .attachment import Attachment


def _now_str() -> str:
    """
    Returns a simple ISO-like timestamp string for logs.
    """
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Update:
    """
    A single update entry for a task.
    Contains a note and an arbitrary number of text attachments.
    """
    timestamp: str
    author: str
    note: str = ""
    attachments: List[Attachment] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Log creation of the Update
        print(
            f"[{_now_str()}] [Update] Created: "
            f"author='{self.author}', timestamp='{self.timestamp}', "
            f"note_preview='{self.note[:40]}{'...' if len(self.note) > 40 else ''}'"
        )

    @classmethod
    def new(
        cls,
        author: str,
        note: str = "",
        attachments: Optional[List[Attachment]] = None,
    ) -> "Update":
        """
        Convenience constructor that auto-fills the timestamp with UTC now.
        """
        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        print(
            f"[{_now_str()}] [Update.new] Creating new Update: "
            f"author='{author}', utc_timestamp='{ts}', "
            f"note_preview='{note[:40]}{'...' if len(note) > 40 else ''}'"
        )
        return cls(
            timestamp=ts,
            author=author,
            note=note,
            attachments=attachments or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        print(
            f"[{_now_str()}] [Update] to_dict() called for "
            f"author='{self.author}', timestamp='{self.timestamp}'"
        )
        return {
            "timestamp": self.timestamp,
            "author": self.author,
            "note": self.note,
            "attachments": [a.to_dict() for a in self.attachments],
        }
