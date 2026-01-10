# Feature Specification: Phase 2 Backend for Spec-Driven Todo System

**Feature Branch**: `008-phase2-backend`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "Define the backend specification for Phase 2. Backend Responsibilities: Expose REST API endpoints, Validate requests, Execute spec-driven todo operations, Persist data using SQLModel. Define: API endpoints, Request/response schemas, Database models, Error handling rules. Constraints: No frontend logic, No direct database access from frontend"

## User Scenarios & Testing

### User Story 1 - CRUD Operations via REST API (Priority: P1)

Frontend clients can perform all todo operations (Create, Read, Update, Delete) through REST API endpoints, with all business logic and validation handled on the backend.

**Why this priority**: Core API functionality required for the web application to work. Without these endpoints, the frontend cannot interact with todo data.

**Independent Test**: Can be tested using HTTP client tools (curl, Postman, HTTPie) by making requests to each endpoint and verifying responses match expected schemas. No frontend required.

**Acceptance Scenarios**:

1. **Given** empty database, **When** client POSTs `/api/todos` with `{ "title": "New task" }`, **Then** system returns 201 with created Todo object containing auto-generated ID
2. **Given** 3 todos exist in database, **When** client GETs `/api/todos`, **Then** system returns 200 with array of 3 Todo objects ordered by created_at desc
3. **Given** todo with ID 1 exists, **When** client GETs `/api/todos/1`, **Then** system returns 200 with specific Todo object
4. **Given** todo with ID 1 exists, **When** client PUTs `/api/todos/1` with `{ "status": "completed" }`, **Then** system returns 200 with updated Todo object
5. **Given** todo with ID 1 exists, **When** client DELETEs `/api/todos/1`, **Then** system returns 200 with success confirmation and todo is removed from database

---

### User Story 2 - Request Validation and Error Handling (Priority: P1)

Backend validates all incoming requests according to schema rules and returns structured error responses with actionable information.

**Why this priority**: Essential for API reliability and security. Prevents invalid data from corrupting database and provides clear feedback to frontend.

**Independent Test**: Send malformed requests (missing required fields, invalid data types, constraint violations) and verify error responses are structured and informative.

**Acceptance Scenarios**:

1. **Given** POST to `/api/todos`, **When** request body is empty `{}`, **Then** system returns 400 with error details: "Field required: title"
2. **Given** POST to `/api/todos`, **When** title exceeds 200 characters, **Then** system returns 400 with error: "title must be at most 200 characters"
3. **Given** GET request to `/api/todos/999`, **When** todo does not exist, **Then** system returns 404 with error: "Todo not found"
4. **Given** POST to `/api/todos`, **When** request body contains unknown field `{ "title": "Task", "invalid_field": "data" }`, **Then** system returns 400 with error ignoring unknown field
5. **Given** PUT to `/api/todos/1`, **When** status is not "pending" or "completed", **Then** system returns 400 with error: "status must be 'pending' or 'completed'"

---

### User Story 3 - Status Management Endpoint (Priority: P2)

Frontend clients can efficiently update just the status of a todo item using a dedicated PATCH endpoint.

**Why this priority**: Common UI pattern (checkbox to complete task) that should be optimized. Not critical for MVP but improves UX.

**Independent Test**: Send PATCH requests to update status and verify only status field changes.

**Acceptance Scenarios**:

1. **Given** todo with status "pending", **When** client PATCHes `/api/todos/1/status` with `{ "status": "completed" }`, **Then** system returns 200 with updated Todo where only status changed
2. **Given** todo with status "completed", **When** client PATCHes `/api/todos/1/status` with `{ "status": "pending" }`, **Then** system returns 200 with updated Todo status reverted to pending
3. **Given** PATCH request to `/api/todos/1/status` with `{ "status": "invalid" }`, **Then** system returns 400 with validation error

---

### User Story 4 - Filtering and Querying (Priority: P2)

Frontend clients can filter todos by status and search by keyword using query parameters.

**Why this priority**: Essential for usable task management with multiple items. Users need to find specific tasks quickly.

**Independent Test**: Create various todos with different statuses and titles, then use query parameters to verify filtering works correctly.

**Acceptance Scenarios**:

1. **Given** 10 todos (5 pending, 5 completed), **When** client GETs `/api/todos?status=pending`, **Then** system returns 200 with array of 5 pending todos only
2. **Given** 10 todos (5 pending, 5 completed), **When** client GETs `/api/todos?status=completed`, **Then** system returns 200 with array of 5 completed todos only
3. **Given** todos with titles containing "documentation", **When** client GETs `/api/todos?search=documentation`, **Then** system returns 200 with todos where title contains search term
4. **Given** 100 todos in database, **When** client GETs `/api/todos`, **Then** system returns 200 with default limit (50) and includes pagination metadata
5. **Given** todos with both "pending" status and search term matches, **When** client GETs `/api/todos?status=pending&search=task`, **Then** system returns todos matching both filters (AND logic)

---

### Edge Cases

- What happens when database connection fails during request?
- How does system handle concurrent updates to same todo (race conditions)?
- What if request body is not valid JSON?
- How does system handle SQL injection attempts?
- What happens when database is empty and client requests filtering?
- How does system handle extremely large description fields (near limit)?
- What if client sends request with incorrect Content-Type header?
- How does system handle timestamp field manipulation by client?
- What happens when DELETE request succeeds but subsequent GET returns 404?
- How does system handle requests with malformed query parameters?

## Requirements

### Functional Requirements

- **FR-001**: Backend MUST expose REST API with base path `/api`
- **FR-002**: System MUST support HTTP methods: GET, POST, PUT, DELETE, PATCH
- **FR-003**: System MUST validate all request bodies using Pydantic schemas
- **FR-004**: System MUST persist todo data to PostgreSQL database using SQLModel
- **FR-005**: System MUST return structured JSON responses for all endpoints
- **FR-006**: System MUST return appropriate HTTP status codes (200, 201, 400, 404, 500)
- **FR-007**: System MUST auto-generate unique IDs for new todos (integer, auto-increment)
- **FR-008**: System MUST auto-generate timestamps for created_at and updated_at fields
- **FR-009**: System MUST support filtering todos by status (pending/completed)
- **FR-010**: System MUST support searching todos by title keyword
- **FR-011**: System MUST validate title length (1-200 characters)
- **FR-012**: System MUST validate description length (max 1000 characters)
- **FR-013**: System MUST restrict status field to "pending" or "completed"
- **FR-014**: System MUST update updated_at timestamp on any modification
- **FR-015**: System MUST handle database transactions with proper rollback on error
- **FR-016**: System MUST provide OpenAPI/Swagger documentation at `/docs` endpoint
- **FR-017**: System MUST configure CORS to allow frontend origin only
- **FR-018**: System MUST log all requests with response status and duration
- **FR-019**: System MUST implement idempotent operations for PUT and DELETE
- **FR-020**: System MUST support pagination for list endpoints (limit/offset)

### Non-Functional Requirements

- **NFR-001**: API response time MUST be < 100ms (p95) for CRUD operations
- **NFR-002**: API MUST handle at least 1000 concurrent requests
- **NFR-003**: System MUST be asynchronous (async/await) for optimal performance
- **NFR-004**: System MUST use connection pooling for database connections
- **NFR-005**: System MUST be stateless (no in-memory session storage)
- **NFR-006**: All API endpoints MUST be idempotent where appropriate
- **NFR-007**: System MUST be type-safe (Python typing annotations)
- **NFR-008**: Error responses MUST be consistent and machine-readable
- **NFR-009**: System MUST support graceful degradation (partial failures don't crash entire API)
- **NFR-010**: Database schema MUST be versioned and migratable

### Key Entities

#### Todo (Database Model)
Represents a todo item persisted in database.
- `id`: Optional[int] - Primary key, auto-generated
- `title`: str - Required, min 1 char, max 200 chars
- `description`: Optional[str] - Optional, max 1000 chars
- `status`: str - Required, enum "pending" or "completed", default "pending"
- `created_at`: datetime - Auto-generated on creation, UTC
- `updated_at`: datetime - Auto-generated on update, UTC

#### TodoCreate (Request Schema)
Schema for creating new todo.
- `title`: str - Required, 1-200 chars
- `description`: Optional[str] - Optional, max 1000 chars

#### TodoUpdate (Request Schema)
Schema for updating existing todo (all fields optional).
- `title`: Optional[str] - 1-200 chars if provided
- `description`: Optional[str] - Max 1000 chars if provided
- `status`: Optional[str] - "pending" or "completed" if provided

#### TodoStatusUpdate (Request Schema)
Schema for updating only status.
- `status`: str - Required, "pending" or "completed"

#### TodoResponse (Response Schema)
Schema for todo responses.
- `id`: int - Unique identifier
- `title`: str - Todo title
- `description`: Optional[str] - Todo description
- `status`: str - "pending" or "completed"
- `created_at`: str - ISO 8601 datetime string
- `updated_at`: str - ISO 8601 datetime string

#### ErrorResponse (Error Schema)
Schema for error responses.
- `error`: str - Human-readable error message
- `details`: Optional[List[ValidationError]] - Detailed validation errors
- `trace_id`: Optional[str] - Unique request identifier for debugging

### API Endpoints

| Method | Path | Purpose | Request Schema | Response Schema |
|--------|------|---------|----------------|-----------------|
| GET | `/api/todos` | List all todos with optional filters | Query params: `status`, `search`, `limit`, `offset` | `TodoResponse[]` |
| POST | `/api/todos` | Create new todo | `TodoCreate` | `TodoResponse` |
| GET | `/api/todos/{id}` | Get single todo by ID | Path param: `id` (int) | `TodoResponse` |
| PUT | `/api/todos/{id}` | Update todo (partial or full) | Path: `id`, Body: `TodoUpdate` | `TodoResponse` |
| DELETE | `/api/todos/{id}` | Delete todo by ID | Path param: `id` (int) | `{ success: true }` |
| PATCH | `/api/todos/{id}/status` | Update todo status only | Path: `id`, Body: `TodoStatusUpdate` | `TodoResponse` |

### Error Handling Rules

| Status Code | Condition | Response Schema |
|-------------|-----------|-----------------|
| 200 | Success (GET, PUT, PATCH) | `TodoResponse` or `TodoResponse[]` |
| 201 | Resource created (POST) | `TodoResponse` |
| 400 | Validation error or bad request | `ErrorResponse` with `details` array |
| 404 | Resource not found | `ErrorResponse` with error message |
| 500 | Server error | `ErrorResponse` with `trace_id` |

**Error Response Examples**:

400 - Validation Error:
```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "title",
      "message": "Field required"
    }
  ]
}
```

404 - Not Found:
```json
{
  "error": "Todo with id 999 not found"
}
```

500 - Server Error:
```json
{
  "error": "Internal server error",
  "trace_id": "abc123xyz"
}
```

### Constraints

- **C-001**: NO frontend logic in backend - all UI code belongs in frontend
- **C-002**: NO direct database access from frontend - all queries via API only
- **C-003**: NO session management - API must be stateless
- **C-004**: NO authentication in Phase 2 (single-user system)
- **C-005**: SQLModel MUST be used for all database operations (no raw SQL)
- **C-006**: All datetime fields MUST use UTC timezone
- **C-007**: All validation MUST use Pydantic (no manual validation)
- **C-008**: NO business logic in frontend - all validation/rules in backend
- **C-009**: CORS MUST be restricted to frontend origin only
- **C-010**: Database credentials MUST come from environment variables (never hardcoded)

### Success Criteria

1. All CRUD operations accessible via REST API with correct HTTP semantics
2. 100% of requests validated with Pydantic schemas before processing
3. All error responses are structured JSON with appropriate status codes
4. API response time < 100ms (p95) for all CRUD operations
5. Database operations use SQLModel with proper connection pooling
6. API documentation available at `/docs` endpoint
7. Unit test coverage ≥ 80% for API endpoints
8. Integration tests verify end-to-end API workflows
9. Database schema is migratable with clear versioning
10. No direct database access possible from frontend (all via API)

## Out of Scope (Phase 2 Backend)

- Authentication and authorization (single-user system)
- Multi-user support or permissions
- Background job processing (synchronous operations only)
- WebSocket or real-time updates
- File upload/download
- Email notifications
- Rate limiting (can be added as middleware if needed)
- API versioning beyond v1
- GraphQL (REST only)
- Advanced search (full-text search, filtering by multiple fields)
- Task categories, tags, or priorities beyond status
- Due dates, reminders, or scheduling
- Undo/redo functionality
- Audit logging beyond basic request logs
- Analytics or metrics endpoints

## Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.104+ |
| ORM | SQLModel | 0.0.14+ |
| Database | PostgreSQL | 15+ (Neon) |
| Python Version | Python | 3.11+ |
| Validation | Pydantic | 2.0+ |
| Async Runtime | asyncio | Built-in |

### Directory Structure

```
phase2/backend/
├── main.py              # FastAPI application entry point
├── api/
│   ├── __init__.py
│   ├── deps.py          # Dependency injection (db session)
│   └── todos.py         # Todo API routes
├── db.py                # Database connection and session management
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── config.py            # Configuration and settings
└── exceptions.py        # Custom exception handlers
```

### Request Processing Flow

```
Client Request
    │
    ▼
FastAPI Router
    │
    ▼
Pydantic Schema Validation
    │
    ├─> Validation Error → 400 Response
    │
    ▼
Dependency Injection (DB Session)
    │
    ▼
Business Logic Handler
    │
    ├─> Not Found → 404 Response
    │
    ▼
SQLModel Database Operation
    │
    ├─> Database Error → 500 Response
    │
    ▼
Response Serialization
    │
    ▼
HTTP Response (200/201)
```

### Database Schema

```sql
CREATE TABLE todo (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'completed'))
);

CREATE INDEX idx_todo_status ON todo(status);
CREATE INDEX idx_todo_created_at ON todo(created_at DESC);
```

### Integration with Phase 1

The backend reuses business logic concepts from Phase 1 but adapts them for web API:

- **Phase 1**: In-memory task list with console commands
- **Phase 2 Backend**: Persistent database with REST API endpoints

**Shared Concepts**:
- Todo entity structure (id, title, status, created_at)
- Operations: add, list, update, delete, complete
- Validation: title length, status enum

**Differences**:
- Phase 2 adds persistence (PostgreSQL)
- Phase 2 uses structured JSON instead of CLI text
- Phase 2 has filtering and searching via query parameters
- Phase 2 uses HTTP semantics instead of command parsing

## Dependencies

- FastAPI 0.104+
- SQLModel 0.0.14+
- uvicorn (ASGI server)
- psycopg2-binary (PostgreSQL adapter)
- pydantic 2.0+
- alembic (database migrations)

## Risks

1. **Database Connection Pool Exhaustion**: High concurrent requests may exhaust pool
   - Mitigation: Configure appropriate pool size; implement connection timeout

2. **Race Conditions**: Concurrent updates to same todo
   - Mitigation: Use database transactions with proper isolation levels

3. **Schema Migration Issues**: Database schema changes may break existing data
   - Mitigation: Use Alembic migrations with rollback support

4. **API Version Conflicts**: Frontend and backend may get out of sync
   - Mitigation: Document API contracts; use OpenAPI schema as contract

5. **Performance Degradation**: Large result sets may slow responses
   - Mitigation: Implement pagination; add database indexes

6. **SQL Injection**: If raw SQL used instead of SQLModel
   - Mitigation: Use only SQLModel ORM operations; never construct raw SQL queries

---

## References

- **ADR-005**: Phase 2 Full-Stack Web Architecture
- **Spec 006**: Todo Console App (Phase 1)
- **Spec 007**: Phase 2 Intelligence Model
- **Constitution**: `.specify/memory/constitution.md`
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
