"""Tests for Task dataclass."""

from src.task import Task


def test_task_defaults():
    task = Task(id=1, title="Buy milk")
    assert task.status == "todo"
    assert task.priority == "medium"
    assert task.description == ""
    assert task.due_date is None


def test_task_to_dict():
    task = Task(id=1, title="Buy milk")
    d = task.to_dict()
    assert d["id"] == 1
    assert d["title"] == "Buy milk"
    assert d["status"] == "todo"


def test_task_from_dict_roundtrip():
    task = Task(id=2, title="Walk dog", priority="high", status="done")
    restored = Task.from_dict(task.to_dict())
    assert restored.id == task.id
    assert restored.title == task.title
    assert restored.priority == task.priority
    assert restored.status == task.status
