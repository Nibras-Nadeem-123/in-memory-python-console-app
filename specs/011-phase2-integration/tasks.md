# Tasks: Phase 2 Full-Stack Integration

**Input**: Design documents from `/specs/011-phase2-integration/`
**Prerequisites**: plan.md (required), spec.md (required), backend spec (008), persistence spec (010)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase2/backend/`
- **Frontend**: `phase2/frontend/`
- **Shared**: `core/`
- **Phase 1**: `phase1/` (untouched)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Phase 2 directory structure: `phase2/backend/`, `phase2/frontend/`, `core/`
- [ ] T002 Create subdirectories: `phase2/backend/{api,migrations/versions,tests}`, `phase2/frontend/{app/todos,components,lib,tests}`
- [ ] T003 Create `.env.example` file at repository root with database, backend, and frontend environment variables
- [ ] T004 Create `core/__init__.py` to establish shared domain logic module
- [ ] T005 Verify Phase 1 isolation: confirm no files in `phase1/` are modified

**Checkpoint**: Project structure ready, Phase 1 isolated

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [ ] T006 Create `phase2/backend/requirements.txt` with: fastapi, uvicorn, sqlmodel, alembic, psycopg2-binary, pydantic-settings, pytest, pytest-asyncio
- [ ] T007 Create `phase2/backend/config.py` with DatabaseSettings class using pydantic-settings
- [ ] T008 Create `phase2/backend/db.py` with database engine, connection pooling (pool_size=5, max_overflow=10), and get_session() dependency
- [ ] T009 Create `phase2/backend/models.py` with Todo SQLModel class (id, title, description, status, created_at, updated_at)
- [ ] T010 Create `phase2/backend/exceptions.py` with TodoNotFoundError, ValidationError, DatabaseError
- [ ] T011 Initialize Alembic in `phase2/backend/migrations/` with `alembic init migrations`
- [ ] T012 Create `phase2/backend/migrations/env.py` configured to use SQLModel metadata
- [ ] T013 Generate initial migration: `alembic revision --autogenerate -m "initial schema"`
- [ ] T014 Customize migration `001_initial_schema.py` to add indexes: status, created_at DESC, (status, created_at DESC), GIN on title
- [ ] T015 Create `phase2/backend/crud.py` with get_todos(), get_todo_by_id(), create_todo(), update_todo(), delete_todo(), update_todo_status()

### Frontend Foundation

- [ ] T016 Initialize Next.js 14 project in `phase2/frontend/` with `npx create-next-app@14 . --typescript --tailwind --app --no-src-dir`
- [ ] T017 Install frontend dependencies in `phase2/frontend/`: npm install
- [ ] T018 Create `phase2/frontend/lib/types.ts` with Todo and TodoFilters TypeScript interfaces
- [ ] T019 Create `phase2/frontend/lib/api.ts` with fetchTodos(), createTodo(), updateTodo(), deleteTodo(), updateTodoStatus() functions

### API Infrastructure

- [ ] T020 Create `phase2/backend/api/deps.py` with get_session() FastAPI dependency
- [ ] T021 Create `phase2/backend/main.py` with FastAPI app initialization, CORS middleware, startup event (connection check), health check endpoint

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Repository Structure Setup (Priority: P1) 🎯 MVP

**Goal**: Developers set up Phase 2 full-stack repository with proper isolation from Phase 1 and designated areas for shared logic

**Independent Test**: Create directory structure and verify via git status that Phase 1 is untouched

### Implementation for US1

- [ ] T022 [P] [US1] Create `core/models.py` with shared Todo dataclass (id, title, description, status, created_at, updated_at)
- [ ] T023 [P] [US1] Create `core/validation.py` with validate_todo() function checking title required, title length, status enum
- [ ] T024 [US1] Verify Phase 1 isolation: run `git diff phase1/` to confirm no changes
- [ ] T025 [US1] Verify Phase 2 isolation: confirm no Phase 2 code in `phase1/` or `src/intelligence/`
- [ ] T026 [US1] Verify core is domain-only: confirm `core/` contains only models and validation, no infrastructure code

**Checkpoint**: Repository structure complete, isolation verified

---

## Phase 4: User Story 2 - Backend-Frontend Integration (Priority: P1) 🎯

**Goal**: Backend API and frontend UI communicate successfully through REST API endpoints with proper data contracts

**Independent Test**: Start backend and frontend, perform CRUD operations through UI, verify database updates

### Backend Implementation for US2

- [ ] T027 [P] [US2] Implement `phase2/backend/api/todos.py` GET /api/todos endpoint with status, search, limit, offset query params
- [ ] T028 [P] [US2] Implement `phase2/backend/api/todos.py` POST /api/todos endpoint with TodoCreate schema validation
- [ ] T029 [P] [US2] Implement `phase2/backend/api/todos.py` GET /api/todos/{id} endpoint returning TodoResponse
- [ ] T030 [P] [US2] Implement `phase2/backend/api/todos.py` PUT /api/todos/{id} endpoint with TodoUpdate schema
- [ ] T031 [P] [US2] Implement `phase2/backend/api/todos.py` DELETE /api/todos/{id} endpoint
- [ ] T032 [P] [US2] Implement `phase2/backend/api/todos.py` PATCH /api/todos/{id}/status endpoint with TodoStatusUpdate schema
- [ ] T033 [US2] Add exception handlers to `phase2/backend/main.py` for TodoNotFoundError (404), ValidationError (400), DatabaseError (500)
- [ ] T034 [US2] Configure CORS in `phase2/backend/main.py` to allow frontend origin only (http://localhost:3000)
- [ ] T035 [US2] Add request logging middleware to `phase2/backend/main.py` to log all requests with response status and duration

### Frontend Implementation for US2

- [ ] T036 [P] [US2] Create `phase2/frontend/components/TodoList.tsx` container component with state management
- [ ] T037 [P] [US2] Create `phase2/frontend/components/TodoItem.tsx` individual todo card with title, status, action buttons
- [ ] T038 [P] [US2] Create `phase2/frontend/components/TodoForm.tsx` form with title and description inputs
- [ ] T039 [P] [US2] Create `phase2/frontend/components/FilterBar.tsx` with status tabs and search input
- [ ] T040 [P] [US2] Create `phase2/frontend/components/LoadingSpinner.tsx` visual loading indicator
- [ ] T041 [P] [US2] Create `phase2/frontend/components/ErrorBanner.tsx` error display with dismiss and retry options
- [ ] T042 [P] [US2] Create `phase2/frontend/components/EmptyState.tsx` message when no todos match filters
- [ ] T043 [US2] Create `phase2/frontend/app/page.tsx` home page with TodoList and FilterBar
- [ ] T044 [US2] Create `phase2/frontend/app/todos/new/page.tsx` create new todo page with TodoForm
- [ ] T045 [US2] Create `phase2/frontend/app/todos/[id]/page.tsx` todo detail view
- [ ] T046 [US2] Create `phase2/frontend/app/todos/[id]/edit/page.tsx` edit todo page with TodoForm
- [ ] T047 [US2] Create `phase2/frontend/app/layout.tsx` root layout with header and main content
- [ ] T048 [US2] Add responsive Tailwind classes to all components for mobile (375x667), tablet (768x1024), desktop (1920x1080)
- [ ] T049 [US2] Implement loading states in all components using LoadingSpinner during API calls
- [ ] T050 [US2] Implement error states in all components using ErrorBanner with retry functionality

**Checkpoint**: Backend API complete, frontend UI complete, integration ready

---

## Phase 5: User Story 3 - End-to-End Testing (Priority: P2)

**Goal**: Full user workflows are tested end-to-end from UI to database to ensure system works as expected

**Independent Test**: Run E2E tests with Playwright, verify all user journeys complete successfully

### Backend Tests for US3

- [ ] T051 [P] [US3] Create `phase2/backend/tests/test_models.py` unit tests for Todo model validation
- [ ] T052 [P] [US3] Create `phase2/backend/tests/test_crud.py` unit tests for all CRUD operations
- [ ] T053 [P] [US3] Create `phase2/backend/tests/test_db.py` unit tests for database connection and pooling
- [ ] T054 [P] [US3] Create `phase2/backend/tests/test_migrations.py` integration tests for migration upgrade and rollback
- [ ] T055 [US3] Create `phase2/backend/tests/test_api/` directory for API endpoint tests
- [ ] T056 [P] [US3] Create `phase2/backend/tests/test_api/test_todos.py` integration tests for all todo API endpoints
- [ ] T057 [US3] Configure pytest in `phase2/backend/pytest.ini` with test database and coverage settings

### Frontend Tests for US3

- [ ] T058 [P] [US3] Create `phase2/frontend/tests/` directory structure
- [ ] T059 [P] [US3] Create component tests for TodoList.tsx
- [ ] T060 [P] [US3] Create component tests for TodoItem.tsx
- [ ] T061 [P] [US3] Create component tests for TodoForm.tsx
- [ ] T062 [P] [US3] Create component tests for FilterBar.tsx
- [ ] T063 [P] [US3] Create component tests for ErrorBanner.tsx
- [ ] T064 [US3] Create page interaction tests for all pages

### E2E Tests for US3

- [ ] T065 [P] [US3] Install Playwright in `phase2/frontend/` with `npm install -D @playwright/test`
- [ ] T066 [P] [US3] Create `phase2/frontend/e2e/` directory for E2E tests
- [ ] T067 [P] [US3] Create E2E test for full CRUD workflow (create, read, update, delete)
- [ ] T068 [P] [US3] Create E2E test for concurrent updates scenario
- [ ] T069 [P] [US3] Create E2E test for network error handling
- [ ] T070 [P] [US3] Create E2E test for validation error handling
- [ ] T071 [P] [US3] Create E2E test for 404 error handling
- [ ] T072 [US3] Configure Playwright in `phase2/frontend/playwright.config.ts`

**Checkpoint**: All tests implemented, coverage metrics available

---

## Phase 6: User Story 4 - Deployment Verification (Priority: P2)

**Goal**: Deployed application works correctly in production environment with proper configuration and data persistence

**Independent Test**: Deploy to staging/production, perform smoke tests, verify all functionality works

### Backend Deployment for US4

- [ ] T073 [US4] Create `phase2/backend/Procfile` for Render/Railway deployment
- [ ] T074 [US4] Add deployment documentation to `phase2/backend/README.md`
- [ ] T075 [US4] Configure backend environment variables on hosting platform (DATABASE_URL, PORT, LOG_LEVEL, CORS_ORIGINS)
- [ ] T076 [US4] Test backend deployment: start server, verify health check endpoint, test API endpoints

### Frontend Deployment for US4

- [ ] T077 [US4] Build frontend: `npm run build` in `phase2/frontend/`
- [ ] T078 [US4] Configure `NEXT_PUBLIC_API_URL` environment variable on Vercel
- [ ] T079 [US4] Test frontend deployment: load application, verify connectivity to backend API
- [ ] T080 [US4] Test responsive design on deployed application (mobile, tablet, desktop)

### Database Setup for US4

- [ ] T081 [US4] Create Neon PostgreSQL database
- [ ] T082 [US4] Configure database connection string in production environment
- [ ] T083 [US4] Run migrations on production database: `alembic upgrade head`
- [ ] T084 [US4] Verify database connectivity: test CRUD operations, verify indexes exist

### Smoke Tests for US4

- [ ] T085 [P] [US4] Run smoke test: create todo via deployed UI, verify persistence across sessions
- [ ] T086 [P] [US4] Run smoke test: load application with 100 concurrent users, verify no errors
- [ ] T087 [P] [US4] Run smoke test: test migration procedure (upgrade and rollback)
- [ ] T088 [P] [US4] Run smoke test: verify logging and error tracking

**Checkpoint**: Application deployed, all smoke tests passing

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T089 [P] Add docstrings to all backend functions in `phase2/backend/`
- [ ] T090 [P] Add JSDoc comments to all frontend TypeScript functions in `phase2/frontend/`
- [ ] T091 [P] Create `phase2/backend/README.md` with setup instructions, API documentation link
- [ ] T092 [P] Create `phase2/frontend/README.md` with setup instructions, development workflow
- [ ] T093 [P] Create repository-level `PHASE2.md` documentation linking to backend and frontend READMEs
- [ ] T094 [P] Run backend test coverage: `pytest phase2/backend/tests/ --cov=phase2/backend --cov-report=html`, verify ≥90%
- [ ] T095 [P] Run frontend test coverage: `npm test` in `phase2/frontend/`
- [ ] T096 [P] Run E2E tests: `npx playwright test` in `phase2/frontend/`
- [ ] T097 Run performance test: measure API response times, verify <100ms p95
- [ ] T098 Run performance test: measure page load times, verify <2s on 4G network
- [ ] T099 [P] Run `git diff phase1/` to verify Phase 1 remains completely untouched
- [ ] T100 Verify Phase 2 isolation: confirm no Phase 2 code in `phase1/` or `src/intelligence/`

**Checkpoint**: All documentation complete, tests passing, Phase 1 isolation verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - independent of other stories
- **User Story 2 (Phase 4)**: Depends on Foundational and US1 - backend-frontend integration
- **User Story 3 (Phase 5)**: Depends on US2 - tests require working backend and frontend
- **User Story 4 (Phase 6)**: Depends on US3 - deployment requires tests passing
- **Polish (Phase 7)**: Depends on all user stories being complete

### Within Each Phase

**Phase 2 (Foundational)**:
- Backend foundation tasks (T006-T021) must complete before frontend can integrate
- Frontend foundation tasks (T016-T019) can start in parallel with backend foundation

**Phase 4 (User Story 2 - Integration)**:
- Backend implementation tasks (T027-T035) can run in parallel
- Frontend implementation tasks (T036-T050) can run in parallel
- Both must complete before integration testing

**Phase 5 (User Story 3 - Testing)**:
- Backend tests (T051-T057) can run in parallel
- Frontend tests (T058-T064) can run in parallel
- E2E tests (T065-T072) depend on backend and frontend tests passing

**Phase 6 (User Story 4 - Deployment)**:
- Backend deployment (T073-T076) can run in parallel with frontend deployment (T077-T080)
- Database setup (T081-T084) must complete before smoke tests
- Smoke tests (T085-T088) can run in parallel

### Parallel Opportunities

**Maximum Parallelization** (with sufficient team capacity):

1. **Phase 2 Foundational**: Backend team (T006-T015) + Frontend team (T016-T019)
2. **Phase 4 Integration**: Backend team (T027-T035) + Frontend team (T036-T050)
3. **Phase 5 Testing**: Backend test team (T051-T057) + Frontend test team (T058-T064) + E2E team (T065-T072)
4. **Phase 6 Deployment**: Backend deploy team (T073-T076) + Frontend deploy team (T077-T080) + DB team (T081-T084)
5. **Phase 7 Polish**: Documentation team (T089-T093) + Test team (T094-T096) + Performance team (T097-T098)

---

## Parallel Examples

### Backend Team (Parallel Execution)

```bash
# Launch all backend API endpoints together:
Task: "Implement GET /api/todos endpoint in phase2/backend/api/todos.py"
Task: "Implement POST /api/todos endpoint in phase2/backend/api/todos.py"
Task: "Implement GET /api/todos/{id} endpoint in phase2/backend/api/todos.py"
Task: "Implement PUT /api/todos/{id} endpoint in phase2/backend/api/todos.py"
Task: "Implement DELETE /api/todos/{id} endpoint in phase2/backend/api/todos.py"
Task: "Implement PATCH /api/todos/{id}/status endpoint in phase2/backend/api/todos.py"
```

### Frontend Team (Parallel Execution)

```bash
# Launch all component creations together:
Task: "Create TodoList.tsx in phase2/frontend/components/"
Task: "Create TodoItem.tsx in phase2/frontend/components/"
Task: "Create TodoForm.tsx in phase2/frontend/components/"
Task: "Create FilterBar.tsx in phase2/frontend/components/"
Task: "Create LoadingSpinner.tsx in phase2/frontend/components/"
Task: "Create ErrorBanner.tsx in phase2/frontend/components/"
Task: "Create EmptyState.tsx in phase2/frontend/components/"
```

### Test Team (Parallel Execution)

```bash
# Launch all test creations together:
Task: "Create test_models.py in phase2/backend/tests/"
Task: "Create test_crud.py in phase2/backend/tests/"
Task: "Create test_db.py in phase2/backend/tests/"
Task: "Create test_migrations.py in phase2/backend/tests/"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Repository Structure)
4. Complete Phase 4: User Story 2 (Backend-Frontend Integration)
5. **STOP and VALIDATE**: Test backend API with curl/Postman, test frontend UI with mock data
6. Integrate backend and frontend, test full CRUD workflow
7. **Deploy MVP**: Backend + Frontend working together
8. Demo MVP to stakeholders

### Incremental Delivery

1. **Milestone 1 (Setup + Foundational)**: Infrastructure ready, backend database operational
2. **Milestone 2 (US1 + US2)**: Full-stack CRUD application working, deployable
3. **Milestone 3 (US3)**: All tests passing, 90%+ coverage, confidence in code quality
4. **Milestone 4 (US4)**: Production deployment complete, monitoring in place
5. **Milestone 5 (Polish)**: Documentation complete, performance validated

### Parallel Team Strategy

With 3 developers:

1. **Team completes Setup (Phase 1) together** - 0.5 days
2. **Once Setup complete**:
   - **Developer A (Backend)**: Phase 2 backend foundation (T006-T015)
   - **Developer B (Frontend)**: Phase 2 frontend foundation (T016-T019)
   - **Developer C (Core)**: US1 shared models (T022-T023)
3. **Once Foundational complete**:
   - **Developer A**: US2 backend API (T027-T035) + US3 backend tests (T051-T057)
   - **Developer B**: US2 frontend components (T036-T050) + US3 frontend tests (T058-T064)
   - **Developer C**: US3 E2E tests (T065-T072) + US4 deployment (T073-T088)

---

## Task Groupings by Component

### Backend Tasks (T006-T015, T021, T027-T035, T051-T057)
- Total: 35 tasks
- Focus: FastAPI, SQLModel, PostgreSQL, Alembic, validation, error handling

### Frontend Tasks (T016-T019, T036-T050, T058-T064, T065-T072)
- Total: 45 tasks
- Focus: Next.js, React, TypeScript, Tailwind, Playwright

### Core/Shared Tasks (T022-T026)
- Total: 5 tasks
- Focus: Domain models, validation rules, isolation verification

### Deployment Tasks (T073-T088)
- Total: 16 tasks
- Focus: Vercel, Render/Railway, Neon, configuration, smoke tests

### Polish Tasks (T089-T100)
- Total: 12 tasks
- Focus: Documentation, testing, performance, verification

---

## Notes

- [P] tasks = different files, no dependencies
- [US1-4] labels map task to specific user story for traceability
- Each user story is independently completable and testable
- Phase 1 code remains completely untouched (T005, T099, T100 verify this)
- All database credentials in environment variables only (T003, T075, T078, T082)
- Test coverage target: 90%+ for backend (T094)
- Performance targets: API <100ms p95 (T097), page load <2s (T098)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, Phase 1 modifications

---

## Summary

- **Total Tasks**: 100
- **Tasks by User Story**:
  - US1 (Repository Setup): 5 tasks (T022-T026)
  - US2 (Backend-Frontend Integration): 24 tasks (T027-T050)
  - US3 (E2E Testing): 22 tasks (T051-T072)
  - US4 (Deployment): 16 tasks (T073-T088)
- **Infrastructure Tasks**: 21 tasks (T001-T021)
- **Polish Tasks**: 12 tasks (T089-T100)

- **Parallel Opportunities**: 57 tasks marked [P]
- **Critical Dependencies**: Phase 2 (Foundational) blocks all user stories

- **MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 50 tasks
- **Full Scope**: All 7 phases = 100 tasks
