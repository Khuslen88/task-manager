"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from src.cli import cli
from src import storage


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "tasks.json"))


@pytest.fixture
def runner():
    return CliRunner()


def test_add_task(runner):
    result = runner.invoke(cli, ["add", "Buy milk"])
    assert result.exit_code == 0
    assert "Added task 1" in result.output


def test_add_task_with_options(runner):
    result = runner.invoke(cli, ["add", "Study", "--priority", "high", "--due", "2026-04-01"])
    assert result.exit_code == 0
    tasks = storage.load_tasks()
    assert tasks[0].priority == "high"
    assert tasks[0].due_date == "2026-04-01"


def test_list_empty(runner):
    result = runner.invoke(cli, ["list"])
    assert "No tasks found" in result.output


def test_list_shows_tasks(runner):
    runner.invoke(cli, ["add", "Task A"])
    runner.invoke(cli, ["add", "Task B"])
    result = runner.invoke(cli, ["list"])
    assert "Task A" in result.output
    assert "Task B" in result.output


def test_list_filter_by_status(runner):
    runner.invoke(cli, ["add", "Task A"])
    runner.invoke(cli, ["add", "Task B"])
    runner.invoke(cli, ["done", "1"])
    result = runner.invoke(cli, ["list", "--status", "todo"])
    assert "Task A" not in result.output
    assert "Task B" in result.output


def test_done_marks_task(runner):
    runner.invoke(cli, ["add", "Finish report"])
    result = runner.invoke(cli, ["done", "1"])
    assert "Marked task 1 as done" in result.output
    tasks = storage.load_tasks()
    assert tasks[0].status == "done"


def test_done_unknown_id(runner):
    result = runner.invoke(cli, ["done", "99"])
    assert "not found" in result.output


def test_delete_task(runner):
    runner.invoke(cli, ["add", "Temp task"])
    result = runner.invoke(cli, ["delete", "1"])
    assert "Deleted task 1" in result.output
    assert storage.load_tasks() == []


def test_edit_task(runner):
    runner.invoke(cli, ["add", "Old title"])
    result = runner.invoke(cli, ["edit", "1", "--title", "New title"])
    assert "Updated task 1" in result.output
    assert storage.load_tasks()[0].title == "New title"


def test_search_finds_match(runner):
    runner.invoke(cli, ["add", "Buy groceries"])
    runner.invoke(cli, ["add", "Walk the dog"])
    result = runner.invoke(cli, ["search", "groceries"])
    assert "Buy groceries" in result.output
    assert "Walk the dog" not in result.output


def test_search_no_match(runner):
    runner.invoke(cli, ["add", "Buy groceries"])
    result = runner.invoke(cli, ["search", "python"])
    assert "No matching tasks" in result.output
