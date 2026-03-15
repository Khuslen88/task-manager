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


def test_next_id_empty():
    assert storage.next_id([]) == 1


def test_next_id_with_tasks():
    tasks = [Task(id=1, title="A"), Task(id=3, title="B")]
    assert storage.next_id(tasks) == 4


def test_save_multiple_tasks():
    tasks = [Task(id=i, title=f"Task {i}") for i in range(1, 4)]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert len(loaded) == 3
    assert [t.id for t in loaded] == [1, 2, 3]
