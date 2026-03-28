import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="Todo List Sample")

BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"
INDEX_FILE = BASE_DIR / "templates" / "index.html"


class TodoCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class TodoItem(TodoCreate):
    id: int
    completed: bool = False


def read_todos() -> list[dict]:
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]", encoding="utf-8")
        return []

    raw = TODO_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    return json.loads(raw)


def write_todos(todos: list[dict]) -> None:
    TODO_FILE.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.get("/", response_class=HTMLResponse)
def serve_index() -> HTMLResponse:
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))


@app.get("/todos", response_model=list[TodoItem])
def get_todos() -> list[dict]:
    return read_todos()


@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoCreate) -> dict:
    todos = read_todos()
    next_id = max((item["id"] for item in todos), default=0) + 1
    new_todo = TodoItem(id=next_id, student_id=todo.student_id, name=todo.name)
    todos.append(new_todo.model_dump())
    write_todos(todos)
    return new_todo.model_dump()


@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoItem) -> dict:
    todos = read_todos()
    for index, item in enumerate(todos):
        if item["id"] == todo_id:
            updated_todo = todo.model_copy(update={"id": todo_id})
            todos[index] = updated_todo.model_dump()
            write_todos(todos)
            return updated_todo.model_dump()
    raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    todos = read_todos()
    filtered_todos = [item for item in todos if item["id"] != todo_id]
    if len(filtered_todos) == len(todos):
        raise HTTPException(status_code=404, detail="Todo not found")
    write_todos(filtered_todos)
