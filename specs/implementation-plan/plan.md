# Implementation Plan: Reusable Intelligence Framework

**Plan ID:** IMPLEMENTATION-PLAN
**Version:** 1.0.0
**Status:** Draft
**Created:** 2025-12-29
**Based On:** All system specifications

---

## 1. Directory Structure

### 1.1 Proposed Structure

```
src/
├── intelligence/                          # Core intelligence framework
│   ├── __init__.py                        # Exports main public API
│   │
│   ├── core/                              # Core intelligence components
│   │   ├── __init__.py
│   │   ├── intelligence_model.py          # Intelligence model (10-stage lifecycle)
│   │   ├── task_stage.py                  # TaskStage enum and states
│   │   ├── task_state.py                  # TaskState enum (unified)
│   │   ├── reasoning_boundary.py          # Reasoning/Execution boundary enforcement
│   │   └── exceptions.py                  # Core exceptions and error taxonomy
│   │
│   ├── context/                           # Context and memory system
│   │   ├── __init__.py
│   │   ├── global_context.py              # GlobalContext (singleton)
│   │   ├── session_context.py             # SessionContext (per user)
│   │   ├── execution_context.py           # ExecutionContext (per request)
│   │   ├── state.py                       # MutableState with versioning
│   │   ├── history.py                     # HistoryLog and HistoryEvent
│   │   ├── checkpoint.py                  # Checkpoint for rollback
│   │   ├── persistence.py                 # Context serialization
│   │   └── isolation.py                   # Context isolation enforcement
│   │
│   ├── skills/                            # Cognitive skills
│   │   ├── __init__.py
│   │   ├── skill_interface.py             # CognitiveSkill base class
│   │   ├── skill_result.py                # SkillResult and failure modes
│   │   ├── skill_registry.py              # SkillRegistry for discovery
│   │   ├── intent_parsing.py              # IntentParsingSkill
│   │   ├── spec_generation.py             # SpecificationGenerationSkill
│   │   ├── task_decomposition.py          # TaskDecompositionSkill
│   │   ├── constraint_validation.py       # ConstraintValidationSkill
│   │   ├── execution_planning.py          # ExecutionPlanningSkill
│   │   └── result_evaluation.py           # ResultEvaluationSkill
│   │
│   ├── agents/                            # Reusable agents
│   │   ├── __init__.py
│   │   ├── agent_interface.py             # Agent base class
│   │   ├── agent_message.py               # AgentMessage and AgentArtifact
│   │   ├── agent_registry.py              # AgentRegistry for discovery
│   │   ├── architect_agent.py             # ArchitectAgent
│   │   ├── planner_agent.py               # PlannerAgent
│   │   ├── executor_agent.py              # ExecutorAgent
│   │   ├── reviewer_agent.py              # ReviewerAgent
│   │   └── refiner_agent.py               # RefinerAgent
│   │
│   ├── runtime/                           # Runtime engine
│   │   ├── __init__.py
│   │   ├── engine.py                      # RuntimeEngine (lifecycle)
│   │   ├── engine_state.py                # EngineState enum
│   │   ├── context_manager.py             # ContextManager
│   │   ├── agent_router.py                # AgentRouter (routing logic)
│   │   ├── agent_dispatcher.py            # AgentDispatcher
│   │   ├── skill_executor.py              # SkillExecutor (with sandbox)
│   │   ├── skill_invoker.py               # SkillInvoker protocol
│   │   ├── error_handler.py               # ErrorHandler
│   │   └── health_check.py                # HealthCheck service
│   │
│   ├── introspection/                     # Logging and introspection
│   │   ├── __init__.py
│   │   ├── event_types.py                 # EventType enum
│   │   ├── trace_event.py                 # TraceEvent structure
│   │   ├── introspection_service.py       # IntrospectionService
│   │   ├── logger.py                      # Structured logging
│   │   └── metrics.py                     # Metrics collection
│   │
│   └── llm/                               # LLM integration (abstraction)
│       ├── __init__.py
│       ├── llm_provider.py                # LLMProvider abstract interface
│       ├── llm_config.py                  # LLM configuration
│       └── llm_response.py                # LLMResponse structure
│
├── cli/                                    # CLI entry points
│   ├── __init__.py
│   └── main.py                            # CLI launcher
│
tests/
├── unit/
│   ├── test_core/
│   ├── test_context/
│   ├── test_skills/
│   ├── test_agents/
│   ├── test_runtime/
│   └── test_introspection/
│
├── integration/
│   ├── test_skill_pipeline.py
│   ├── test_agent_collaboration.py
│   └── test_full_execution.py
│
└── fixtures/
    ├── contexts.py
    ├── skills.py
    └── agents.py
```

### 1.2 Key Files Summary

| Layer | Files | Purpose |
|-------|-------|---------|
| **Core** | 6 files | Intelligence model, states, boundaries |
| **Context** | 7 files | 3-level hierarchy, persistence |
| **Skills** | 9 files | 6 cognitive skills + interfaces |
| **Agents** | 8 files | 5 agents + interfaces |
| **Runtime** | 9 files | Engine, routing, execution |
| **Introspection** | 5 files | Logging, tracing, metrics |
| **LLM** | 3 files | LLM abstraction |

---

## 2. Module Responsibilities

### 2.1 Core Layer (`intelligence/core/`)

**Responsibility:** Define the intelligence model and enforce boundaries.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `intelligence_model.py` | 10-stage lifecycle, component definitions | `IntelligenceModel` |
| `task_stage.py` | Stage definitions (INPUT, INTERPRET, etc.) | `TaskStage` enum |
| `task_state.py` | Unified state model (12 states) | `TaskState` enum |
| `reasoning_boundary.py` | Enforce reasoning/execution separation | `ReasoningBoundary` |
| `exceptions.py` | Error taxonomy and core exceptions | `IntelligenceError` |

### 2.2 Context Layer (`intelligence/context/`)

**Responsibility:** Manage state, history, and isolation.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `global_context.py` | Engine-wide singleton context | `GlobalContext` |
| `session_context.py` | Per-user session context | `SessionContext` |
| `execution_context.py` | Per-request execution context | `ExecutionContext` |
| `state.py` | Versioned key-value store | `MutableState` |
| `history.py` | Append-only event log | `HistoryLog`, `HistoryEvent` |
| `checkpoint.py` | State snapshots for rollback | `Checkpoint` |
| `persistence.py` | Serialization/deserialization | `ContextSerializer` |
| `isolation.py` | Cross-context access enforcement | `ContextIsolation` |

### 2.3 Skills Layer (`intelligence/skills/`)

**Responsibility:** Implement stateless, composable cognitive skills.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `skill_interface.py` | Base class for all skills | `CognitiveSkill` |
| `skill_result.py` | SkillResult with failure classification | `SkillResult`, `FailureType` |
| `skill_registry.py` | Skill discovery and registration | `SkillRegistry` |
| `intent_parsing.py` | Parse raw intent to structured form | `IntentParsingSkill` |
| `spec_generation.py` | Generate formal specifications | `SpecificationGenerationSkill` |
| `task_decomposition.py` | Break goals into task trees | `TaskDecompositionSkill` |
| `constraint_validation.py` | Validate constraints | `ConstraintValidationSkill` |
| `execution_planning.py` | Generate execution plans | `ExecutionPlanningSkill` |
| `result_evaluation.py` | Evaluate outcomes | `ResultEvaluationSkill` |

### 2.4 Agents Layer (`intelligence/agents/`)

**Responsibility:** Stateful orchestrators that invoke skills.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `agent_interface.py` | Base class for all agents | `Agent` |
| `agent_message.py` | Inter-agent communication | `AgentMessage`, `AgentArtifact` |
| `agent_registry.py` | Agent discovery and registration | `AgentRegistry` |
| `architect_agent.py` | Design system structure | `ArchitectAgent` |
| `planner_agent.py` | Break specs into tasks | `PlannerAgent` |
| `executor_agent.py` | Perform implementation actions | `ExecutorAgent` |
| `reviewer_agent.py` | Audit quality and correctness | `ReviewerAgent` |
| `refiner_agent.py` | Improve outputs iteratively | `RefinerAgent` |

### 2.5 Runtime Layer (`intelligence/runtime/`)

**Responsibility:** Orchestrate execution and manage lifecycle.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `engine.py` | Main engine lifecycle | `RuntimeEngine` |
| `engine_state.py` | Engine state management | `EngineState` enum |
| `context_manager.py` | Context creation and lifecycle | `ContextManager` |
| `agent_router.py` | Route tasks to agents | `AgentRouter` |
| `agent_dispatcher.py` | Invoke and manage agents | `AgentDispatcher` |
| `skill_executor.py` | Execute skills with safety | `SkillExecutor` |
| `skill_invoker.py` | Skill invocation protocol | `SkillInvoker` |
| `error_handler.py` | Error classification/recovery | `ErrorHandler` |
| `health_check.py` | System health monitoring | `HealthCheck` |

### 2.6 Introspection Layer (`intelligence/introspection/`)

**Responsibility:** Logging, tracing, and metrics.

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `event_types.py` | Event type definitions | `EventType` enum |
| `trace_event.py` | Trace event structure | `TraceEvent` |
| `introspection_service.py` | Central introspection service | `IntrospectionService` |
| `logger.py` | Structured logging | `IntelligenceLogger` |
| `metrics.py` | Metrics collection | `MetricsCollector` |

### 2.7 LLM Layer (`intelligence/llm/`)

**Responsibility:** LLM provider abstraction (for extensibility).

| Module | Responsibility | Exports |
|--------|---------------|---------|
| `llm_provider.py` | Abstract LLM interface | `LLMProvider` |
| `llm_config.py` | LLM configuration | `LLMConfig` |
| `llm_response.py` | LLM response structure | `LLMResponse` |

---

## 3. Implementation Order

### Phase 1: Foundation (Week 1)

**Goal:** Establish core types, exceptions, and context base.

```
Day 1-2: Core Types
├── intelligence/core/exceptions.py      # Error taxonomy
├── intelligence/core/task_stage.py      # TaskStage enum
├── intelligence/core/task_state.py      # TaskState enum
└── intelligence/core/__init__.py        # Exports

Day 3-4: Context Foundation
├── intelligence/context/isolation.py    # Isolation rules
├── intelligence/context/state.py        # MutableState
├── intelligence/context/history.py      # HistoryLog, HistoryEvent
└── intelligence/context/__init__.py     # Exports

Day 5: Context Hierarchy
├── intelligence/context/global_context.py
├── intelligence/context/session_context.py
├── intelligence/context/execution_context.py
└── intelligence/context/__init__.py
```

**Dependencies:** None (foundation)
**Tests:** Test State versioning, History append-only, Isolation

### Phase 2: Skills Framework (Week 2)

**Goal:** Implement skill interface and registry.

```
Day 1-2: Skill Framework
├── intelligence/skills/skill_interface.py
├── intelligence/skills/skill_result.py
├── intelligence/skills/skill_registry.py
└── intelligence/skills/__init__.py

Day 3-4: First Cognitive Skills
├── intelligence/skills/intent_parsing.py
├── intelligence/skills/spec_generation.py
└── intelligence/skills/__init__.py (updated)

Day 5: More Skills
├── intelligence/skills/task_decomposition.py
├── intelligence/skills/constraint_validation.py
└── intelligence/skills/execution_planning.py
```

**Dependencies:** Phase 1 (types for inputs/outputs)
**Tests:** Test skill invocation, failure classification, registry lookup

### Phase 3: Runtime Core (Week 3)

**Goal:** Build engine, context manager, and skill execution.

```
Day 1-2: Engine and Context Manager
├── intelligence/runtime/engine.py
├── intelligence/runtime/engine_state.py
├── intelligence/runtime/context_manager.py
└── intelligence/runtime/__init__.py

Day 3-4: Skill Execution
├── intelligence/runtime/skill_invoker.py
├── intelligence/runtime/skill_executor.py
├── intelligence/runtime/error_handler.py
└── intelligence/runtime/__init__.py (updated)

Day 5: Introspection Foundation
├── intelligence/introspection/event_types.py
├── intelligence/introspection/trace_event.py
├── intelligence/introspection/logger.py
└── intelligence/introspection/__init__.py
```

**Dependencies:** Phase 1 (context), Phase 2 (skills)
**Tests:** Test engine lifecycle, skill execution with timeout

### Phase 4: Agents (Week 4)

**Goal:** Implement agents that orchestrate skills.

```
Day 1-2: Agent Framework
├── intelligence/agents/agent_interface.py
├── intelligence/agents/agent_message.py
├── intelligence/agents/agent_registry.py
└── intelligence/agents/__init__.py

Day 3-4: Core Agents
├── intelligence/agents/architect_agent.py
├── intelligence/agents/planner_agent.py
├── intelligence/agents/executor_agent.py
└── intelligence/agents/__init__.py (updated)

Day 5: Review and Refine Agents
├── intelligence/agents/reviewer_agent.py
├── intelligence/agents/refiner_agent.py
└── intelligence/agents/__init__.py (updated)
```

**Dependencies:** Phase 2 (skills), Phase 3 (runtime)
**Tests:** Test agent routing, collaboration protocols

### Phase 5: Routing and Error Handling (Week 5)

**Goal:** Connect all components with routing and error handling.

```
Day 1-2: Agent Routing
├── intelligence/runtime/agent_router.py
├── intelligence/runtime/agent_dispatcher.py
└── intelligence/runtime/__init__.py (updated)

Day 3-4: Error Handling Integration
├── intelligence/runtime/error_handler.py (completed)
├── intelligence/core/reasoning_boundary.py
└── intelligence/core/__init__.py (updated)

Day 5: Introspection Integration
├── intelligence/introspection/introspection_service.py
├── intelligence/introspection/metrics.py
└── intelligence/introspection/__init__.py
```

**Dependencies:** Phase 3 (runtime), Phase 4 (agents)
**Tests:** Test routing decisions, error propagation, boundary crossing

### Phase 6: Persistence and Checkpoints (Week 6)

**Goal:** Add serialization, persistence, and rollback.

```
Day 1-2: Serialization
├── intelligence/context/persistence.py
├── intelligence/context/checkpoint.py
└── intelligence/context/__init__.py (updated)

Day 3-4: Rollback Implementation
├── intelligence/context/checkpoint.py (rollback methods)
└── intelligence/context/history.py (rollback events)

Day 5: Integration Tests
├── Test full serialization round-trip
├── Test checkpoint create/restore
└── Test rollback flow
```

**Dependencies:** Phase 1 (context)
**Tests:** Test serialization, rollback, persistence

### Phase 7: LLM Integration (Week 7)

**Goal:** Define LLM abstraction (extensible, not tied to provider).

```
Day 1-2: LLM Interface
├── intelligence/llm/llm_provider.py
├── intelligence/llm/llm_config.py
├── intelligence/llm/llm_response.py
└── intelligence/llm/__init__.py

Day 3: Default Implementation (Optional)
├── intelligence/llm/openai_provider.py  # If needed
└── intelligence/llm/anthropic_provider.py # If needed

Day 4-5: Integration with Skills
├── Update intent_parsing.py to use LLM
├── Update spec_generation.py to use LLM
└── Test LLM integration
```

**Dependencies:** Phase 2 (skills)
**Tests:** Test LLM abstraction, provider switching

### Phase 8: Integration and Polish (Week 8)

**Goal:** Full integration, CLI, documentation.

```
Day 1-2: CLI Integration
├── src/cli/main.py
└── src/__init__.py (updated)

Day 3-4: Integration Tests
├── test_full_execution.py
├── test_agent_collaboration.py
└── test_skill_pipeline.py

Day 5: Documentation and Cleanup
├── Update README.md
├── Add docstrings
└── Run mypy, ruff, coverage
```

**Dependencies:** All previous phases
**Tests:** Full integration tests, E2E tests

---

## 4. Dependencies Graph

### 4.1 Module Dependency Matrix

```
                    Phase 1    Phase 2    Phase 3    Phase 4    Phase 5    Phase 6    Phase 7
                        │          │          │          │          │          │          │
core/types  ────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼
                        │          │          │          │          │          │          │
context/     ────────────┼──────────┤          │          │          │          │          │
                        │          │          │          │          │          │          │
skills/      ────────────┼──────────┤          │          │          │          │          │
                        │          │          │          │          │          │          │
runtime/     ────────────┼──────────┼──────────┤          │          │          │          │
                        │          │          │          │          │          │          │
agents/      ────────────┼──────────┼──────────┼──────────┤          │          │          │
                        │          │          │          │          │          │          │
introspection───────────┼──────────┼──────────┼──────────┼──────────┤          │          │
                        │          │          │          │          │          │          │
llm/         ────────────┼──────────┤          │          │          │          │          │
```

### 4.2 Key Dependency Chains

```
Chain 1: Engine → ContextManager → ExecutionContext → MutableState
Chain 2: Engine → AgentDispatcher → Agent → SkillInvoker → Skill
Chain 3: Engine → IntrospectionService → TraceEvent → Logger
Chain 4: Any → Context → HistoryLog → HistoryEvent
```

### 4.3 No-Cycle Guarantee

```
core/          ← No dependencies (foundation)
    ↓
context/       ← Depends on core/
    ↓
skills/        ← Depends on core/, context/
    ↓
runtime/       ← Depends on core/, context/, skills/
    ↓
agents/        ← Depends on core/, context/, skills/, runtime/
    ↓
introspection/ ← Depends on all
    ↓
llm/           ← Depends on core/ (independent layer)
```

---

## 5. Entry Points and Exports

### 5.1 Public API (`intelligence/__init__.py`)

```python
# Main exports for users of the framework
from intelligence.core import (
    IntelligenceModel,
    TaskStage,
    TaskState,
    IntelligenceError,
)

from intelligence.context import (
    GlobalContext,
    SessionContext,
    ExecutionContext,
)

from intelligence.skills import (
    CognitiveSkill,
    SkillRegistry,
    IntentParsingSkill,
    SpecificationGenerationSkill,
    TaskDecompositionSkill,
    ConstraintValidationSkill,
    ExecutionPlanningSkill,
    ResultEvaluationSkill,
)

from intelligence.agents import (
    Agent,
    AgentRegistry,
    ArchitectAgent,
    PlannerAgent,
    ExecutorAgent,
    ReviewerAgent,
    RefinerAgent,
)

from intelligence.runtime import (
    RuntimeEngine,
    EngineState,
)

from intelligence.introspection import (
    IntrospectionService,
    EventType,
)
```

### 5.2 CLI Entry Point (`src/cli/main.py`)

```python
def main():
    """CLI entry point for the intelligence framework."""
    engine = RuntimeEngine()
    engine.start()
    # ... CLI logic ...
```

---

## 6. Test Organization

### 6.1 Test Structure

```
tests/
├── unit/
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_task_state.py
│   │   ├── test_exceptions.py
│   │   └── test_reasoning_boundary.py
│   │
│   ├── test_context/
│   │   ├── __init__.py
│   │   ├── test_state.py
│   │   ├── test_history.py
│   │   ├── test_context_isolation.py
│   │   └── test_persistence.py
│   │
│   ├── test_skills/
│   │   ├── __init__.py
│   │   ├── test_skill_interface.py
│   │   ├── test_skill_registry.py
│   │   ├── test_intent_parsing.py
│   │   ├── test_spec_generation.py
│   │   ├── test_task_decomposition.py
│   │   ├── test_constraint_validation.py
│   │   ├── test_execution_planning.py
│   │   └── test_result_evaluation.py
│   │
│   ├── test_agents/
│   │   ├── __init__.py
│   │   ├── test_agent_interface.py
│   │   ├── test_architect_agent.py
│   │   ├── test_planner_agent.py
│   │   ├── test_executor_agent.py
│   │   ├── test_reviewer_agent.py
│   │   └── test_refiner_agent.py
│   │
│   ├── test_runtime/
│   │   ├── __init__.py
│   │   ├── test_engine.py
│   │   ├── test_context_manager.py
│   │   ├── test_agent_router.py
│   │   ├── test_skill_executor.py
│   │   └── test_error_handler.py
│   │
│   └── test_introspection/
│       ├── __init__.py
│       ├── test_event_types.py
│       ├── test_trace_event.py
│       └── test_introspection_service.py
│
├── integration/
│   ├── __init__.py
│   ├── test_skill_pipeline.py          # Multi-skill composition
│   ├── test_agent_collaboration.py      # Agent-to-agent
│   └── test_full_execution.py           # End-to-end
│
└── fixtures/
    ├── __init__.py
    ├── contexts.py                      # Context fixtures
    ├── skills.py                        # Skill fixtures
    └── agents.py                        # Agent fixtures
```

### 6.2 Coverage Targets

| Layer | Target |
|-------|--------|
| Core | >90% |
| Context | >95% |
| Skills | >90% |
| Agents | >85% |
| Runtime | >90% |
| Introspection | >80% |
| **Overall** | **>90%** |

---

## 7. Migration Strategy

### 7.1 Existing Code Handling

The existing code at `src/` (todo_cli, executor, etc.) is for a todo application. The intelligence framework should be **new code** that can eventually be used by the todo app, not a replacement.

```
src/
├── todo/                               # Existing todo app (keep as-is)
│   ├── todo_cli.py
│   ├── todo_executor.py
│   └── ...
│
└── intelligence/                       # NEW framework (this plan)
    ├── core/
    ├── context/
    ├── skills/
    ├── agents/
    ├── runtime/
    └── ...
```

### 7.2 Integration Path

```
Phase 8+ (Post-Implementation)
├── Create todo_intelligence.py        # Todo-specific intelligence
├── Update todo_cli.py to use framework
└── Deprecate todo_executor.py gradually
```

---

## 8. Success Criteria

| Milestone | Criterion | Target |
|-----------|-----------|--------|
| **Phase 1** | Core types compile, tests pass | 100% unit tests |
| **Phase 2** | Skills invoke correctly | 100% skill tests |
| **Phase 3** | Engine starts, executes empty plan | Integration test |
| **Phase 4** | Agents route and dispatch | Agent tests pass |
| **Phase 5** | Full tracing enabled | Introspection test |
| **Phase 6** | Serialization works | Round-trip test |
| **Phase 7** | LLM abstraction functional | Provider swap test |
| **Phase 8** | All tests pass, coverage >90% | CI pipeline |

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **LLM abstraction complexity** | High | Keep interface minimal, add providers later |
| **Agent collaboration complexity** | Medium | Start with simple request/response |
| **Rollback complexity** | Medium | Implement append-only first, add checkpoints later |
| **Circular dependencies** | High | Enforce dependency order in code review |
| **Test coverage >90%** | Medium | Write tests before implementation (TDD) |

---

**Plan Status:** Ready for Review
**Next Step:** Architect approval → Begin Phase 1
