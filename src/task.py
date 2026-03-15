"""Task dataclass definition."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a single task."""

    id: int
    title: str
    status: str = "todo"
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        """Serialize task to a plain dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
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
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
