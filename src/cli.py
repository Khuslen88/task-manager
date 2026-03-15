"""CLI entry point using Click."""

import re
from datetime import datetime

import click

from src.task import Task, VALID_PRIORITIES
from src import storage

PRIORITY_COLORS = {"high": "red", "medium": "yellow", "low": "cyan"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_due(ctx, param, value):
    if value and not DATE_RE.match(value):
        raise click.BadParameter("Due date must be in YYYY-MM-DD format.")
    return value


def _fmt_priority(priority: str) -> str:
    return click.style(f"[{priority}]", fg=PRIORITY_COLORS.get(priority, "white"))


def _fmt_task(t: Task) -> str:
    check = click.style("x", fg="green") if t.status == "done" else " "
    title = click.style(t.title, dim=(t.status == "done"))
    due = click.style(f"  due: {t.due_date}", fg="magenta") if t.due_date else ""
    return f"[{check}] {t.id}: {title}  {_fmt_priority(t.priority)}{due}"


@click.group()
def cli():
    """Task — a simple CLI task manager.

    \b
    Quick start:
      task add "Buy milk" --priority high
      task list
      task done 1
    """


@cli.command()
@click.argument("title")
@click.option("--description", "-d", default="", help="Optional task description.")
@click.option("--due", default=None, callback=_validate_due, help="Due date in YYYY-MM-DD format.")
@click.option(
    "--priority", "-p",
    default="medium",
    type=click.Choice(sorted(VALID_PRIORITIES)),
    show_default=True,
    help="Priority level.",
)
def add(title, description, due, priority):
    """Add a new task.

    \b
    Examples:
      task add "Buy milk"
      task add "Submit report" --due 2026-04-01 --priority high
    """
    if not title.strip():
        raise click.UsageError("Title cannot be empty.")
    task_id = storage.next_id()
    task = Task(id=task_id, title=title.strip(), description=description, due_date=due, priority=priority)
    tasks = storage.load_tasks()
    tasks.append(task)
    storage.save_tasks(tasks)
    click.echo(click.style(f"✓ Added task {task_id}: {title}", fg="green"))


@cli.command("list")
@click.option("--status", type=click.Choice(["todo", "done"]), default=None, help="Filter by status.")
@click.option(
    "--priority", "-p",
    type=click.Choice(sorted(VALID_PRIORITIES)),
    default=None,
    help="Filter by priority.",
)
def list_tasks(status, priority):
    """List tasks, optionally filtered.

    \b
    Examples:
      task list
      task list --status todo
      task list --priority high
    """
    tasks = storage.load_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if not tasks:
        click.echo(click.style("No tasks found.", dim=True))
        return
    for t in tasks:
        click.echo(_fmt_task(t))


@cli.command()
@click.argument("task_id", type=int)
def done(task_id):
    """Mark a task as done.

    \b
    Example:
      task done 3
    """
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            if t.status == "done":
                click.echo(click.style(f"Task {task_id} is already done.", fg="yellow"))
                return
            t.status = "done"
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            click.echo(click.style(f"✓ Marked task {task_id} as done.", fg="green"))
            return
    click.echo(click.style(f"Error: task {task_id} not found.", fg="red"), err=True)


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def delete(task_id):
    """Delete a task (asks for confirmation).

    \b
    Example:
      task delete 2
    """
    tasks = storage.load_tasks()
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        click.echo(click.style(f"Error: task {task_id} not found.", fg="red"), err=True)
        return
    storage.save_tasks(remaining)
    click.echo(click.style(f"Deleted task {task_id}.", fg="yellow"))


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title", default=None, help="New title.")
@click.option("--description", "-d", default=None, help="New description.")
@click.option("--due", default=None, callback=_validate_due, help="New due date (YYYY-MM-DD).")
@click.option("--priority", "-p", type=click.Choice(sorted(VALID_PRIORITIES)), default=None, help="New priority.")
def edit(task_id, title, description, due, priority):
    """Edit a task's fields.

    \b
    Example:
      task edit 1 --title "New title" --priority low
    """
    if all(v is None for v in [title, description, due, priority]):
        raise click.UsageError("Provide at least one field to update.")
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            if title is not None:
                if not title.strip():
                    raise click.UsageError("Title cannot be empty.")
                t.title = title.strip()
            if description is not None:
                t.description = description
            if due is not None:
                t.due_date = due
            if priority is not None:
                t.priority = priority
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            click.echo(click.style(f"✓ Updated task {task_id}.", fg="green"))
            return
    click.echo(click.style(f"Error: task {task_id} not found.", fg="red"), err=True)


@cli.command()
@click.argument("keyword")
def search(keyword):
    """Search tasks by keyword in title or description.

    \b
    Example:
      task search "milk"
    """
    if not keyword.strip():
        raise click.UsageError("Search keyword cannot be empty.")
    tasks = storage.load_tasks()
    kw = keyword.lower()
    results = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]
    if not results:
        click.echo(click.style("No matching tasks.", dim=True))
        return
    for t in results:
        click.echo(_fmt_task(t))


if __name__ == "__main__":
    cli()
