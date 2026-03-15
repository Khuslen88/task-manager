"""FastAPI web server for the task manager."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.task import Task, VALID_PRIORITIES, VALID_STATUSES
from src import storage

app = FastAPI(title="Task Manager")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


# ── Models ───────────────────────────────────────────────────────────────────

class TaskIn(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"
    assignee: str = ""
    tags: List[str] = []


class TaskPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None


class StatusIn(BaseModel):
    status: str


class CommentIn(BaseModel):
    text: str
    author: str = "Me"


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/tasks")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    q: Optional[str] = None,
):
    tasks = storage.load_tasks()
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if assignee:
        tasks = [t for t in tasks if t.assignee.lower() == assignee.lower()]
    if q:
        kw = q.lower()
        tasks = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()
                 or any(kw in tag.lower() for tag in t.tags)]
    return [t.to_dict() for t in tasks]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            return t.to_dict()
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")


@app.post("/tasks", status_code=201)
def add_task(body: TaskIn):
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    if body.priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {body.priority}")
    task_id = storage.next_id()
    task = Task(
        id=task_id,
        title=body.title.strip(),
        description=body.description,
        due_date=body.due_date,
        priority=body.priority,
        assignee=body.assignee,
        tags=body.tags,
    )
    tasks = storage.load_tasks()
    tasks.append(task)
    storage.save_tasks(tasks)
    return task.to_dict()


@app.patch("/tasks/{task_id}")
def edit_task(task_id: int, body: TaskPatch):
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            if body.title is not None:
                if not body.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty.")
                t.title = body.title.strip()
            if body.description is not None:
                t.description = body.description
            if body.due_date is not None:
                t.due_date = body.due_date if body.due_date else None
            if body.priority is not None:
                if body.priority not in VALID_PRIORITIES:
                    raise HTTPException(status_code=400, detail=f"Invalid priority: {body.priority}")
                t.priority = body.priority
            if body.status is not None:
                if body.status not in VALID_STATUSES:
                    raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")
                t.status = body.status
            if body.assignee is not None:
                t.assignee = body.assignee
            if body.tags is not None:
                t.tags = body.tags
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            return t.to_dict()
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")


@app.patch("/tasks/{task_id}/done")
def mark_done(task_id: int):
    """Kept for CLI backward compatibility."""
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.status = "done"
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


@app.post("/tasks/{task_id}/comments", status_code=201)
def add_comment(task_id: int, body: CommentIn):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Comment text cannot be empty.")
    tasks = storage.load_tasks()
    for t in tasks:
        if t.id == task_id:
            comment = {
                "id": len(t.comments) + 1,
                "author": body.author or "Me",
                "text": body.text.strip(),
                "at": datetime.now().isoformat(timespec="seconds"),
            }
            t.comments.append(comment)
            t.updated_at = datetime.now().isoformat(timespec="seconds")
            storage.save_tasks(tasks)
            return comment
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
