"""JSON storage utilities for tasks."""

import json
import os
import tempfile
from typing import List, Tuple

from src.task import Task

# Resolve data file relative to project root (one level above src/)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.environ.get("TASK_DATA_FILE", os.path.join(_PROJECT_ROOT, "tasks.json"))


def _load_raw() -> dict:
    """Read the raw JSON structure from disk. Returns empty structure if file missing."""
    path = os.path.abspath(DATA_FILE)
    if not os.path.exists(path):
        return {"next_id": 1, "tasks": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(data: dict) -> None:
    """Write JSON to disk atomically using a temp file + rename."""
    path = os.path.abspath(DATA_FILE)
    dir_ = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)  # atomic on all platforms
    except Exception:
        os.unlink(tmp_path)
        raise


def load_tasks() -> List[Task]:
    """Load all tasks from disk. Returns empty list if file doesn't exist."""
    return [Task.from_dict(t) for t in _load_raw().get("tasks", [])]


def save_tasks(tasks: List[Task]) -> None:
    """Persist tasks to disk, preserving the next_id counter."""
    raw = _load_raw()
    raw["tasks"] = [t.to_dict() for t in tasks]
    _save_raw(raw)


def next_id() -> int:
    """Return the next available task ID and increment the persistent counter."""
    raw = _load_raw()
    nid = raw.get("next_id", 1)
    raw["next_id"] = nid + 1
    raw.setdefault("tasks", [])
    _save_raw(raw)
    return nid
