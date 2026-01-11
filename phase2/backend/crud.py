from typing import List, Optional
from sqlmodel import Session, select, col
from models import Todo, TodoCreate, TodoUpdate
from exceptions import TodoNotFoundError, ValidationError


def get_todos(
    session: Session,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Todo]:
    """Retrieve todos with optional filtering and search.

    Args:
        session: Database session
        status_filter: Filter by status ('pending', 'completed', or None for all)
        search_query: Search title by keyword (case-insensitive)
        limit: Maximum number of results (default 50, max 1000)
        offset: Number of results to skip (for pagination)

    Returns:
        List of Todo objects matching criteria, ordered by created_at DESC

    Raises:
        ValueError: If limit > 1000 or offset < 0
    """
    if limit > 1000:
        raise ValueError("Limit cannot exceed 1000")
    if offset < 0:
        raise ValueError("Offset cannot be negative")

    statement = select(Todo).order_by(col(Todo.created_at).desc())

    if status_filter and status_filter in ['pending', 'completed']:
        statement = statement.where(Todo.status == status_filter)

    if search_query:
        # Simple case-insensitive search in title
        statement = statement.where(Todo.title.ilike(f"%{search_query}%"))

    statement = statement.offset(offset).limit(limit)

    results = session.exec(statement)
    return list(results.all())


def get_todo_by_id(session: Session, todo_id: int) -> Optional[Todo]:
    """Retrieve a single todo by ID.

    Args:
        session: Database session
        todo_id: Unique identifier of todo

    Returns:
        Todo object if found, None otherwise
    """
    return session.get(Todo, todo_id)


def create_todo(session: Session, todo: TodoCreate) -> Todo:
    """Create a new todo.

    Args:
        session: Database session
        todo: TodoCreate schema with title and optional description

    Returns:
        Created Todo object with auto-generated ID and timestamps

    Raises:
        ValidationError: If title is empty or exceeds 200 characters
    """
    if not todo.title or not todo.title.strip():
        raise ValidationError("title", "Title is required")
    if len(todo.title) > 200:
        raise ValidationError("title", "Title must be at most 200 characters")
    if todo.description and len(todo.description) > 1000:
        raise ValidationError("description", "Description must be at most 1000 characters")

    # Create Todo with status defaulting to 'pending'
    db_todo = Todo.model_validate({
        **todo.model_dump(),
        "status": "pending"
    })

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


def update_todo(session: Session, todo_id: int, todo: TodoUpdate) -> Optional[Todo]:
    """Update an existing todo.

    Args:
        session: Database session
        todo_id: Unique identifier of todo to update
        todo: TodoUpdate schema with fields to update (all optional)

    Returns:
        Updated Todo object if found and updated, None otherwise

    Raises:
        ValidationError: If title or description validation fails
        ValidationError: If status is not 'pending' or 'completed'
    """
    db_todo = get_todo_by_id(session, todo_id)
    if not db_todo:
        return None

    # Validate if fields are provided
    if todo.title is not None:
        if not todo.title.strip():
            raise ValidationError("title", "Title is required")
        if len(todo.title) > 200:
            raise ValidationError("title", "Title must be at most 200 characters")
        db_todo.title = todo.title

    if todo.description is not None:
        if len(todo.description) > 1000:
            raise ValidationError("description", "Description must be at most 1000 characters")
        db_todo.description = todo.description

    if todo.status is not None:
        if todo.status not in ['pending', 'completed']:
            raise ValidationError("status", "Status must be 'pending' or 'completed'")
        db_todo.status = todo.status

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


def delete_todo(session: Session, todo_id: int) -> bool:
    """Delete a todo by ID.

    Args:
        session: Database session
        todo_id: Unique identifier of todo to delete

    Returns:
        True if todo was deleted, False if not found
    """
    db_todo = get_todo_by_id(session, todo_id)
    if not db_todo:
        return False

    session.delete(db_todo)
    session.commit()
    return True


def update_todo_status(session: Session, todo_id: int, status: str) -> Optional[Todo]:
    """Update only the status of a todo.

    Args:
        session: Database session
        todo_id: Unique identifier of todo
        status: New status ('pending' or 'completed')

    Returns:
        Updated Todo object if found, None otherwise

    Raises:
        ValidationError: If status is not 'pending' or 'completed'
    """
    if status not in ['pending', 'completed']:
        raise ValidationError("status", "Status must be 'pending' or 'completed'")

    return update_todo(session, todo_id, TodoUpdate(status=status))
