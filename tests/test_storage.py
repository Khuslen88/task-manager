"""Tests for storage utilities."""

import os
import pytest
from src.task import Task
from src import storage


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    """Redirect storage to a temp file so tests don't touch real tasks.json."""
    fake_path = str(tmp_path / "tasks.json")
    monkeypatch.setattr(storage, "DATA_FILE", fake_path)
    yield fake_path


def test_load_tasks_empty_when_no_file():
    tasks = storage.load_tasks()
    assert tasks == []


def test_save_and_load_roundtrip():
    tasks = [Task(id=1, title="Test task")]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert len(loaded) == 1
    assert loaded[0].title == "Test task"
    assert loaded[0].id == 1


def test_next_id_starts_at_one():
    assert storage.next_id() == 1


def test_next_id_increments():
    first = storage.next_id()
    second = storage.next_id()
    assert second == first + 1


def test_next_id_never_reuses_after_delete():
    id1 = storage.next_id()
    tasks = [Task(id=id1, title="A")]
    storage.save_tasks(tasks)
    # delete all tasks
    storage.save_tasks([])
    id2 = storage.next_id()
    assert id2 != id1  # counter kept moving even though tasks were deleted


def test_save_multiple_tasks():
    tasks = [Task(id=i, title=f"Task {i}") for i in range(1, 4)]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert len(loaded) == 3
    assert [t.id for t in loaded] == [1, 2, 3]


def test_atomic_write_produces_valid_file(tmp_path, monkeypatch):
    fake_path = str(tmp_path / "tasks.json")
    monkeypatch.setattr(storage, "DATA_FILE", fake_path)
    storage.save_tasks([Task(id=1, title="Atomic test")])
    # No .tmp files should remain
    leftover = [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    assert leftover == []
