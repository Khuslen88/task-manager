"""FastAPI web server for the task manager."""

import sys
import os

# Allow imports from project root (src/*)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.task import Task, VALID_PRIORITIES
from src import storage

app = FastAPI(title="Task Manager")

# Serve the frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


# ── Models ──────────────────────────────────────────────────────────────────

class TaskIn(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"


class TaskPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/tasks")
def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, q: Optional[str] = None):
    tasks = storage.load_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if q:
        kw = q.lower()
        tasks = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]
    return [t.to_dict() for t in tasks]


@app.post("/tasks", status_code=201)
def add_task(body: TaskIn):
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if body.priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {body.priority}")
    task_id = storage.next_id()
    task = Task(id=task_id, title=body.title.strip(), description=body.description,
                due_date=body.due_date, priority=body.priority)
    tasks = storage.load_tasks()
    tasks.append(task)
    storage.save_tasks(tasks)
    return task.to_dict()


@app.patch("/tasks/{task_id}/done")
def mark_done(task_id: int):
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.status = "done"
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            return t.to_dict()
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")


@app.patch("/tasks/{task_id}")
def edit_task(task_id: int, body: TaskPatch):
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            if body.title is not None:
                t.title = body.title.strip()
            if body.description is not None:
                t.description = body.description
            if body.due_date is not None:
                t.due_date = body.due_date
            if body.priority is not None:
                if body.priority not in VALID_PRIORITIES:
                    raise HTTPException(status_code=400, detail=f"Invalid priority: {body.priority}")
                t.priority = body.priority
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            return t.to_dict()
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    tasks = storage.load_tasks()
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    storage.save_tasks(remaining)
