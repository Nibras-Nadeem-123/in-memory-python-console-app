# Tasks: SDD System Phase 1 - Frontend-Backend Architecture

**Feature**: Frontend-Backend Spec Generation System
**Branch**: `phase1-frontend-backend`
**Prerequisites**: plan.md, data-model.md, contracts/openapi.yaml

**Organization**: Tasks are grouped by implementation phase to enable independent testing at each milestone.

## Format: `- [ ] [TaskID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 = MVP)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/src/`
- **Tests**: `backend/tests/`, `frontend/tests/`
- **Documentation**: `specs/sdd-phase1-frontend-backend/`

---

## Phase 1: Project Setup & Infrastructure

**Purpose**: Initialize project structure and development environment

### Backend Initialization

- [ ] T001 [P] Create backend directory structure per plan.md at backend/
- [ ] T002 [P] Initialize Python virtual environment in backend/venv
- [ ] T003 [P] Create backend/requirements.txt with FastAPI 0.104+, Pydantic 2.5+, uvicorn, pytest 7.4+
- [ ] T004 [P] Create backend/pyproject.toml with project metadata and tool configurations
- [ ] T005 [P] Create backend/.gitignore for Python (venv/, __pycache__/, *.pyc, .env)
- [ ] T006 [P] Create backend/README.md with setup instructions per quickstart.md

### Frontend Initialization

- [ ] T007 [P] Initialize Vite + React + TypeScript project in frontend/ using create-vite
- [ ] T008 [P] Update frontend/package.json with TanStack Query, React Testing Library, Vitest
- [ ] T009 [P] Configure frontend/vite.config.ts with proxy to backend http://localhost:8000
- [ ] T010 [P] Configure frontend/tsconfig.json with strict type checking
- [ ] T011 [P] Create frontend/.gitignore for Node.js (node_modules/, dist/, .env.local)
- [ ] T012 [P] Create frontend/README.md with setup instructions per quickstart.md

### Root Project Files

- [ ] T013 Create root .gitignore combining backend and frontend ignore patterns
- [ ] T014 Create root README.md describing Phase 1 goals and quickstart
- [ ] T015 [P] Create .env.example files for backend/ and frontend/ with config templates

**Checkpoint**: Project structure ready - can install dependencies and run dev servers

---

## Phase 2: Backend Foundation (Blocking Prerequisites)

**Purpose**: Core infrastructure that all features depend on

### Data Models

- [ ] T016 Create backend/app/__init__.py (empty marker file)
- [ ] T017 Create backend/app/models/__init__.py and export all models
- [ ] T018 [P] Implement UserIntent model in backend/app/models/intent.py per data-model.md
- [ ] T019 [P] Implement Entity model with EntityType enum in backend/app/models/spec.py
- [ ] T020 [P] Implement Relationship model with RelationshipType enum in backend/app/models/spec.py
- [ ] T021 [P] Implement Constraint model with ConstraintType and Priority enums in backend/app/models/spec.py
- [ ] T022 [P] Implement Assumption model with ConfidenceLevel enum in backend/app/models/spec.py
- [ ] T023 [P] Implement SpecMetadata model with confidence calculation in backend/app/models/spec.py
- [ ] T024 Implement StructuredSpec model with validation in backend/app/models/spec.py

### Core Infrastructure

- [ ] T025 Create backend/app/core/__init__.py (empty marker file)
- [ ] T026 Implement RequestContext model in backend/app/core/context.py for request-scoped state
- [ ] T027 Implement Engine orchestrator in backend/app/core/engine.py with execute() method
- [ ] T028 Implement SpecBuilder skeleton in backend/app/core/spec_builder.py with build() method signature

**Checkpoint**: Data models defined - can validate JSON payloads

---

## Phase 3: Backend Skills (Core Logic)

**Purpose**: Discrete spec generation logic

### Skill Infrastructure

- [ ] T029 Create backend/app/skills/__init__.py and export all skills
- [ ] T030 Create base Skill interface in backend/app/skills/base.py with execute() method

### Individual Skills

- [ ] T031 [P] Implement GoalIdentifierSkill in backend/app/skills/goal_identifier.py
- [ ] T032 [P] Implement EntityExtractorSkill in backend/app/skills/entity_extractor.py
- [ ] T033 [P] Implement ConstraintParserSkill in backend/app/skills/constraint_parser.py
- [ ] T034 [P] Implement AssumptionDetectorSkill in backend/app/skills/assumption_detector.py

### Spec Builder Integration

- [ ] T035 Implement SpecBuilder.build() in backend/app/core/spec_builder.py orchestrating all skills
- [ ] T036 Add confidence score calculation to SpecBuilder using formula from data-model.md
- [ ] T037 Add metadata generation (timestamp, processing_time, warnings) to SpecBuilder

**Checkpoint**: Core spec generation logic complete - can transform intent to spec

---

## Phase 4: Backend API Layer

**Purpose**: Expose spec generation via REST API

### API Setup

- [ ] T038 Create backend/app/api/__init__.py (empty marker file)
- [ ] T039 Implement POST /api/v1/spec endpoint in backend/app/api/spec.py per openapi.yaml
- [ ] T040 Add request validation (word count, encoding) to /spec endpoint
- [ ] T041 Add error handling for 400 (validation), 422 (ambiguous), 500 (server) errors
- [ ] T042 Implement GET /api/v1/health endpoint returning status and version

### FastAPI Application

- [ ] T043 Create FastAPI app instance in backend/app/main.py
- [ ] T044 Configure CORS middleware in main.py allowing http://localhost:5173
- [ ] T045 Register /spec and /health routers in main.py
- [ ] T046 Add startup/shutdown event handlers for logging in main.py
- [ ] T047 Add request logging middleware in main.py

**Checkpoint**: Backend API complete - can curl endpoints and receive responses

---

## Phase 5: Frontend Foundation

**Purpose**: Base UI structure and routing

### App Structure

- [ ] T048 Create frontend/src/App.tsx as main component with layout
- [ ] T049 Create frontend/src/main.tsx as entry point with React.StrictMode
- [ ] T050 Create frontend/src/index.css with base styles and CSS reset
- [ ] T051 Create frontend/src/types/spec.ts with TypeScript interfaces matching backend models

### API Client

- [ ] T052 Create frontend/src/api/client.ts with fetch wrapper and base URL from env
- [ ] T053 Implement generateSpec() function in client.ts calling POST /api/v1/spec
- [ ] T054 Add error handling and timeout (5s) to API client
- [ ] T055 Create frontend/src/hooks/useSpecGeneration.ts using TanStack Query

**Checkpoint**: Frontend can call backend API

---

## Phase 6: Frontend UI Components (User Story 1 - MVP)

**Purpose**: Complete intent-to-spec workflow UI

**User Story**: As a user, I can submit an idea and receive a structured specification

**Independent Test**: Submit 100-word intent via UI, verify structured spec displays with goal, entities, constraints within 3 seconds

### Input Component

- [ ] T056 [US1] Create IntentInput component in frontend/src/components/IntentInput.tsx
- [ ] T057 [US1] Add word count validation (50-500 words) to IntentInput with live feedback
- [ ] T058 [US1] Add submit button with loading state to IntentInput
- [ ] T059 [US1] Add client-side validation error display to IntentInput

### Output Components

- [ ] T060 [US1] Create SpecOutput container in frontend/src/components/SpecOutput.tsx
- [ ] T061 [US1] Create GoalSection component in frontend/src/components/GoalSection.tsx
- [ ] T062 [US1] Create EntitiesSection component in frontend/src/components/EntitiesSection.tsx
- [ ] T063 [US1] Create ConstraintsSection component in frontend/src/components/ConstraintsSection.tsx
- [ ] T064 [US1] Create AssumptionsSection component in frontend/src/components/AssumptionsSection.tsx
- [ ] T065 [US1] Create MetadataSection component in frontend/src/components/MetadataSection.tsx

### Error Handling

- [ ] T066 [US1] Create ErrorDisplay component in frontend/src/components/ErrorDisplay.tsx
- [ ] T067 [US1] Add error handling for 400, 422, 500 responses to ErrorDisplay
- [ ] T068 [US1] Add retry button to ErrorDisplay for failed requests

### Integration

- [ ] T069 [US1] Wire IntentInput to useSpecGeneration hook in App.tsx
- [ ] T070 [US1] Wire SpecOutput to display generated spec in App.tsx
- [ ] T071 [US1] Wire ErrorDisplay to show API errors in App.tsx
- [ ] T072 [US1] Add loading spinner during spec generation in App.tsx

**Checkpoint**: MVP complete - full intent-to-spec workflow functional

---

## Phase 7: Testing & Quality

**Purpose**: Ensure code quality and correctness

### Backend Tests

- [ ] T073 [P] Create backend/tests/__init__.py (empty marker file)
- [ ] T074 [P] Create backend/tests/unit/__init__.py (empty marker file)
- [ ] T075 [P] Create backend/tests/integration/__init__.py (empty marker file)
- [ ] T076 [P] Test UserIntent model validation in backend/tests/unit/test_intent_model.py
- [ ] T077 [P] Test StructuredSpec model validation in backend/tests/unit/test_spec_model.py
- [ ] T078 [P] Test GoalIdentifierSkill in backend/tests/unit/test_goal_identifier.py
- [ ] T079 [P] Test EntityExtractorSkill in backend/tests/unit/test_entity_extractor.py
- [ ] T080 [P] Test ConstraintParserSkill in backend/tests/unit/test_constraint_parser.py
- [ ] T081 [P] Test AssumptionDetectorSkill in backend/tests/unit/test_assumption_detector.py
- [ ] T082 [P] Test SpecBuilder.build() with sample inputs in backend/tests/unit/test_spec_builder.py
- [ ] T083 [P] Test POST /spec endpoint with valid input in backend/tests/integration/test_api_spec.py
- [ ] T084 [P] Test POST /spec endpoint with invalid input (400) in backend/tests/integration/test_api_spec.py
- [ ] T085 [P] Test POST /spec endpoint with ambiguous input (422) in backend/tests/integration/test_api_spec.py
- [ ] T086 [P] Test GET /health endpoint in backend/tests/integration/test_api_health.py

### Frontend Tests

- [ ] T087 [P] Create frontend/tests/setup.ts with testing library configuration
- [ ] T088 [P] Test IntentInput component render in frontend/tests/components/IntentInput.test.tsx
- [ ] T089 [P] Test IntentInput word count validation in frontend/tests/components/IntentInput.test.tsx
- [ ] T090 [P] Test SpecOutput displays all sections in frontend/tests/components/SpecOutput.test.tsx
- [ ] T091 [P] Test ErrorDisplay shows error messages in frontend/tests/components/ErrorDisplay.test.tsx
- [ ] T092 [P] Test useSpecGeneration hook in frontend/tests/hooks/useSpecGeneration.test.ts
- [ ] T093 Integration test: submit intent and verify spec display in frontend/tests/integration/workflow.test.tsx

### Code Quality

- [ ] T094 [P] Run ruff lint on backend/app/ and fix issues
- [ ] T095 [P] Run mypy on backend/app/ and fix type errors
- [ ] T096 [P] Run eslint on frontend/src/ and fix issues
- [ ] T097 [P] Run tsc --noEmit on frontend/ and fix type errors
- [ ] T098 [P] Verify test coverage >80% on backend/app/core/ and backend/app/skills/
- [ ] T099 [P] Verify test coverage >70% on frontend/src/components/

**Checkpoint**: Tests passing - code meets quality standards

---

## Phase 8: Documentation & Polish

**Purpose**: Production-ready deliverables

### Configuration Files

- [ ] T100 [P] Create backend/.env.example with HOST, PORT, CORS_ORIGINS, LOG_LEVEL
- [ ] T101 [P] Create frontend/.env.example with VITE_API_URL, VITE_API_TIMEOUT
- [ ] T102 [P] Create docker-compose.yml for local development (optional)

### Documentation

- [ ] T103 [P] Update backend/README.md with API documentation and examples
- [ ] T104 [P] Update frontend/README.md with component documentation
- [ ] T105 Update root README.md with complete setup and usage instructions
- [ ] T106 [P] Add JSDoc comments to all frontend components
- [ ] T107 [P] Add docstrings to all backend skills and models

### Deployment Prep

- [ ] T108 [P] Create backend/Dockerfile for containerization (optional)
- [ ] T109 [P] Create frontend build script in package.json (npm run build)
- [ ] T110 [P] Test production build: backend runs with uvicorn, frontend builds to dist/

**Checkpoint**: Phase 1 complete and documented

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Backend Foundation) ← BLOCKS all backend work
    ↓
Phase 3 (Backend Skills) ← depends on Phase 2
    ↓
Phase 4 (Backend API) ← depends on Phase 3
    ↓
Phase 5 (Frontend Foundation) ← depends on Phase 4 (needs API to exist)
    ↓
Phase 6 (Frontend UI - MVP) ← depends on Phase 5
    ↓
Phase 7 (Testing & Quality) ← depends on Phases 2-6
    ↓
Phase 8 (Documentation & Polish) ← depends on Phase 7
```

### Task Dependencies Within Phases

**Phase 2 (Backend Foundation)**:
- T016-T017 must complete before T018-T024 (need __init__.py)
- T018-T023 can run in parallel (different models)
- T024 depends on T018-T023 (references all models)
- T025-T026 independent
- T027 depends on T026 (uses RequestContext)
- T028 depends on T024 (returns StructuredSpec)

**Phase 3 (Backend Skills)**:
- T029-T030 must complete first (base infrastructure)
- T031-T034 can run in parallel (independent skills)
- T035 depends on T031-T034 (uses all skills)
- T036-T037 depend on T035 (extend SpecBuilder)

**Phase 4 (Backend API)**:
- T038 first, then T039-T042 can run in parallel
- T043 depends on T039-T042 (registers routers)
- T044-T047 depend on T043 (configure app)

**Phase 5 (Frontend Foundation)**:
- T048-T051 can run in parallel
- T052-T054 must run sequentially (build API client)
- T055 depends on T052-T054 (uses API client)

**Phase 6 (Frontend UI)**:
- T056-T059 (IntentInput) sequential
- T060-T065 (Output components) can run in parallel after T060
- T066-T068 (ErrorDisplay) sequential
- T069-T072 (Integration) must be last, depend on all UI components

**Phase 7 (Testing)**:
- All unit tests (T076-T082, T088-T091) can run in parallel
- Integration tests (T083-T086, T093) depend on implementation
- Code quality (T094-T099) can run in parallel after implementation

**Phase 8 (Documentation)**:
- All tasks can run in parallel

---

## Parallel Execution Opportunities

### Maximum Parallelism by Phase

**Phase 1 (Setup)**: 15 tasks total
- Parallel group 1: T001, T002, T007, T013
- Parallel group 2: T003, T004, T005, T006, T008, T009, T010, T011, T012
- Sequential: T014, T015

**Phase 2 (Backend Foundation)**: 13 tasks total
- Sequential: T016, T017
- Parallel group: T018, T019, T020, T021, T022, T023 (6 models)
- Sequential: T024, T025, T026, T027, T028

**Phase 3 (Backend Skills)**: 9 tasks total
- Sequential: T029, T030
- Parallel group: T031, T032, T033, T034 (4 skills)
- Sequential: T035, T036, T037

**Phase 4 (Backend API)**: 10 tasks total
- Sequential: T038
- Parallel group: T039, T040, T041, T042 (4 endpoints)
- Sequential: T043, T044, T045, T046, T047

**Phase 5 (Frontend Foundation)**: 8 tasks total
- Parallel group: T048, T049, T050, T051
- Sequential: T052, T053, T054, T055

**Phase 6 (Frontend UI)**: 17 tasks total
- Sequential: T056, T057, T058, T059, T060
- Parallel group: T061, T062, T063, T064, T065 (5 components)
- Sequential: T066, T067, T068, T069, T070, T071, T072

**Phase 7 (Testing)**: 27 tasks total
- Parallel group: T076-T086 (11 backend tests), T088-T092 (5 frontend tests), T094-T099 (6 quality)
- Sequential: T073, T074, T075, T087, T093

**Phase 8 (Documentation)**: 11 tasks total
- Parallel group: T100-T110 (all can run in parallel)

---

## Implementation Strategy

### MVP First Approach (Recommended)

1. **Week 1: Backend MVP**
   - Complete Phase 1 (Setup)
   - Complete Phase 2 (Backend Foundation)
   - Complete Phase 3 (Backend Skills) - implement basic versions
   - Complete Phase 4 (Backend API) - /spec endpoint only

2. **Week 2: Frontend MVP**
   - Complete Phase 5 (Frontend Foundation)
   - Complete Phase 6 (Frontend UI) - basic styling
   - **STOP and VALIDATE**: Test intent-to-spec flow end-to-end

3. **Week 3: Quality & Polish**
   - Complete Phase 7 (Testing) - aim for >80% coverage
   - Complete Phase 8 (Documentation)
   - Deploy demo

### Incremental Delivery Checkpoints

After each checkpoint, the system should be demonstrable:

1. **After Phase 2**: Can validate JSON payloads with Pydantic
2. **After Phase 3**: Can transform intent to spec via Python script
3. **After Phase 4**: Can curl backend API and receive structured spec
4. **After Phase 5**: Frontend can call backend (even with hardcoded UI)
5. **After Phase 6**: Full workflow functional (MVP complete)
6. **After Phase 7**: Production-ready with tests
7. **After Phase 8**: Documented and deployable

### Testing Strategy

**Test-Driven Development (Optional)**:
- For each skill (T031-T034), write test first (T078-T081)
- For each API endpoint (T039-T042), write test first (T083-T086)
- For each component (T056-T065), write test first (T088-T091)

**Integration Testing**:
- T093 validates complete workflow
- Manual testing per quickstart.md at each checkpoint

---

## Summary

| Phase | Tasks | Tests | Parallel Tasks | Est. Days |
|-------|-------|-------|----------------|-----------|
| 1: Setup | 15 | 0 | 13 | 1 |
| 2: Backend Foundation | 13 | 0 | 6 | 2 |
| 3: Backend Skills | 9 | 0 | 4 | 2 |
| 4: Backend API | 10 | 0 | 4 | 2 |
| 5: Frontend Foundation | 8 | 0 | 4 | 1 |
| 6: Frontend UI (MVP) | 17 | 0 | 5 | 3 |
| 7: Testing & Quality | 27 | 16 | 22 | 3 |
| 8: Documentation & Polish | 11 | 0 | 11 | 1 |
| **Total** | **110** | **16** | **69** | **15** |

---

## Notes

- All tasks follow strict checkbox format: `- [ ] [TaskID] [P?] [Story?] Description with path`
- [P] = parallelizable (different files, no blocking dependencies)
- [US1] = User Story 1 (MVP scope)
- Phase 1-5 are prerequisites; Phase 6 is the MVP user story
- Tests are included but optional (can skip for rapid prototyping)
- Each phase has clear completion criteria
- Parallel opportunities identified for efficient development
- MVP scope: Phases 1-6 (can demo intent-to-spec workflow)
- Production-ready: All phases (includes tests and docs)

---

## Independent Test Criteria (MVP - Phase 6)

**User Story 1: Intent to Spec Workflow**

**Given**: Backend running on localhost:8000, Frontend running on localhost:5173

**When**: User enters 100-word intent describing a "todo app with priorities and tags"

**Then**:
- Frontend validates word count client-side
- Frontend sends POST request to /api/v1/spec
- Backend returns 200 with StructuredSpec JSON
- Frontend displays:
  - Goal section with primary objective
  - Entities section showing Task and Tag entities
  - Constraints section with priority filtering requirement
  - Assumptions section with clarification flags
  - Metadata section with confidence score >0.7
- Total time from submit to display: <3 seconds
- No console errors in browser DevTools
- No 500 errors in backend logs

**Test Method**: Manual testing per quickstart.md examples
