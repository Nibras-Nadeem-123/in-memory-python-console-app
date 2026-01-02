# Phase 1 SDD System Constitution

**Version**: 1.0.0
**Ratified**: 2025-12-31
**Status**: IMMUTABLE
**Scope**: Specification Generation System (Frontend + Backend)

---

## Purpose

Phase 1 exists to transform human intent into inspectable, structured specifications.

**What it does**: Accept natural language descriptions (50-500 words) and extract goal, entities, constraints, and assumptions with confidence scoring.

**What it does NOT do**: Planning, execution, persistence, authentication, or multi-turn conversations.

**Success means**: Given the same input, the system MUST produce deterministic, transparent, and reproducible specifications that humans can inspect, validate, and use as input for Phase 2+.

---

## Core Principles

### 1. Specification Before Execution
The system transforms intent → specification ONLY. It does not plan or execute. Phase 1's output is the contract for all downstream phases.

**Rationale**: Clear separation of concerns. Specification quality determines all downstream success.

### 2. Determinism and Reproducibility
Given identical input, the system MUST produce identical output. No randomness, no ML inference, no timestamps in output.

**Rationale**: Specifications must be testable, auditable, and debuggable.

### 3. Separation of Concerns
Frontend handles presentation. Backend handles transformation. Skills handle extraction. Each layer has ONE job.

**Rationale**: Modularity enables testing, replacement, and independent evolution.

### 4. Stateless Execution
No persistence. No session. No memory between requests. Each request is independent and complete.

**Rationale**: Simplicity, testability, and horizontal scalability.

### 5. Human-in-the-Loop
The system assists human judgment, never replaces it. All outputs include confidence scores and metadata for human validation.

**Rationale**: Specifications require human domain expertise. AI assists, humans decide.

---

## Architectural Guarantees

### The System SHALL

1. **Accept Intent (50-500 words)**: Validate word count before processing
2. **Extract 4 Components**: Goal, entities, constraints, assumptions
3. **Return Structured JSON**: Conforming to StructuredSpec schema
4. **Include Confidence Score**: Algorithmic quality assessment (0.0-1.0)
5. **Provide Warnings**: Surface ambiguities, missing information
6. **Execute Deterministically**: Same input → same output
7. **Isolate Requests**: No shared state between API calls
8. **Log All Operations**: Request method, path, status, duration
9. **Handle Errors Gracefully**: Return structured error responses with suggestions
10. **Respect Type Contracts**: Frontend TypeScript ↔ Backend Pydantic exact match

### The System SHALL NOT

1. **Persist Data**: No database, no file storage, no session state
2. **Authenticate Users**: No login, no authorization, no user management
3. **Use ML/AI APIs**: Pattern-based extraction only (regex, keywords)
4. **Plan or Execute**: No task breakdown, no code generation
5. **Modify Inputs**: Intent text is read-only
6. **Share State**: No global mutable state across requests
7. **Cache Results**: Each request is independently processed
8. **Make Assumptions About Users**: All context comes from the intent text
9. **Exceed Scope**: No features beyond spec generation
10. **Break Type Safety**: All models validated at runtime

---

## Component Boundaries

### 1. Frontend (React + TypeScript)
**Responsibility**: User interaction and result presentation

**May**:
- Validate word count (50-500)
- Display spec components (goal, entities, constraints, assumptions)
- Show loading states and errors
- Provide retry mechanisms

**May NOT**:
- Perform entity extraction
- Calculate confidence scores
- Store specifications
- Communicate with anything except `/api/v1/spec` and `/api/v1/health`

**Interface**: HTTP POST to `/api/v1/spec` with `{text: string}`, receive `StructuredSpec`

---

### 2. Backend API (FastAPI)
**Responsibility**: HTTP interface and request orchestration

**May**:
- Validate request format and word count
- Route requests to Engine
- Format responses (success/error)
- Log requests and timing
- Apply CORS rules

**May NOT**:
- Perform extraction logic
- Contain business rules
- Store state between requests
- Make decisions about entity types or constraints

**Interface**:
- Input: `POST /api/v1/spec` with `IntentRequest`
- Output: `StructuredSpec` or `ErrorResponse`

---

### 3. Engine (`app/core/engine.py`)
**Responsibility**: Request lifecycle management

**May**:
- Create RequestContext per request
- Instantiate SpecBuilder
- Coordinate execution flow
- Catch and wrap exceptions

**May NOT**:
- Perform extraction logic
- Validate input (delegated to API layer)
- Store state across requests
- Contain skill-specific logic

**Interface**: `execute(UserIntent) -> StructuredSpec`

---

### 4. Context (`app/core/context.py`)
**Responsibility**: Request-scoped state container

**May**:
- Hold UserIntent (read-only)
- Store intermediate results in typed dict
- Provide getters/setters for state

**May NOT**:
- Persist beyond request scope
- Communicate with external systems
- Validate or transform data
- Be shared across requests

**Interface**: `RequestContext(intent: UserIntent)` with `get(key)` and `set(key, value)`

---

### 5. SpecBuilder (`app/core/spec_builder.py`)
**Responsibility**: Skill orchestration and spec assembly

**May**:
- Instantiate skills (GoalIdentifier, EntityExtractor, ConstraintParser, AssumptionDetector)
- Execute skills in sequence
- Aggregate results into StructuredSpec
- Calculate confidence score from components

**May NOT**:
- Validate intent (delegated to API layer)
- Perform extraction logic (delegated to skills)
- Store state between calls
- Make HTTP requests

**Current Limitation**: Skills are hard-coded (see Evolution Policy)

**Interface**: `build(RequestContext) -> StructuredSpec`

---

### 6. Skills (`app/skills/*.py`)
**Responsibility**: Single-purpose extraction logic

**Each Skill May**:
- Read intent text from context
- Apply pattern matching (regex, keywords, heuristics)
- Return typed result (str, List[Entity], List[Constraint], List[Assumption])
- Raise ValueError if extraction fails

**Each Skill May NOT**:
- Call other skills
- Modify context (read-only access to intent)
- Perform I/O operations
- Store internal state
- Use ML/AI APIs

**Interface**: All skills implement `Skill` abstract base class with `execute(RequestContext) -> T`

**Current Skills**:
1. **GoalIdentifierSkill**: Extract primary objective (returns `str`)
2. **EntityExtractorSkill**: Identify domain entities (returns `List[Entity]`)
3. **ConstraintParserSkill**: Parse requirements (returns `List[Constraint]`)
4. **AssumptionDetectorSkill**: Surface implicit assumptions (returns `List[Assumption]`)

---

## Evolution Policy

### Phase 1 is FROZEN

Once deployed, Phase 1's behavior is immutable. Future work extends, not modifies.

**Rationale**: Phase 1 is a stable foundation. Breaking changes invalidate downstream phases.

### Permitted Changes

| Change Type | Allowed | Process |
|-------------|---------|---------|
| Bug fixes (determinism violated) | ✅ Yes | Patch version (1.0.x) |
| Performance optimizations (no behavior change) | ✅ Yes | Patch version (1.0.x) |
| New skills (extend functionality) | ✅ Yes | Minor version (1.x.0) + document |
| New attributes on existing models | ✅ Yes | Minor version (1.x.0) + backward compat |
| Documentation updates | ✅ Yes | No version bump |

### Prohibited Changes

| Change Type | Impact | Alternative |
|-------------|--------|-------------|
| Change StructuredSpec schema (breaking) | ❌ Blocks Phase 2+ | Create v2 API endpoint |
| Remove skills or fields | ❌ Breaks contracts | Deprecate, don't remove |
| Add randomness or ML APIs | ❌ Violates determinism | Build Phase 2+ extension |
| Add persistence or state | ❌ Violates stateless principle | Build separate service |
| Change skill execution order | ⚠️ May break determinism | Requires extensive testing |

### Extension Points (Future Phases)

Phase 2+ MAY extend Phase 1 through:

1. **New API endpoints**: `/api/v1/plan`, `/api/v1/execute` (Phase 1 untouched)
2. **Wrapper services**: Planning service that calls Phase 1, then adds planning logic
3. **Skill registry**: Dynamic skill loading (requires SpecBuilder refactor)
4. **Plugin system**: User-defined skills implementing `Skill` interface

**Critical Rule**: Future phases MUST NOT modify Phase 1 behavior. They MAY consume Phase 1 output.

---

## Success Criteria

Phase 1 is successful when:

### Functional Requirements
- ✅ Accepts 50-500 word intent
- ✅ Extracts goal, entities (≥1), constraints (≥1), assumptions
- ✅ Returns valid StructuredSpec JSON
- ✅ Calculates confidence score
- ✅ Handles errors gracefully with suggestions

### Non-Functional Requirements
- ✅ **Deterministic**: Same input → same output
- ✅ **Transparent**: All extraction logic is inspectable (no black boxes)
- ✅ **Reproducible**: No side effects, no hidden state
- ✅ **Fast**: p95 latency < 500ms
- ✅ **Typed**: Pydantic + TypeScript full coverage
- ✅ **Documented**: Every module, class, function has docstrings

### Quality Gates (Not Yet Met)
- ❌ **Test Coverage**: 0% → Target 80%+ (unit + integration + contract)
- ❌ **Extensibility**: Hard-coded skills → Target: SkillRegistry
- ❌ **Dependency Injection**: Global Engine singleton → Target: FastAPI Depends()

**Status**: Phase 1 is FUNCTIONAL but not COMPLETE. Critical quality gaps must be addressed before Phase 2.

---

## Governance

### 1. Respect the Constitution
All code reviews, PRs, and architectural decisions MUST verify compliance with this document.

**Violation examples**:
- ❌ Adding database calls to skills
- ❌ Using ML APIs for entity extraction
- ❌ Sharing state between requests
- ❌ Breaking frontend-backend type contract

### 2. Preserve Modularity
Each component boundary is sacred. Cross-boundary access requires explicit interfaces.

**Examples**:
- ✅ Frontend calls API via HTTP
- ✅ API uses Engine via `execute()` method
- ✅ Skills read context via `get()` method
- ❌ Frontend directly imports backend Python code
- ❌ Skills call other skills directly
- ❌ API contains extraction logic

### 3. Document Deviations
If a violation is necessary (rare), it requires:
1. ADR (Architecture Decision Record) with full justification
2. Migration plan to restore compliance
3. Explicit approval from architect
4. Timeline for remediation

### 4. Test Everything
All new code requires:
- Unit tests (pure logic)
- Integration tests (API endpoints)
- Contract tests (frontend-backend interface)

**Current Status**: 0% coverage is unacceptable and must be remediated.

### 5. Version Bumps
Follow semantic versioning strictly:
- **Patch (1.0.x)**: Bug fixes, performance, docs
- **Minor (1.x.0)**: New skills, backward-compatible additions
- **Major (x.0.0)**: Breaking changes (requires new API version)

---

## Known Limitations (Technical Debt)

### Critical (Must Fix Before Phase 2)
1. **Zero Test Coverage** (Risk: HIGH)
   - Cannot safely refactor or extend
   - Fix: Write comprehensive test suite (Sprint 1)

2. **Hard-Coded Skill Registration** (Risk: HIGH)
   - Adding skills requires modifying SpecBuilder
   - Fix: Implement SkillRegistry (Sprint 2)

3. **Global Engine Singleton** (Risk: MEDIUM)
   - Makes testing difficult
   - Fix: Use FastAPI dependency injection (Sprint 2)

### Important (Should Fix)
4. **No API Versioning Strategy** (Risk: MEDIUM)
   - Breaking changes will require backward compatibility hacks
   - Fix: Document versioning policy (Sprint 4)

5. **Untyped Context State** (Risk: LOW)
   - `Dict[str, Any]` allows any data
   - Fix: Create typed `IntermediateResults` dataclass (Sprint 3)

6. **Manual Type Duplication** (Risk: LOW)
   - Frontend TypeScript manually kept in sync with Pydantic
   - Fix: Auto-generate TypeScript from Pydantic (Sprint 4)

---

## References

- **Analysis**: `PHASE1_ANALYSIS.md` (comprehensive architectural evaluation)
- **Framework Constitution**: `.specify/memory/constitution.md` (parent principles)
- **ADR**: `history/adr/003-spec-driven-development-system-architecture.adr.md`
- **Backend Code**: `backend/app/` (implementation)
- **Frontend Code**: `frontend/src/` (implementation)
- **Documentation**: `QUICKSTART.md`, `HOW_TO_RUN.md`, `TROUBLESHOOTING.md`

---

## Amendment Process

This Constitution may be amended through:

1. **Proposal**: Submit ADR with rationale for change
2. **Review**: Architect evaluates impact on downstream phases
3. **Approval**: Requires demonstration that change preserves Phase 1 guarantees
4. **Migration**: Update all affected code, tests, and documentation
5. **Version Bump**: Follow semantic versioning rules

**Last Amendment**: None (1.0.0 initial ratification)

---

**Signature**: Constitution ratified by architectural review on 2025-12-31.

**Status**: This Constitution is now in effect for all Phase 1 development and maintenance.
