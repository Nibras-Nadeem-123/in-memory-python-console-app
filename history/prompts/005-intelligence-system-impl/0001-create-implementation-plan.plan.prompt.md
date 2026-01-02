---
id: "0013"
title: "Create Implementation Plan"
stage: "plan"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "implementation-plan"
branch: "005-intelligence-system-impl"
user: "/sp.plan"
command: "n/a"
labels:
  - "implementation"
  - "planning"
  - "architecture"
  - "roadmap"
links:
  plan: "specs/implementation-plan/plan.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/implementation-plan/plan.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.plan
Create an implementation plan to turn the architecture into code.

Include:
- Directory structure
- Module responsibilities
- Order of implementation
- Dependencies

# Response

Created `specs/implementation-plan/plan.md` with comprehensive 8-week implementation plan.

**Directory Structure:**
```
src/intelligence/
├── core/              # Intelligence model, states, boundaries
├── context/           # 3-level hierarchy (Global → Session → Execution)
├── skills/            # 6 cognitive skills + interfaces
├── agents/            # 5 agents + interfaces
├── runtime/           # Engine, routing, execution
├── introspection/     # Logging, tracing, metrics
└── llm/               # LLM abstraction layer
```

**Module Responsibilities:**
- Core: Defines 10-stage lifecycle, TaskState enum, reasoning boundaries
- Context: State management, history, isolation, persistence
- Skills: Stateless cognitive operations (intent parsing, planning, etc.)
- Agents: Stateful orchestrators that invoke skills
- Runtime: Engine lifecycle, skill execution, agent routing
- Introspection: Event logging, trace reconstruction, metrics

**8-Week Implementation Order:**

| Week | Phase | Focus |
|------|-------|-------|
| 1 | Foundation | Core types, exceptions, context base |
| 2 | Skills Framework | Skill interface, registry, 6 skills |
| 3 | Runtime Core | Engine, context manager, skill execution |
| 4 | Agents | 5 agent implementations |
| 5 | Routing & Errors | Agent routing, error handling |
| 6 | Persistence | Serialization, checkpoints, rollback |
| 7 | LLM Integration | LLM abstraction layer |
| 8 | Integration | CLI, E2E tests, polish |

**Dependencies:**
- Core (foundation, no deps)
- Context (depends on core)
- Skills (depends on core, context)
- Runtime (depends on core, context, skills)
- Agents (depends on core, context, skills, runtime)
- Introspection (depends on all)
- LLM (depends on core, independent layer)

**Test Coverage Targets:** >90% overall

**Migration Strategy:** Keep existing todo app separate, integrate framework later
