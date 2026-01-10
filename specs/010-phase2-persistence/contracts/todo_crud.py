# Database Contract: Todo CRUD Operations

**Version**: 1.0
**Date**: 2026-01-07
**Feature**: Persistence Layer (010-phase2-persistence)

## Overview

This document defines the internal contract between the backend API layer and the persistence layer. All database operations must conform to this contract.

## CRUD Operations

### 1. Get Todos

```python
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
```

**SQL Query**:
```sql
SELECT * FROM todo
WHERE ($1 IS NULL OR status = $1)
  AND ($2 IS NULL OR to_tsvector('english', title) @@ to_tsquery('english', $2))
ORDER BY created_at DESC
LIMIT $3 OFFSET $4;
```

### 2. Get Todo By ID

```python
def get_todo_by_id(session: Session, todo_id: int) -> Optional[Todo]:
    """Retrieve a single todo by ID.

    Args:
        session: Database session
        todo_id: Unique identifier of todo

    Returns:
        Todo object if found, None otherwise
    """
```

**SQL Query**:
```sql
SELECT * FROM todo WHERE id = $1;
```

### 3. Create Todo

```python
def create_todo(session: Session, todo: TodoCreate) -> Todo:
    """Create a new todo.

    Args:
        session: Database session
        todo: TodoCreate schema with title and optional description

    Returns:
        Created Todo object with auto-generated ID and timestamps

    Raises:
        ValidationError: If title is empty or exceeds 200 characters
        ValidationError: If description exceeds 1000 characters
    """
```

**SQL Query**:
```sql
INSERT INTO todo (title, description, status, created_at, updated_at)
VALUES ($1, $2, 'pending', NOW(), NOW())
RETURNING *;
```

### 4. Update Todo

```python
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
```

**SQL Query**:
```sql
UPDATE todo
SET title = COALESCE($1, title),
    description = COALESCE($2, description),
    status = COALESCE($3, status),
    updated_at = NOW()
WHERE id = $4
RETURNING *;
```

### 5. Delete Todo

```python
def delete_todo(session: Session, todo_id: int) -> bool:
    """Delete a todo by ID.

    Args:
        session: Database session
        todo_id: Unique identifier of todo to delete

    Returns:
        True if todo was deleted, False if not found
    """
```

**SQL Query**:
```sql
DELETE FROM todo WHERE id = $1 RETURNING id;
```

### 6. Update Todo Status

```python
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
```

**SQL Query**:
```sql
UPDATE todo
SET status = $1, updated_at = NOW()
WHERE id = $2
RETURNING *;
```

## Schema Contracts

### TodoBase (Create/Update)

```python
class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
```

**Validation Rules**:
- title: Required, 1-200 characters
- description: Optional, 0-1000 characters

### TodoCreate

```python
class TodoCreate(TodoBase):
    pass
```

**Contract**: Used when creating new todos. Status auto-sets to 'pending'.

### TodoUpdate

```python
class TodoUpdate(TodoBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = None
```

**Contract**: Used when updating existing todos. Only provided fields are updated.

### TodoResponse

```python
class TodoResponse(SQLModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
```

**Contract**: Returned from all read operations.

## Error Contracts

### ValidationError

```python
class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
```

**Usage**: Invalid title length, invalid status, missing required fields

### TodoNotFoundError

```python
class TodoNotFoundError(Exception):
    """Raised when todo with specified ID does not exist."""

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
```

**Usage**: `get_todo_by_id()`, `update_todo()`, `delete_todo()` when ID not found

### DatabaseError

```python
class DatabaseError(Exception):
    """Raised when database operation fails."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
```

**Usage**: Connection failures, constraint violations, transaction failures

## Transaction Contract

### Session Management

```python
def get_session() -> Generator[Session, None, None]:
    """Provide database session with automatic cleanup.

    Yields:
        Session object for database operations

    Guarantees:
        - Session is automatically committed on success
        - Session is automatically rolled back on error
        - Session is closed after use
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
```

**Usage**: All database operations must use this dependency for FastAPI.

## Performance Contract

### Query Time Limits

| Operation | Max Time (p95) | Max Time (p99) |
|-----------|----------------|----------------|
| get_todos (filtered, 10k records) | 100ms | 200ms |
| get_todos (search, 10k records) | 200ms | 500ms |
| get_todo_by_id | 5ms | 10ms |
| create_todo | 10ms | 20ms |
| update_todo | 10ms | 20ms |
| delete_todo | 10ms | 20ms |
| update_todo_status | 5ms | 10ms |

### Connection Pool Limits

- Min connections: 5 (pool_size)
- Max connections: 15 (pool_size + max_overflow)
- Wait timeout: 30 seconds
- Recycle time: 3600 seconds

## Testing Contract

### Unit Tests

- Model validation tests (Pydantic constraints)
- CRUD function tests (mock session)
- Error handling tests (exceptions)

### Integration Tests

- All CRUD operations with real database
- Transaction rollback on error
- Connection pool behavior
- Migration upgrade and rollback

### Performance Tests

- 10,000 record dataset
- Measure query times
- Verify index usage (EXPLAIN ANALYZE)

## Versioning

This contract is versioned to track changes:

- **v1.0**: Initial CRUD operations (2026-01-07)

Future versions must maintain backwards compatibility where possible.
