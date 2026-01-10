# Quickstart: Phase 2 Persistence Layer

**Date**: 2026-01-07
**Feature**: Persistence Layer (010-phase2-persistence)

## Prerequisites

- Python 3.11+ installed
- Neon PostgreSQL account (free tier works)
- Git repository cloned
- Virtual environment created

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd phase2/backend
pip install sqlmodel alembic psycopg2-binary pydantic-settings pytest pytest-asyncio
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Neon database URL
```

```env
# .env
DATABASE_URL=postgresql+psycopg2://user:password@ep-neon-host/dbname?sslmode=require
LOG_LEVEL=INFO
```

### 3. Initialize Database

```bash
alembic upgrade head
```

### 4. Verify Connection

```bash
python -c "from db import check_connection; check_connection()"
```

**Expected output**: "Database connection successful"

## Development Workflow

### Adding a New Migration

```bash
alembic revision --autogenerate -m "description of changes"
# Review the generated migration in migrations/versions/
alembic upgrade head
```

### Running Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Viewing Database

```bash
# Connect to Neon via psql
psql $DATABASE_URL

# View tables
\d todo

# View data
SELECT * FROM todo ORDER BY created_at DESC;
```

## Common Operations

### Create a Todo (Python REPL)

```python
from sqlmodel import Session, create_engine, select
from models import Todo, TodoCreate
from db import get_session

with Session(engine) as session:
    todo_create = TodoCreate(title="Test todo", description="Test description")
    todo = Todo.from_orm(todo_create)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    print(f"Created todo with ID: {todo.id}")
```

### Query Todos

```python
from sqlmodel import Session, select
from models import Todo
from db import get_session

with Session(engine) as session:
    todos = session.exec(select(Todo).order_by(Todo.created_at.desc())).all()
    for todo in todos:
        print(f"{todo.id}: {todo.title} ({todo.status})")
```

### Update Todo Status

```python
from sqlmodel import Session, select
from models import Todo
from db import get_session

with Session(engine) as session:
    todo = session.exec(select(Todo).where(Todo.id == 1)).one()
    todo.status = "completed"
    session.add(todo)
    session.commit()
```

## Troubleshooting

### Connection Error

**Problem**: "could not connect to server"

**Solution**:
1. Check DATABASE_URL in .env
2. Verify Neon database is active
3. Ensure SSL mode is required

### Migration Error

**Problem**: "Target database is not up to date"

**Solution**:
```bash
alembic upgrade head
```

### Pool Exhaustion

**Problem**: "Connection pool exhausted"

**Solution**:
1. Increase `max_overflow` in db.py
2. Check for connection leaks (unclosed sessions)
3. Reduce concurrent operations

## Next Steps

After setting up persistence:

1. Implement CRUD operations in `crud.py`
2. Create API endpoints in `api/todos.py`
3. Add error handling in `exceptions.py`
4. Write comprehensive tests
5. Integrate with backend FastAPI application

## Resources

- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Neon Docs](https://neon.tech/docs)
