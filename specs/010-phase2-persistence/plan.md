# Implementation Plan: Phase 2 Persistence Layer

**Branch**: `010-phase2-persistence` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-phase2-persistence/spec.md`

## Summary

Implement PostgreSQL database persistence layer for Phase 2 todo system using SQLModel ORM with Neon cloud database, Alembic migrations, and environment-based configuration. The layer provides database schema, connection pooling, and migration workflow while keeping Phase 1 code untouched.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLModel 0.0.14+, Alembic, psycopg2-binary
**Storage**: PostgreSQL 15+ on Neon (serverless)
**Testing**: pytest with test database fixtures
**Target Platform**: Linux server (backend API)
**Project Type**: Web application backend
**Performance Goals**: Read <100ms p95, Write <200ms p95, 10k records query <100ms
**Constraints**: <200ms p95 response time, connection pool supports 100 concurrent connections, UTC timezone for all timestamps
**Scale/Scope**: Single table (todo), 4 indexes, connection pool of 5+10 overflow, typical deployment 1k users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reusable Intelligence**: N/A - This is infrastructure/database layer, not intelligence framework component
- **II. Intelligence-First**: N/A - No planning/reasoning layer, pure persistence
- **III. Domain-Agnostic & Modular**: PASS - SQLModel models are modular, no hardcoded todo business logic in persistence layer
- **IV. Skill-Based**: N/A - Persistence infrastructure, not skill functionality
- **V. Safety & Introspectability**: PASS - Transaction rollback, error logging, connection validation, migration history tracking
- **VI. Frozen Intelligence Architecture**: PASS - Does not touch frozen intelligence modules (`src/intelligence/*`), extends through new code in isolated location

## Project Structure

### Documentation (this feature)

```text
specs/010-phase2-persistence/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (SQLModel schemas)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
phase2/backend/
├── db.py                    # Database connection and session management
├── models.py                # SQLModel models (Todo table)
├── migrations/              # Alembic migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
├── config.py                # Database configuration (environment variables)
└── tests/
    ├── test_db.py            # Database connection tests
    ├── test_models.py        # Model validation tests
    └── test_migrations.py    # Migration tests

# Phase 1 remains untouched (frozen)
phase1/
├── main.py
├── executor.py
└── ...

# Shared domain logic (if needed in future)
core/
├── __init__.py
└── models.py                # Shared domain models (future)
```

**Structure Decision**: Monolithic backend structure for Phase 2, isolated from Phase 1. Phase 2 code lives in `phase2/backend/` directory with clear separation from Phase 1 (`phase1/`). Future shared logic would go in `core/` but Phase 2 persistence is backend-specific and doesn't require cross-phase sharing yet.

## Phase 0: Research

**Goal**: Resolve all technical unknowns and establish best practices

### Research Tasks

1. **SQLModel + Alembic Integration Pattern**
   - Decision: Use Alembic with `alembic revision --autogenerate` for schema changes
   - Rationale: Autogenerate reduces manual SQL, SQLAlchemy/Alembic integration well-established
   - Alternatives considered: Manual SQL migrations (error-prone), other ORMs (SQLModel chosen per spec)

2. **Neon PostgreSQL Specific Configuration**
   - Decision: Use connection string with sslmode=require, pool_size=5, max_overflow=10
   - Rationale: Neon requires SSL, standard pool sizes for web workloads
   - Alternatives considered: Larger pools (wastes resources), smaller pools (connection exhaustion)

3. **Text Search Implementation**
   - Decision: PostgreSQL's built-in full-text search with GIN index on title
   - Rationale: Native PostgreSQL feature, no external dependencies, efficient for keyword search
   - Alternatives considered: LIKE pattern matching (slow), external search service (overkill for Phase 2)

4. **Migration Execution Strategy**
   - Decision: Automatic migration on startup in development, manual in production
   - Rationale: Developer convenience vs. production safety
   - Alternatives considered: Always manual (slows development), always auto (risky for production)

5. **Connection Pool Configuration**
   - Decision: pool_size=5, max_overflow=10, pool_recycle=3600s, pool_pre_ping=True
   - Rationale: Balances connection efficiency with resource usage, prevents stale connections
   - Alternatives considered: Larger pools (exhausts database limits), no recycling (stale connections)

### Research Output

See `research.md` for detailed findings and decision rationale.

## Phase 1: Design & Contracts

**Goal**: Define data model and contracts

### 1. Data Model (data-model.md)

**Todo Entity**:
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Database Schema**:
- Table: `todo`
- Columns: id, title, description, status, created_at, updated_at
- Constraints: PRIMARY KEY (id), CHECK (status IN ('pending', 'completed'))
- Indexes: (status), (created_at DESC), (status, created_at DESC), GIN (title to_tsvector)

**State Transitions**: pending → completed (one-way, no return)

### 2. API Contracts (contracts/)

**Internal Contract (Backend → Database)**:
- `get_todos(status_filter: str, search_query: str) -> List[Todo]`
- `get_todo_by_id(id: int) -> Todo | None`
- `create_todo(todo: TodoCreate) -> Todo`
- `update_todo(id: int, todo: TodoUpdate) -> Todo | None`
- `delete_todo(id: int) -> bool`
- `update_todo_status(id: int, status: str) -> Todo | None`

**Schema Files**:
- `contracts/todo_base.sql` - Base table schema
- `contracts/indexes.sql` - Index definitions
- `contracts/constraints.sql` - Constraint definitions

### 3. Agent Context Update

Update agent context to include SQLModel, Alembic, PostgreSQL technologies.

### 4. Quickstart Guide (quickstart.md)

Developer onboarding steps for persistence layer setup.

## Phase 2: Implementation Steps

**Goal**: Build and test persistence layer

### Step 1: Project Setup (1 day)

1. Create `phase2/backend/` directory structure
2. Initialize Alembic: `alembic init migrations`
3. Configure `.env.example` with database URL template
4. Set up `pydantic-settings` for configuration management
5. Add requirements to `requirements.txt`: sqlmodel, alembic, psycopg2-binary, pydantic-settings

**Acceptance**: Directory structure in place, Alembic initialized, `.env.example` committed

### Step 2: Database Models (1 day)

1. Create `phase2/backend/models.py`:
   - Define `Todo` SQLModel class
   - Add Pydantic validation for field constraints
   - Define `TodoCreate`, `TodoUpdate`, `TodoResponse` schemas
2. Create `phase2/backend/config.py`:
   - `DatabaseSettings` class with pydantic-settings
   - Load `DATABASE_URL`, `POOL_SIZE`, `MAX_OVERFLOW` from environment
3. Write unit tests for model validation

**Acceptance**: Model passes all validation tests, constraints enforced by Pydantic

### Step 3: Database Connection (1 day)

1. Create `phase2/backend/db.py`:
   - Create database engine with connection pooling
   - Create `get_session()` dependency for FastAPI (or context manager for CLI)
   - Add connection pool configuration
   - Implement `check_connection()` for startup validation
2. Configure Alembic `env.py` to use engine from `db.py`
3. Write tests for connection pooling and validation

**Acceptance**: Connection pool handles 100 concurrent connections, startup validation works

### Step 4: Initial Migration (1 day)

1. Create initial schema migration: `alembic revision --autogenerate -m "initial schema"`
2. Review and customize migration:
   - Add check constraint for status enum
   - Add indexes: status, created_at DESC, composite (status, created_at DESC)
   - Add GIN index for full-text search on title
3. Add rollback operations to migration
4. Write migration tests:
   - Test upgrade on fresh database
   - Test rollback
   - Test idempotency (run upgrade twice)

**Acceptance**: Migration applies successfully, rollback works, indexes created

### Step 5: CRUD Operations (2 days)

1. Create `phase2/backend/crud.py`:
   - Implement `get_todos()` with filtering and search
   - Implement `get_todo_by_id()`
   - Implement `create_todo()`
   - Implement `update_todo()`
   - Implement `delete_todo()`
   - Implement `update_todo_status()`
2. Add transaction handling with rollback on error
3. Write integration tests for all CRUD operations
4. Performance test with 10,000 records

**Acceptance**: All CRUD operations work, performance <100ms p95 for reads, <200ms p95 for writes

### Step 6: Error Handling & Logging (1 day)

1. Add exception classes in `phase2/backend/exceptions.py`:
   - `DatabaseConnectionError`
   - `MigrationError`
   - `TodoNotFoundError`
2. Add logging to all database operations
3. Add connection failure detection and retry logic
4. Write error handling tests

**Acceptance**: Errors logged appropriately, connection failures handled gracefully

### Step 7: Environment Configuration (0.5 day)

1. Create `.env.example` template
2. Document all environment variables
3. Create configuration validation on startup
4. Write tests for configuration loading

**Acceptance**: Application fails fast with clear error if `DATABASE_URL` missing

### Step 8: Integration Testing (1 day)

1. Create test database fixture for pytest
2. Write end-to-end tests:
   - Full CRUD workflow
   - Concurrent access scenarios
   - Migration rollback scenarios
   - Connection pool exhaustion
3. Performance benchmarks

**Acceptance**: All integration tests pass, performance meets requirements

### Step 9: Documentation (0.5 day)

1. Complete `quickstart.md` with setup instructions
2. Add docstrings to all functions
3. Create migration workflow documentation
4. Update README with persistence layer details

**Acceptance**: Documentation complete and tested

## Phase 3: Integration Milestones

**Goal**: Verify persistence layer integration with Phase 2 backend

### Milestone 1: Database Initialization

**Date**: After Step 4
**Verification**:
- Fresh Neon database can be initialized
- All tables and indexes created
- Migration history tracked correctly

**Success Criteria**: `alembic upgrade head` succeeds on fresh database

### Milestone 2: CRUD Operations

**Date**: After Step 5
**Verification**:
- All CRUD operations functional
- Filtering and search working
- Performance benchmarks met

**Success Criteria**: 10,000 record query <100ms, CRUD operations passing tests

### Milestone 3: Backend Integration

**Date**: After Step 8
**Verification**:
- Backend API can use persistence layer
- API endpoints connected to database
- Error handling works end-to-end

**Success Criteria**: Backend API tests pass with real database

## Testing Strategy

### Unit Tests
- Model validation tests
- Configuration loading tests
- Connection pool tests
- Exception handling tests

### Integration Tests
- CRUD operation tests with test database
- Migration upgrade/rollback tests
- Concurrent access tests
- Performance benchmarks

### Test Coverage
- Target: 90%+ code coverage for persistence layer
- All database operations tested
- All error paths tested

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Migration failure | Medium | High | Test migrations on production-like data, maintain rollback scripts |
| Connection pool exhaustion | Low | High | Monitor pool utilization, configure alerts |
| Performance degradation | Low | Medium | Regular performance testing, index usage monitoring |
| Schema drift | Low | Medium | Restrict database access, audit schema changes |
| Data loss during migration | Low | Critical | Backup before migrations, test rollback procedures |

## Dependencies

- Neon PostgreSQL database account
- Python 3.11+ environment
- Backend spec (008-phase2-backend) for API contracts
- ADR-005 for architecture decisions

## Out of Scope

- Multi-tenant database schema
- Database replication
- Read replicas
- Caching layer (Redis)
- Advanced search beyond basic text search
- Data archival
- Foreign key relationships (single table only)

## Success Criteria

1. Database initialization completes in <10 seconds
2. All migrations apply in <30 seconds
3. Query response time <100ms p95 with 10,000 records
4. Connection pool handles 100 concurrent connections
5. Migrations can be rolled back without data loss
6. Test coverage ≥90%
7. Phase 1 code completely untouched
8. All database credentials in environment variables only
9. Documentation complete and tested
10. Integration tests with backend API passing

## Next Steps

After this plan is approved:
1. Execute Phase 0: Research (already complete)
2. Execute Phase 1: Design & Contracts
3. Generate tasks via `/sp.tasks`
4. Begin implementation

---

**Plan Status**: Draft
**Review Required**: Yes
**Approval Authority**: Architect
