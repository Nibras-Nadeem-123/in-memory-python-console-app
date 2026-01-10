# Implementation Plan: Phase 2 Full-Stack Integration

**Branch**: `011-phase2-integration` | **Date**: 2026-01-07
**Spec**: [spec.md](./spec.md)
**Dependencies**: Spec 008 (backend), Spec 009 (frontend), Spec 010 (persistence)

## Summary

Coordinate and integrate all Phase 2 components (backend API, frontend UI, database persistence) into a cohesive full-stack web application while maintaining strict isolation from Phase 1 code and establishing shared domain logic in `core/`.

## Technical Context

**Backend**: Python 3.11+, FastAPI 0.104+, SQLModel, PostgreSQL 15+ (Neon)
**Frontend**: Next.js 14+ (App Router), TypeScript 5.0+, React 18+
**Database**: PostgreSQL with Alembic migrations
**Testing**: pytest (backend), Jest/Playwright (frontend)
**Performance**: <100ms API response p95, <2s page load
**Architecture**: Monolithic full-stack, API-driven, stateless backend

## Constitution Check

**PASS** - All principles satisfied:
- No modifications to frozen intelligence layer
- Phase 1 code completely isolated and untouched
- Modular architecture with clear separation
- No hardcoded domain logic in infrastructure
- Error handling and logging throughout

## Repository Structure

```
├── phase1/                          # FROZEN - Console app
│   ├── main.py
│   ├── executor.py
│   ├── parser.py
│   └── ...

├── phase2/                          # NEW - Full-stack web app
│   ├── backend/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── db.py                    # Database connection
│   │   ├── models.py                # SQLModel models
│   │   ├── crud.py                  # Database operations
│   │   ├── config.py                # Configuration
│   │   ├── api/
│   │   │   ├── deps.py              # Dependencies
│   │   │   └── todos.py             # Todo endpoints
│   │   ├── migrations/              # Alembic migrations
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   └── tests/
│   │
│   └── frontend/
│       ├── app/                     # Next.js App Router
│       │   ├── page.tsx             # Home page
│       │   ├── todos/
│       │   │   ├── [id]/            # Todo detail
│       │   │   └── new/             # Create todo
│       │   ├── layout.tsx           # Root layout
│       │   └── globals.css          # Global styles
│       ├── components/
│       │   ├── TodoList.tsx
│       │   ├── TodoItem.tsx
│       │   ├── TodoForm.tsx
│       │   ├── FilterBar.tsx
│       │   └── ErrorBanner.tsx
│       ├── lib/
│       │   ├── api.ts               # API client
│       │   └── types.ts             # TypeScript types
│       └── tests/
│
├── core/                            # SHARED - Domain logic
│   ├── __init__.py
│   ├── models.py                    # Shared domain models
│   └── validation.py                # Business rules
│
├── src/intelligence/                # FROZEN - Intelligence framework
│   ├── context.py
│   ├── runtime.py
│   └── ...
│
└── .env.example                     # Environment variables template
```

## Phase 1: Repository Structure Setup (1 day)

### 1.1 Create Phase 2 Directories

```bash
mkdir -p phase2/backend/{api,migrations/versions,tests}
mkdir -p phase2/frontend/{app/todos,components,lib,tests}
mkdir -p core
```

**Acceptance**: All directories created, Phase 1 untouched

### 1.2 Initialize Frontend Project

```bash
cd phase2/frontend
npx create-next-app@14 . --typescript --tailwind --app --no-src-dir
npm install
```

**Acceptance**: Next.js project initialized, TypeScript configured

### 1.3 Set Up Environment Variables

Create `.env.example`:
```env
# Database
DATABASE_URL=postgresql://user:pass@ep-neon/db

# Backend
PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Frontend (Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Acceptance**: `.env.example` committed, no credentials in repo

## Phase 2: Backend Implementation (5 days)

### Step 2.1: Database Layer (from Spec 010)

1. Create `phase2/backend/db.py` with connection pooling
2. Create `phase2/backend/models.py` with Todo SQLModel
3. Initialize Alembic migrations
4. Create initial migration with indexes

**Acceptance**: Database connection works, migration applies

### Step 2.2: CRUD Operations

1. Create `phase2/backend/crud.py`:
   - `get_todos()` with filtering and search
   - `get_todo_by_id()`
   - `create_todo()`
   - `update_todo()`
   - `delete_todo()`
   - `update_todo_status()`

**Acceptance**: All CRUD operations tested, <100ms p95

### Step 2.3: FastAPI Application

1. Create `phase2/backend/main.py`:
   - Initialize FastAPI app
   - Configure CORS
   - Add startup event (connection check)
   - Add health check endpoint

2. Create `phase2/backend/api/deps.py`:
   - `get_session()` dependency

3. Create `phase2/backend/api/todos.py`:
   - `GET /api/todos` - List todos
   - `POST /api/todos` - Create todo
   - `GET /api/todos/{id}` - Get todo
   - `PUT /api/todos/{id}` - Update todo
   - `DELETE /api/todos/{id}` - Delete todo
   - `PATCH /api/todos/{id}/status` - Update status

**Acceptance**: All endpoints working, OpenAPI docs at `/docs`

### Step 2.4: Error Handling

1. Create `phase2/backend/exceptions.py`:
   - `TodoNotFoundError`
   - `ValidationError`
   - `DatabaseError`

2. Add exception handlers to FastAPI app

**Acceptance**: Errors return proper status codes and messages

### Step 2.5: Backend Tests

```bash
cd phase2/backend
pytest tests/ --cov=. --cov-report=html
```

**Acceptance**: 90%+ coverage, all tests passing

## Phase 3: Frontend Implementation (5 days)

### Step 3.1: API Client

Create `phase2/frontend/lib/api.ts`:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchTodos(filters: TodoFilters): Promise<Todo[]> { }
export async function createTodo(todo: TodoCreate): Promise<Todo> { }
export async function updateTodo(id: number, todo: TodoUpdate): Promise<Todo> { }
export async function deleteTodo(id: number): Promise<void> { }
export async function updateTodoStatus(id: number, status: string): Promise<Todo> { }
```

**Acceptance**: API client functions working with TypeScript types

### Step 3.2: TypeScript Types

Create `phase2/frontend/lib/types.ts`:
```typescript
export interface Todo {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface TodoFilters {
  status?: 'all' | 'pending' | 'completed';
  search?: string;
  limit?: number;
  offset?: number;
}
```

**Acceptance**: Types match backend Pydantic schemas

### Step 3.3: Components

Create components in `phase2/frontend/components/`:

1. `TodoList.tsx` - Container for todo list
2. `TodoItem.tsx` - Individual todo card
3. `TodoForm.tsx` - Create/edit form
4. `FilterBar.tsx` - Status filter and search
5. `LoadingSpinner.tsx` - Loading indicator
6. `ErrorBanner.tsx` - Error display
7. `EmptyState.tsx` - Empty list message

**Acceptance**: All components render correctly

### Step 3.4: Pages

Create pages in `phase2/frontend/app/`:

1. `page.tsx` - Home page with todo list and filters
2. `todos/new/page.tsx` - Create new todo
3. `todos/[id]/page.tsx` - Todo detail view
4. `todos/[id]/edit/page.tsx` - Edit todo
5. `layout.tsx` - Root layout with header

**Acceptance**: Navigation works, routes correct

### Step 3.5: State Management

Use React hooks for state:
- `useState()` for local component state
- `useEffect()` for data fetching
- No global state (keep it simple for Phase 2)

**Acceptance**: State updates correctly, no memory leaks

### Step 3.6: Responsive Design

1. Add Tailwind classes for responsive breakpoints
2. Test on mobile (375x667), tablet (768x1024), desktop (1920x1080)

**Acceptance**: Works on all screen sizes

### Step 3.7: Frontend Tests

```bash
cd phase2/frontend
npm test
```

**Acceptance**: Component tests passing

## Phase 4: Integration (3 days)

### Step 4.1: Backend-Frontend Connection

1. Start backend: `cd phase2/backend && uvicorn main:app --reload`
2. Start frontend: `cd phase2/frontend && npm run dev`
3. Test all API endpoints from frontend
4. Verify CORS configuration

**Acceptance**: Frontend successfully calls backend APIs

### Step 4.2: End-to-End Tests

Create E2E tests with Playwright:
```typescript
test('full todo workflow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('[data-testid="add-todo"]');
  await page.fill('[data-testid="todo-title"]', 'Test todo');
  await page.click('[data-testid="submit"]');
  await expect(page.locator('[data-testid="todo-item"]')).toHaveCount(1);
});
```

**Acceptance**: E2E tests pass for all user flows

### Step 4.3: Performance Testing

1. Create 10,000 test todos in database
2. Measure API response times
3. Measure page load times
4. Identify bottlenecks

**Acceptance**: API <100ms p95, page load <2s

### Step 4.4: Error Handling Verification

1. Test network errors (disconnect backend)
2. Test validation errors (invalid data)
3. Test 404 errors (non-existent todos)
4. Test 500 errors (simulate server error)

**Acceptance**: All errors displayed correctly with recovery options

## Phase 5: Core Domain Logic (1 day)

### Step 5.1: Create Shared Models

Create `core/models.py`:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Todo:
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

**Acceptance**: Shared models defined, no business logic

### Step 5.2: Validation Rules

Create `core/validation.py`:
```python
from core.models import Todo

def validate_todo(todo: Todo) -> list[str]:
    errors = []
    if not todo.title:
        errors.append("Title is required")
    if len(todo.title) > 200:
        errors.append("Title too long")
    if todo.status not in ['pending', 'completed']:
        errors.append("Invalid status")
    return errors
```

**Acceptance**: Validation rules tested, backend uses them

## Phase 6: Deployment Setup (2 days)

### Step 6.1: Backend Deployment

1. Create `phase2/backend/requirements.txt`
2. Create `Procfile` for Render/Railway
3. Configure environment variables on hosting platform
4. Test deployment

**Acceptance**: Backend deployed and accessible

### Step 6.2: Frontend Deployment

1. Build frontend: `npm run build`
2. Deploy to Vercel
3. Configure `NEXT_PUBLIC_API_URL` environment variable
4. Test deployed application

**Acceptance**: Frontend deployed and working

### Step 6.3: Database Setup

1. Create Neon PostgreSQL database
2. Set up connection string
3. Run migrations: `alembic upgrade head`
4. Verify database connectivity

**Acceptance**: Database initialized, migrations applied

## Integration Milestones

### Milestone 1: Backend API Complete (After Phase 2)
- Date: Day 6
- Verification: All endpoints tested, OpenAPI docs available
- Success: Backend API ready for frontend integration

### Milestone 2: Frontend UI Complete (After Phase 3)
- Date: Day 11
- Verification: All pages and components rendered
- Success: Frontend UI ready for backend integration

### Milestone 3: Full Integration (After Phase 4)
- Date: Day 14
- Verification: Frontend talks to backend, E2E tests pass
- Success: Full-stack application working

### Milestone 4: Deployment (After Phase 6)
- Date: Day 17
- Verification: Application deployed and accessible
- Success: Production-ready application

## Testing Strategy

### Backend Tests
- Unit tests: Models, CRUD operations, validation
- Integration tests: API endpoints, database operations
- Coverage target: 90%+

### Frontend Tests
- Component tests: All React components
- Integration tests: Page interactions
- E2E tests: Full user workflows with Playwright

### Integration Tests
- API contract tests
- End-to-end workflows
- Performance benchmarks

## Isolation Verification

### Phase 1 Untouched
- No modifications to `phase1/` directory
- Phase 1 imports not affected
- Phase 1 functionality preserved

### Phase 2 Isolated
- All Phase 2 code in `phase2/` directory
- No Phase 2 code in `phase1/` or `src/intelligence/`
- Clean separation of concerns

### Core Shared
- `core/` contains only domain models and validation
- No infrastructure code in core
- Phase 2 imports from core as needed

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| API contract mismatch | Medium | High | Use TypeScript types matching Pydantic, contract tests |
| CORS issues | Low | Medium | Configure CORS early, test across origins |
| Performance degradation | Low | Medium | Performance testing, indexing, connection pooling |
| Deployment failures | Medium | High | Test deployment early, have rollback plan |
| Phase 1 regression | Low | Critical | No Phase 1 code touched, verify after each phase |

## Success Criteria

1. Phase 1 code completely untouched (verified by git diff)
2. All backend API endpoints functional and tested
3. Frontend UI works on all screen sizes
4. Backend and frontend successfully integrate
5. E2E tests pass for all user workflows
6. API response time <100ms p95
7. Page load time <2s
8. 90%+ test coverage (backend)
9. Application deployed and accessible
10. Documentation complete

## Next Steps

1. Review and approve this plan
2. Generate detailed tasks via `/sp.tasks`
3. Execute implementation phases sequentially
4. Verify milestones after each phase
5. Deploy and test production application

---

**Plan Status**: Draft
**Review Required**: Yes
**Total Estimated Time**: 17 days
