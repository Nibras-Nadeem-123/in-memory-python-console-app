from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from models import Todo, TodoCreate, TodoUpdate, TodoResponse, TodoStatusUpdate
from crud import get_todos, get_todo_by_id, create_todo as crud_create_todo, update_todo, delete_todo, update_todo_status
from api.deps import get_db_session
from exceptions import TodoNotFoundError, ValidationError, DatabaseError

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=List[TodoResponse])
def list_todos(
    status: Optional[str] = Query(None, description="Filter by status: pending, completed"),
    search: Optional[str] = Query(None, description="Search by title keyword"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_db_session)
):
    """List all todos with optional filtering and search."""
    try:
        todos = get_todos(session, status, search, limit, offset)
        return todos
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    todo: TodoCreate,
    session: Session = Depends(get_db_session)
):
    """Create a new todo."""
    try:
        db_todo = crud_create_todo(session, todo)
        return TodoResponse.model_validate(db_todo)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={
            "error": "Validation failed",
            "field": e.field,
            "message": e.message
        })


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    session: Session = Depends(get_db_session)
):
    """Get a single todo by ID."""
    todo = get_todo_by_id(session, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return TodoResponse.model_validate(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo_endpoint(
    todo_id: int,
    todo: TodoUpdate,
    session: Session = Depends(get_db_session)
):
    """Update an existing todo."""
    try:
        db_todo = update_todo(session, todo_id, todo)
        if not db_todo:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return TodoResponse.model_validate(db_todo)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={
            "error": "Validation failed",
            "field": e.field,
            "message": e.message
        })


@router.delete("/{todo_id}")
def delete_todo_endpoint(
    todo_id: int,
    session: Session = Depends(get_db_session)
):
    """Delete a todo by ID."""
    success = delete_todo(session, todo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return {"success": True}


@router.patch("/{todo_id}/status", response_model=TodoResponse)
def update_status(
    todo_id: int,
    status_update: TodoStatusUpdate,
    session: Session = Depends(get_db_session)
):
    """Update only the status of a todo."""
    try:
        db_todo = update_todo_status(session, todo_id, status_update.status)
        if not db_todo:
            raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
        return TodoResponse.model_validate(db_todo)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={
            "error": "Validation failed",
            "field": e.field,
            "message": e.message
        })
