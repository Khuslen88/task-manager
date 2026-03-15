"""Task dataclass definition."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

VALID_PRIORITIES = {"high", "medium", "low"}
VALID_STATUSES = {"todo", "in_progress", "done"}


@dataclass
class Task:
    """Represents a single task."""

    id: int
    title: str
    status: str = "todo"
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"
    assignee: str = ""
    tags: List[str] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def __post_init__(self):
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Must be one of {sorted(VALID_PRIORITIES)}.")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of {sorted(VALID_STATUSES)}.")

    def to_dict(self) -> dict:
        """Serialize task to a plain dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "assignee": self.assignee,
            "tags": self.tags,
            "comments": self.comments,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """Deserialize a task from a plain dictionary."""
        return Task(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "todo"),
            assignee=data.get("assignee", ""),
            tags=data.get("tags", []),
            comments=data.get("comments", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
