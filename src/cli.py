"""CLI entry point using Click."""

from datetime import datetime

import click

from src.task import Task, VALID_PRIORITIES
from src import storage


@click.group()
def cli():
    """A simple CLI task manager."""


@cli.command()
@click.argument("title")
@click.option("--description", "-d", default="", help="Task description.")
@click.option("--due", default=None, help="Due date (YYYY-MM-DD).")
@click.option(
    "--priority", "-p",
    default="medium",
    type=click.Choice(sorted(VALID_PRIORITIES)),
    help="Priority level.",
)
def add(title, description, due, priority):
    """Add a new task."""
    task_id = storage.next_id()
    task = Task(id=task_id, title=title, description=description, due_date=due, priority=priority)
    tasks = storage.load_tasks()
    tasks.append(task)
    storage.save_tasks(tasks)
    click.echo(f"Added task {task_id}: {title}")


@cli.command("list")
@click.option("--status", type=click.Choice(["todo", "done"]), default=None, help="Filter by status.")
@click.option(
    "--priority", "-p",
    type=click.Choice(sorted(VALID_PRIORITIES)),
    default=None,
    help="Filter by priority.",
)
def list_tasks(status, priority):
    """List tasks."""
    tasks = storage.load_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if not tasks:
        click.echo("No tasks found.")
        return
    for t in tasks:
        check = "x" if t.status == "done" else " "
        due = f"  due: {t.due_date}" if t.due_date else ""
        click.echo(f"[{check}] {t.id}: {t.title}  [{t.priority}]{due}")


@cli.command()
@click.argument("task_id", type=int)
def done(task_id):
    """Mark a task as done."""
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.status = "done"
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            click.echo(f"Marked task {task_id} as done.")
            return
    click.echo(f"Task {task_id} not found.", err=True)


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id):
    """Delete a task."""
    tasks = storage.load_tasks()
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        click.echo(f"Task {task_id} not found.", err=True)
        return
    storage.save_tasks(remaining)
    click.echo(f"Deleted task {task_id}.")


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", default=None)
@click.option("--description", "-d", default=None)
@click.option("--due", default=None)
@click.option("--priority", "-p", type=click.Choice(sorted(VALID_PRIORITIES)), default=None)
def edit(task_id, title, description, due, priority):
    """Edit a task."""
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            if title is not None:
                t.title = title
            if description is not None:
                t.description = description
            if due is not None:
                t.due_date = due
            if priority is not None:
                t.priority = priority
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            click.echo(f"Updated task {task_id}.")
            return
    click.echo(f"Task {task_id} not found.", err=True)


@cli.command()
@click.argument("keyword")
def search(keyword):
    """Search tasks by keyword."""
    tasks = storage.load_tasks()
    kw = keyword.lower()
    results = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]
    if not results:
        click.echo("No matching tasks.")
        return
    for t in results:
        check = "x" if t.status == "done" else " "
        click.echo(f"[{check}] {t.id}: {t.title}  [{t.priority}]")


if __name__ == "__main__":
    cli()
