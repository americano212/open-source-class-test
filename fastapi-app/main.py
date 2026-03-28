import json
from json import JSONDecodeError
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="Todo List Sample")

BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"
INDEX_FILE = BASE_DIR / "templates" / "index.html"


class TodoBase(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=120)


class TodoCreate(TodoBase):
    completed: bool = False


class TodoReplace(TodoBase):
    completed: bool = False


class TodoUpdate(BaseModel):
    student_id: str | None = Field(default=None, min_length=1, max_length=20)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    completed: bool | None = None


class TodoItem(TodoBase):
    id: int
    completed: bool = False


def read_todos() -> list[dict]:
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]", encoding="utf-8")
        return []

    raw = TODO_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Todo data file is corrupted",
        ) from exc

    return data


def write_todos(todos: list[dict]) -> None:
    TODO_FILE.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_summary(todos: list[dict]) -> dict[str, int]:
    total = len(todos)
    completed = sum(1 for item in todos if item.get("completed"))
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
    }


def get_todo_index(todos: list[dict], todo_id: int) -> int:
    for index, item in enumerate(todos):
        if item["id"] == todo_id:
            return index
    raise HTTPException(status_code=404, detail="Todo not found")


@app.get("/", response_class=HTMLResponse)
def serve_index() -> HTMLResponse:
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoItem])
def get_todos() -> list[dict]:
    return read_todos()


@app.get("/todos/summary")
def get_todo_summary() -> dict[str, int]:
    return build_summary(read_todos())


@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoCreate) -> dict:
    todos = read_todos()
    next_id = max((item["id"] for item in todos), default=0) + 1
    new_todo = TodoItem(
        id=next_id,
        student_id=todo.student_id,
        name=todo.name,
        completed=todo.completed,
    )
    todos.append(new_todo.model_dump())
    write_todos(todos)
    return new_todo.model_dump()


@app.put("/todos/{todo_id}", response_model=TodoItem)
def replace_todo(todo_id: int, todo: TodoReplace) -> dict:
    todos = read_todos()
    todo_index = get_todo_index(todos, todo_id)
    updated_todo = TodoItem(id=todo_id, **todo.model_dump())
    todos[todo_index] = updated_todo.model_dump()
    write_todos(todos)
    return updated_todo.model_dump()


@app.patch("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoUpdate) -> dict:
    changes = todo.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided")

    todos = read_todos()
    todo_index = get_todo_index(todos, todo_id)
    updated_todo = TodoItem.model_validate(
        {
            **todos[todo_index],
            **changes,
            "id": todo_id,
        }
    )
    todos[todo_index] = updated_todo.model_dump()
    write_todos(todos)
    return updated_todo.model_dump()


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    todos = read_todos()
    filtered_todos = [item for item in todos if item["id"] != todo_id]
    if len(filtered_todos) == len(todos):
        raise HTTPException(status_code=404, detail="Todo not found")
    write_todos(filtered_todos)
