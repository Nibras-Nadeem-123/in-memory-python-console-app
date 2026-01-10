# ADR-005: Phase 2 Full-Stack Web Architecture

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** Spec-Driven Todo System - Phase 2
- **Context:** Transforming Phase 1 (console-based, in-memory application) into a full-stack web application with persistence while maintaining Phase 1 code unchanged.

## Executive Summary

This ADR documents the architectural transformation from a console-based in-memory application (Phase 1) to a full-stack web application with persistence (Phase 2). The architecture prioritizes clear separation of concerns, technology choices optimized for rapid development and scalability, and strict isolation of Phase 2 code to preserve the Phase 1 implementation.

---

## Decision

Adopt a **monolithic full-stack architecture** with the following technology stack and organizational structure:

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Next.js | 14+ (App Router) | React framework with SSR, routing, and API routes |
| **Backend** | FastAPI | 0.104+ | High-performance Python async API framework |
| **ORM** | SQLModel | 0.0.14+ | SQLAlchemy + Pydantic hybrid for type-safe models |
| **Database** | PostgreSQL | 15+ (hosted on Neon) | Serverless Postgres with auto-scaling |
| **API Protocol** | REST | HTTP/1.1 | Standard REST endpoints with JSON payloads |
| **Type Safety** | TypeScript | 5.0+ | Static typing for frontend |
| **Type Safety** | Python typing | 3.11+ | Static typing for backend |

### Directory Structure

```
├── core/                    # Shared domain logic (business rules, validation)
│   ├── models.py           # Domain models (reused by both phases)
│   └── validation.py       # Business logic validation
├── phase1/                 # Console app (unchanged, frozen)
│   ├── main.py
│   └── ...
├── phase2/                 # Full-stack web app (isolated)
│   ├── backend/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── api/            # Route handlers
│   │   ├── db.py           # Database connection
│   │   └── models.py       # SQLModel schemas (extend core)
│   ├── frontend/
│   │   ├── app/            # Next.js App Router
│   │   ├── components/     # React components
│   │   └── lib/            # API client utilities
│   └── shared/             # TypeScript types shared with backend
└── history/                # ADRs, PHRs, docs
```

### Architectural Principles

| Principle | Description |
|-----------|-------------|
| **Backend owns business logic** | Frontend is UI-only; all validation, rules, and state management in backend |
| **Shared domain layer** | `core/` contains reusable business logic and models |
| **Strict phase isolation** | Phase 1 remains untouched; Phase 2 lives in `phase2/` |
| **Type-safe contracts** | TypeScript types mirror Pydantic models for API contracts |
| **No hidden state** | All state is persisted in database; no frontend state beyond UI |

---

## Consequences

### Positive

| Benefit | Impact |
|---------|--------|
| **Rapid development** | Next.js + FastAPI provide excellent DX and built-in tooling |
| **Type safety** | End-to-end type safety (Pydantic → TypeScript) catches errors early |
| **Clear separation** | Backend logic isolated from frontend concerns |
| **Preserved Phase 1** | Console app remains as reference/alternative implementation |
| **Scalable infrastructure** | Neon auto-scales; architecture supports future growth |
| **Modern stack** | Well-supported, widely-used technologies with strong communities |

### Negative

| Drawback | Mitigation |
|----------|------------|
| **Technology switching** | Two languages (Python/TypeScript) increases cognitive load | Use type-sharing tooling; document API contracts clearly |
| **Code duplication** | Models defined in both Python (SQLModel) and TypeScript | Use code generation (e.g., `pydantic-to-typescript`) if duplication becomes problematic |
| **Monolithic constraints** | Single deployment for both frontend/backend | Planned future migration to microservices if needed (explicitly out of scope for Phase 2) |
| **Vendor lock-in (Neon)** | Tied to Neon's serverless Postgres | Database schema is standard PostgreSQL; migration path exists |
| **Learning curve** | New stack for team (Next.js App Router, FastAPI, SQLModel) | Documentation and training materials included |

---

## Alternatives Considered

### Alternative A: Next.js API Routes (Pythonless)

**Description:** Use Next.js for both frontend and backend (JavaScript/TypeScript only).

**Rejected Because:**
- Loses Python ecosystem benefits (FastAPI's async performance, Pydantic validation)
- Requires rewriting all business logic from scratch
- SQLModel provides superior type safety vs Prisma/TypeORM
- Python is already established in Phase 1 and `core/`

### Alternative B: SPA with Separate Backend (Vite + FastAPI)

**Description:** Use Vite for frontend, deploy separately from FastAPI backend.

**Rejected Because:**
- Next.js App Router provides superior DX for full-stack development
- Lost benefits of SSR and API routes co-location
- Increased deployment complexity (two separate services)
- No SSR capabilities (important for SEO and performance)

### Alternative C: GraphQL API

**Description:** Replace REST with GraphQL for frontend-backend communication.

**Rejected Because:**
- Overkill for Phase 2 requirements (simple CRUD operations)
- Adds complexity (resolvers, schema stitching, caching)
- REST is simpler to debug and reason about
- Can be introduced later if complex querying needs emerge

### Alternative D: MongoDB with Mongoose/PyMongo

**Description:** Use NoSQL database instead of PostgreSQL.

**Rejected Because:**
- Todo system has structured, relational data requirements
- SQLModel provides superior type safety and validation
- PostgreSQL on Neon offers excellent performance and serverless scaling
- SQL databases better enforce data integrity constraints

### Alternative E: Background Jobs with Celery/Redis

**Description:** Add background job processing from the start.

**Rejected Because:**
- Explicitly out of scope for Phase 2 (defined as non-goal)
- Adds operational complexity (Redis, worker processes)
- Not required for synchronous CRUD operations
- Can be added later if needed (clear extension path)

---

## API Design

### REST Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| GET | `/api/todos` | List all todos | - | `Todo[]` |
| POST | `/api/todos` | Create todo | `{ title, description? }` | `Todo` |
| GET | `/api/todos/{id}` | Get single todo | - | `Todo` |
| PUT | `/api/todos/{id}` | Update todo | `{ title?, description?, status? }` | `Todo` |
| DELETE | `/api/todos/{id}` | Delete todo | - | `{ success: true }` |
| PATCH | `/api/todos/{id}/status` | Update status only | `{ status: 'pending'|'completed' }` | `Todo` |

### Data Model

```python
# SQLModel (backend)
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")  # "pending" or "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

```typescript
// TypeScript (frontend)
interface Todo {
  id: number;
  title: string;
  description?: string;
  status: "pending" | "completed";
  created_at: string;
  updated_at: string;
}
```

### Error Handling

| Status Code | Condition | Response Body |
|-------------|-----------|---------------|
| 200 | Success | `{ data: T }` |
| 201 | Created | `{ data: T }` |
| 400 | Validation error | `{ error: string, details: ValidationError[] }` |
| 404 | Not found | `{ error: string }` |
| 500 | Server error | `{ error: string, trace_id: string }` |

---

## Deployment Strategy

### Phase 2 Deployment

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend (Next.js) | Vercel | Automatic deployments from Git, SSR support |
| Backend (FastAPI) | Render or Railway | Containerized deployment, auto-scaling |
| Database | Neon | Serverless Postgres, auto-scaling, branching |
| API Communication | HTTPS | CORS configured for frontend origin |

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | Neon connection string | `postgresql://user:pass@ep-neon/db` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://your-app.vercel.app` |
| `LOG_LEVEL` | Logging verbosity | `INFO` or `DEBUG` |

---

## Migration Path from Phase 1 to Phase 2

### Current State (Phase 1)
- In-memory Python list for todos
- Console-based UI with CLI commands
- Single-file architecture (`main.py`)

### Target State (Phase 2)
- PostgreSQL-backed persistence
- Web UI with React/Next.js
- Full-stack architecture with API layer

### Data Migration (If Needed)
```python
# Phase 1 data export (if migrating existing todos)
todos = phase1_app.get_all_todos()
with open('phase1_data.json', 'w') as f:
    json.dump([todo.dict() for todo in todos], f)

# Phase 2 data import
from phase2.backend.db import Session
from phase2.backend.models import Todo

with Session() as session:
    for todo_data in json.load(open('phase1_data.json')):
        session.add(Todo(**todo_data))
    session.commit()
```

---

## Non-Functional Requirements

### Performance

| Metric | Target | Implementation |
|--------|--------|----------------|
| API response time | < 100ms (p95) | FastAPI async, database indexing, connection pooling |
| Page load time | < 1s (p95) | Next.js SSR, static optimization, code splitting |
| Concurrent users | 1000+ | Neon auto-scaling, stateless API design |

### Reliability

| Requirement | Implementation |
|-------------|----------------|
| **Database backups** | Neon automatic backups, point-in-time recovery |
| **Error logging** | Structured logging (JSON) with trace IDs |
| **Graceful degradation** | Frontend shows error states, retry logic |
| **Idempotency** | Safe retry for failed requests (PUT/DELETE) |

### Security

| Concern | Implementation |
|---------|----------------|
| **Input validation** | Pydantic models on backend, TypeScript types on frontend |
| **SQL injection** | SQLModel uses parameterized queries by default |
| **CORS** | Explicit allowed origins in FastAPI config |
| **Rate limiting** | FastAPI middleware (optional for Phase 2) |
| **Secrets management** | Environment variables, no hardcoded credentials |

---

## Success Criteria

- [ ] Phase 1 code remains completely unchanged
- [ ] Phase 2 code is isolated in `phase2/` directory
- [ ] Frontend communicates with backend only via REST API
- [ ] All business logic lives in backend (validation, state changes)
- [ ] Database schema is versioned and migratable
- [ ] TypeScript types match Python Pydantic models
- [ ] API documentation available (FastAPI auto-docs at `/docs`)
- [ ] Deployment instructions complete and tested
- [ ] Tests cover API endpoints and critical business logic

---

## Future Extensions (Out of Scope for Phase 2)

| Extension | Consideration |
|-----------|---------------|
| **Microservices** | Can extract services if scaling needs emerge |
| **Background jobs** | Add Celery/RQ for async tasks if needed |
| **GraphQL** | Replace REST if complex querying requirements emerge |
| **Real-time updates** | Add WebSockets/Server-Sent Events if needed |
| **AI agents** | Future phase to integrate intelligence layer |
| **Authentication** | Add JWT/OAuth if multi-user support needed |

---

## References

- Constitution: `.specify/memory/constitution.md`
- ADR-003: Spec-Driven Development System Architecture
- ADR-004: Phase 2 Intelligence Integration
- Phase 2 Spec: `specs/phase2-web-interface/spec.md` (if exists)
- Phase 2 Plan: `specs/phase2-web-interface/plan.md` (if exists)

---

**ADR Version:** 1.0.0
**Accepted Date:** 2026-01-07
**Amendments:** None
**Next Review:** After Phase 2 implementation completion
