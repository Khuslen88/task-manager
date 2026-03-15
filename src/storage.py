"""JSON storage utilities for tasks."""

import json
import os
from typing import List

from src.task import Task

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "tasks.json")


def _resolve_path() -> str:
    return os.path.abspath(DATA_FILE)


def load_tasks() -> List[Task]:
    """Load all tasks from the JSON file. Returns empty list if file doesn't exist."""
    path = _resolve_path()
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task.from_dict(t) for t in data.get("tasks", [])]


def save_tasks(tasks: List[Task]) -> None:
    """Persist all tasks to the JSON file."""
    path = _resolve_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": [t.to_dict() for t in tasks]}, f, indent=2)
        f.write("\n")


def next_id(tasks: List[Task]) -> int:
    """Return the next available task ID."""
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
