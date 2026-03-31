# Task Manager

A command-line task management tool built with Python and Click. Create, organize, and track tasks from your terminal with persistent JSON storage.

## Features

- Add tasks with title, description, due date, and priority
- List all tasks or filter by status/priority
- Mark tasks as done
- Edit task fields
- Delete tasks with confirmation
- Search tasks by keyword
- Color-coded terminal output
- Data persists between sessions via `tasks.json`

## Requirements

- Python 3.9+
- pip

## Setup

```bash
# Clone the repository
git clone https://github.com/Khuslen88/task-manager.git
cd task-manager

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run commands using `python -m src.cli` or set up an alias:

```bash
alias task="python -m src.cli"
```

### Add a task

```bash
task add "Buy groceries"
task add "Submit report" --description "Q1 summary" --due 2026-04-01 --priority high
```

### List tasks

```bash
task list                        # all tasks
task list --status todo          # only incomplete
task list --status done          # only completed
task list --priority high        # filter by priority
```

### Complete a task

```bash
task done 1
```

### Edit a task

```bash
task edit 1 --title "New title"
task edit 2 --priority low --due 2026-05-01
```

### Delete a task

```bash
task delete 3    # prompts for confirmation
```

### Search tasks

```bash
task search "groceries"
```

## Priority Levels

| Level    | Color  |
|----------|--------|
| `high`   | Red    |
| `medium` | Yellow |
| `low`    | Cyan   |

## Data Storage

Tasks are stored in `tasks.json` at the project root. Override the path with the `TASK_DATA_FILE` environment variable:

```bash
TASK_DATA_FILE=~/mytasks.json task list
```

## Running Tests

```bash
pytest
```

## Project Structure

```
task-manager/
├── src/
│   ├── task.py       # Task dataclass and validation
│   ├── storage.py    # JSON persistence layer
│   └── cli.py        # Click CLI commands
├── tests/
│   ├── test_task.py
│   ├── test_storage.py
│   └── test_cli.py
├── web/
│   ├── app.py        # FastAPI REST API
│   └── static/       # Web UI
├── requirements.txt
└── tasks.json        # Generated at runtime
```

## Web Interface

A FastAPI-based web interface is also available:

```bash
pip install fastapi uvicorn
uvicorn web.app:app --reload
```

Then open `http://localhost:8000` in your browser.

## Dependencies

- [Click](https://click.palletsprojects.com/) — CLI framework
- [FastAPI](https://fastapi.tiangolo.com/) — Web API framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [pytest](https://pytest.org/) — Testing
