# Implementation Plan: SDD System Phase 1 - Frontend-Backend Architecture

**Branch**: `phase1-frontend-backend` | **Date**: 2025-12-31 | **Spec**: User Requirements
**Input**: Create minimal but complete system transforming user intent into structured specification

## Summary

Build a minimal Spec-Driven Development (SDD) system with clean frontend-backend separation that transforms natural language user intent into structured specifications. Phase 1 focuses on intent capture, interpretation, and structured output without execution, task automation, or persistence.

**Core Value**: Enable users to submit ideas and receive structured specifications immediately, establishing the foundation for future planning and execution phases.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (FastAPI)
- Frontend: TypeScript 5.0+ / React 18+

**Primary Dependencies**:
- Backend: FastAPI 0.104+, Pydantic 2.5+, uvicorn
- Frontend: React 18+, TypeScript 5+, Vite 5+, TanStack Query (React Query)

**Storage**: In-memory only (Python dictionaries/lists) - No database required for Phase 1

**Testing**:
- Backend: pytest 7.4+, pytest-asyncio
- Frontend: Vitest, React Testing Library

**Target Platform**:
- Backend: Linux/macOS/WSL (development), containerized for deployment
- Frontend: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)

**Project Type**: Web application (separate backend API + frontend SPA)

**Performance Goals**:
- Spec generation: <2 seconds for typical user input
- API response time: <500ms p95
- Frontend TTI (Time to Interactive): <3 seconds

**Constraints**:
- No persistence required (in-memory only)
- No authentication/authorization in Phase 1
- Single-user context per request (no session management)
- No AI model orchestration yet (deterministic parsing only)

**Scale/Scope**:
- Support 10-20 concurrent users (development/demo)
- Input: 50-500 word intent descriptions
- Output: Structured specs with 3-10 key entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **I. Reusable Intelligence**: Backend spec builder is designed as a reusable component, not tied to specific domains. Frontend is a thin presentation layer.

✅ **II. Intelligence-First**: Clear separation between reasoning (spec builder) and execution (no execution in Phase 1). System interprets "why" (user intent) before defining "what" (structured spec).

✅ **III. Domain-Agnostic & Modular**: Core spec builder uses generic patterns (entities, constraints, goals). API layer is cleanly separated from business logic. Frontend components are modular and reusable.

✅ **IV. Skill-Based**: Spec builder composed of discrete skills: intent parsing, entity extraction, constraint identification, assumption detection.

✅ **V. Safety & Introspectability**: All processing transparent and logged. Context includes full audit trail. Frontend displays complete reasoning chain.

✅ **VI. Frozen Intelligence Architecture**: Phase 1 builds on existing `src/intelligence/` frozen layer without modifications. Extends through new spec-building skills only.

**Status**: ✅ **PASS** - No constitutional violations

## Project Structure

### Documentation (this feature)

```text
specs/sdd-phase1-frontend-backend/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Data structures
├── quickstart.md        # Phase 1: Getting started guide
└── contracts/           # Phase 1: API specifications
    └── openapi.yaml
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── spec.py          # POST /spec endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── context.py       # Request-scoped context
│   │   ├── engine.py        # Orchestrates spec generation
│   │   └── spec_builder.py  # Intent → Spec transformer
│   ├── models/
│   │   ├── __init__.py
│   │   ├── intent.py        # Input model
│   │   └── spec.py          # Output model
│   └── skills/
│       ├── __init__.py
│       ├── entity_extractor.py
│       ├── constraint_parser.py
│       └── goal_identifier.py
├── tests/
│   ├── unit/
│   │   ├── test_spec_builder.py
│   │   └── test_skills.py
│   ├── integration/
│   │   └── test_api.py
│   └── contract/
│       └── test_openapi_compliance.py
├── pyproject.toml
└── README.md

frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── IntentInput.tsx    # Text area + submit
│   │   ├── SpecOutput.tsx     # Structured spec display
│   │   └── ErrorDisplay.tsx   # Error handling
│   ├── api/
│   │   └── client.ts          # Backend API client
│   ├── types/
│   │   └── spec.ts            # TypeScript types
│   └── hooks/
│       └── useSpecGeneration.ts
├── tests/
│   ├── components/
│   └── integration/
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

**Structure Decision**: Selected **Web application** structure (Option 2) because the user explicitly requested frontend-backend architecture. Backend and frontend are in separate directories with independent build systems, enabling parallel development and independent deployment.

## Complexity Tracking

> No constitutional violations - this section is not applicable.

---

## Phase 0: Research & Technology Decisions

**Purpose**: Resolve all unknowns and document technology choices

### Research Tasks

1. **FastAPI Best Practices for Spec Generation**
   - Research: Optimal request/response patterns for text-to-structured transformations
   - Research: Error handling patterns for invalid/ambiguous input
   - Research: CORS configuration for local development

2. **React Component Patterns for Structured Data Display**
   - Research: Best practices for rendering nested/hierarchical specs
   - Research: Markdown rendering vs custom components
   - Research: Real-time validation UI patterns

3. **TypeScript Type Safety for API Contracts**
   - Research: OpenAPI → TypeScript code generation tools
   - Research: Runtime validation with Pydantic → Zod equivalence

4. **Testing Strategy for Intent Parsing**
   - Research: Test data generation for varied user inputs
   - Research: Snapshot testing for structured outputs
   - Research: Contract testing between frontend/backend

**Output**: `research.md` with decisions and rationale

---

## Phase 1: Design & Contracts

### 1. Data Model Design

**Output**: `data-model.md`

#### Core Entities

**UserIntent** (Input)
- `text`: string (50-500 words)
- `timestamp`: ISO 8601 timestamp
- `request_id`: UUID

**StructuredSpec** (Output)
- `goal`: string (primary objective)
- `entities`: List[Entity]
- `constraints`: List[Constraint]
- `assumptions`: List[Assumption]
- `metadata`: SpecMetadata

**Entity**
- `name`: string
- `type`: enum (Domain, Resource, Actor, Process)
- `description`: string
- `attributes`: List[string]
- `relationships`: List[Relationship]

**Constraint**
- `type`: enum (Performance, Security, Business, Technical)
- `description`: string
- `priority`: enum (Must, Should, Could)

**Assumption**
- `description`: string
- `confidence`: enum (High, Medium, Low)
- `needs_clarification`: boolean

**SpecMetadata**
- `generated_at`: ISO 8601 timestamp
- `processing_time_ms`: float
- `confidence_score`: float (0.0-1.0)
- `warnings`: List[string]

#### State Transitions

Phase 1 is stateless - no transitions. Each request is independent.

#### Validation Rules

- Intent text: 50-500 words (frontend and backend validation)
- Entity names: must be unique within spec
- Constraints: at least 1 "Must" priority
- Goal: required, non-empty
- Confidence score: 0.0-1.0 range

### 2. API Contract Design

**Output**: `contracts/openapi.yaml`

#### POST /api/v1/spec

**Request**:
```json
{
  "text": "Create a todo application with task management, priorities, and tags"
}
```

**Response 200**:
```json
{
  "goal": "Build a task management system with priority and categorization features",
  "entities": [
    {
      "name": "Task",
      "type": "Domain",
      "description": "Core work item that users manage",
      "attributes": ["title", "description", "priority", "tags", "status"],
      "relationships": [
        {"type": "belongs_to", "target": "User"}
      ]
    },
    {
      "name": "Tag",
      "type": "Resource",
      "description": "Categorization label for tasks",
      "attributes": ["name", "color"],
      "relationships": [
        {"type": "many_to_many", "target": "Task"}
      ]
    }
  ],
  "constraints": [
    {
      "type": "Business",
      "description": "Users must be able to filter tasks by priority",
      "priority": "Must"
    },
    {
      "type": "Business",
      "description": "Tags should support color coding for visual distinction",
      "priority": "Should"
    }
  ],
  "assumptions": [
    {
      "description": "Single-user application (no multi-tenancy)",
      "confidence": "Medium",
      "needs_clarification": true
    }
  ],
  "metadata": {
    "generated_at": "2025-12-31T10:30:00Z",
    "processing_time_ms": 123.45,
    "confidence_score": 0.85,
    "warnings": []
  }
}
```

**Response 400** (Invalid Input):
```json
{
  "error": "Invalid input",
  "details": "Intent text must be between 50-500 words. Received: 20 words."
}
```

**Response 422** (Ambiguous Intent):
```json
{
  "error": "Ambiguous intent",
  "details": "Unable to identify primary goal. Please clarify the main purpose.",
  "suggestions": [
    "Specify whether this is a web or mobile application",
    "Clarify if users need authentication"
  ]
}
```

#### GET /api/v1/health

**Response 200**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 3. Component Design

#### Frontend Components

**IntentInput**
- Props: `onSubmit: (text: string) => void`, `isLoading: boolean`
- Features: Word count, validation, submit button state
- Validation: Client-side 50-500 word check

**SpecOutput**
- Props: `spec: StructuredSpec | null`, `isLoading: boolean`
- Features: Collapsible sections, entity graph visualization
- Display: Goal (header), Entities (cards), Constraints (list), Assumptions (warnings)

**ErrorDisplay**
- Props: `error: ApiError | null`
- Features: Dismissible, actionable suggestions
- Types: validation errors, ambiguity errors, server errors

#### Backend Components

**SpecBuilder** (Core Logic)
```python
class SpecBuilder:
    def build(self, intent: UserIntent) -> StructuredSpec:
        """Transform intent into structured spec."""
        # 1. Extract goal
        goal = self._identify_goal(intent.text)

        # 2. Extract entities
        entities = self._extract_entities(intent.text)

        # 3. Identify constraints
        constraints = self._parse_constraints(intent.text)

        # 4. Detect assumptions
        assumptions = self._detect_assumptions(intent.text, entities)

        # 5. Calculate confidence
        confidence = self._calculate_confidence(goal, entities, constraints)

        return StructuredSpec(...)
```

**Skills** (Composable Logic)
- `EntityExtractorSkill`: Identifies nouns and relationships
- `GoalIdentifierSkill`: Finds primary objective
- `ConstraintParserSkill`: Detects requirements and limitations
- `AssumptionDetectorSkill`: Identifies implicit assumptions

### 4. Quickstart Guide

**Output**: `quickstart.md`

Content:
- Prerequisites (Python 3.11+, Node 18+)
- Backend setup (venv, pip install, uvicorn run)
- Frontend setup (npm install, npm run dev)
- First request (curl example, browser demo)
- Architecture overview diagram
- Next steps (Phase 2 preview)

---

## Phase 1 Deliverables Summary

**Documentation**:
- ✅ research.md - Technology decisions and rationale
- ✅ data-model.md - Complete data structures with validation rules
- ✅ contracts/openapi.yaml - Full API specification
- ✅ quickstart.md - Getting started guide

**Code** (to be implemented after planning):
- Backend API with /spec endpoint
- Frontend SPA with intent input and spec display
- Unit tests for all skills and components
- Integration tests for API
- Contract tests for OpenAPI compliance

**Quality Gates**:
- All endpoints match OpenAPI specification
- Frontend TypeScript types match backend Pydantic models
- Test coverage >80% for core logic
- API response time <500ms for sample inputs
- Frontend renders without errors for all valid specs

---

## Non-Goals (Explicitly Out of Scope)

- ❌ Planning agent (Phase 2)
- ❌ Task execution (Phase 2+)
- ❌ Persistence/database (Phase 2+)
- ❌ Authentication/authorization (Phase 2+)
- ❌ AI model integration (Phase 2+)
- ❌ Multi-user sessions (Phase 2+)
- ❌ Real-time collaboration (Future)

---

## Success Criteria

1. **Functional**:
   - ✅ User can submit intent via frontend
   - ✅ Backend generates structured spec in <2 seconds
   - ✅ Frontend displays spec with all sections
   - ✅ Errors are handled gracefully with helpful messages

2. **Technical**:
   - ✅ API matches OpenAPI specification
   - ✅ Frontend types match backend models
   - ✅ Test coverage >80% on core logic
   - ✅ No constitutional violations

3. **Quality**:
   - ✅ Code follows project standards (ruff, mypy, eslint)
   - ✅ Documentation complete and accurate
   - ✅ Architecture is clean and extensible

4. **Readiness**:
   - ✅ Foundation ready for Phase 2 (planning agents)
   - ✅ Clear extension points identified
   - ✅ Performance baseline established

---

## Next Steps (After /sp.plan)

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement Phase 0: Research (resolve unknowns)
3. Implement Phase 1: Core components (spec builder, API, UI)
4. Phase 2 Planning: Add planning agents and task generation

**Branch**: `phase1-frontend-backend`
**Plan Location**: `/specs/sdd-phase1-frontend-backend/plan.md`
**Ready for**: Task generation (`/sp.tasks`)
