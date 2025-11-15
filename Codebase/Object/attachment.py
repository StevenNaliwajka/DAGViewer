#!/usr/bin/env python3
"""
Codebase/TaskMGMT/attachment.py

Defines the Attachment data structure.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Attachment:
    """
    A single text attachment associated with an update.
    """
    name: str
    content: str
    type: str = "text/plain"  # keep a type field for future flexibility

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "content": self.content,
        }
