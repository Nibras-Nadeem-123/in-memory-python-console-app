# Core Intelligence Model Specification

**Spec ID:** CORE-INTELLIGENCE-MODEL
**Version:** 1.0.0
**Status:** Draft
**Created:** 2025-12-29

## 1. Overview

This specification defines the core intelligence model for the reusable intelligence framework. It establishes what constitutes "intelligence" in this system, the lifecycle of reasoning tasks, and the boundaries between reasoning and execution phases.

## 2. What is Intelligence in This System

### 2.1 Definition

**Intelligence** in this system is the **adaptive capability to transform ambiguous intent into structured, executable plans through contextual understanding, reasoning, and iterative refinement.**

Intelligence is NOT:
- Raw computation or data processing
- Pre-programmed responses or rule-matching
- Single-purpose task automation

Intelligence IS:
- **Interpretive:** Derives meaning from incomplete/ambiguous input
- **Transformative:** Converts intent into structured representation
- **Planning:** Generates actionable sequences from goals
- **Evaluative:** Assesses outcomes against intent
- **Refinable:** Improves through feedback and learning

### 2.2 Intelligence Components

| Component | Purpose | Nature |
|-----------|---------|--------|
| **Interpreter** | Parse and understand intent | Pattern recognition, context extraction |
| **Transformer** | Convert intent to structured meaning | Schema mapping, abstraction |
| **Planner** | Generate action sequences | Goal decomposition, dependency resolution |
| **Executor** | Invoke reusable skills | Skill dispatch, resource management |
| **Evaluator** | Assess outcome quality | Metrics, threshold checking, feedback |

### 2.3 Intelligence Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌────────────┐    ┌──────────────┐           │
│   │ INTERPRET│───▶│ TRANSFORM  │───▶│    PLAN      │           │
│   │  Intent  │    │  Meaning   │    │   Actions    │           │
│   └──────────┘    └────────────┘    └──────────────┘           │
│        │                                    │                   │
│        ▼                                    ▼                   │
│   ┌──────────┐                      ┌──────────────┐           │
│   │  CONTEXT │                      │   EXECUTE    │           │
│   │  Store   │◀─────────────────────│   Skills     │           │
│   └──────────┘                      └──────────────┘           │
│        │                                    │                   │
│        ▼                                    ▼                   │
│   ┌──────────────────────────────────────────────┐             │
│   │                EVALUATE                      │             │
│   │         Outcome vs Intent                    │             │
│   └──────────────────────────────────────────────┘             │
│                           │                                      │
│                           ▼                                      │
│                   ┌──────────────┐                               │
│                   │   REFINE     │                               │
│                   │   (if needed)│                               │
│                   └──────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Lifecycle of a Reasoning Task

### 3.1 Task Lifecycle Stages

A reasoning task progresses through these stages:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         TASK LIFECYCLE                                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────┐    ┌───────────┐    ┌───────────┐    ┌─────────┐        │
│  │  INPUT  │───▶│ INTERPRET │───▶│ TRANSFORM │───▶│  PLAN   │        │
│  │  Raw    │    │  Parse    │    │  Structure│    │  Decom- │        │
│  │  Input  │    │  Intent   │    │  Meaning  │    │  pose   │        │
│  └─────────┘    └───────────┘    └───────────┘    └─────────┘        │
│       │              │               │              │                 │
│       │              │               │              │                 │
│       │              │               │              ▼                 │
│       │              │               │        ┌─────────┐             │
│       │              │               │        │ VALIDATE│             │
│       │              │               │        │  Plan   │             │
│       │              │               │        └─────────┘             │
│       │              │               │              │                 │
│       │              │               │              ▼                 │
│       │              │               │        ┌─────────┐             │
│       │              │               │        │ APPROVE │             │
│       │              │               │        │  Plan   │             │
│       │              │               │        └─────────┘             │
│       │              │               │              │                 │
│       ▼              ▼               ▼              ▼                 │
│  ┌─────────────────────────────────────────────────────┐             │
│  │                   EXECUTE                           │             │
│  │         Dispatch Skills → Collect Results           │             │
│  └─────────────────────────────────────────────────────┘             │
│                              │                                        │
│                              ▼                                        │
│  ┌─────────────────────────────────────────────────────┐             │
│  │                   EVALUATE                          │             │
│  │            Compare Outcome vs Intent                │             │
│  └─────────────────────────────────────────────────────┘             │
│                              │                                        │
│                    ┌─────────┴─────────┐                             │
│                    │                   │                              │
│                    ▼                   ▼                              │
│             ┌──────────┐        ┌──────────┐                         │
│             │ SUCCESS  │        │ REFINE   │                         │
│             │ Complete │        │ Retry/   │                         │
│             │          │        │ Adjust   │                         │
│             └──────────┘        └──────────┘                         │
│                    │                   │                              │
│                    └─────────┬─────────┘                              │
│                              ▼                                        │
│                      ┌──────────────┐                                 │
│                      │  TERMINATE   │                                 │
│                      │  (Any State) │                                 │
│                      └──────────────┘                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Stage Definitions

#### Stage 1: INPUT
- **Purpose:** Receive raw user input
- **Actions:**
  - Capture raw text/query
  - Attach session context
  - Timestamp and tag for tracing
- **Outputs:** `RawInput` with metadata

#### Stage 2: INTERPRET
- **Purpose:** Parse user intent from raw input
- **Actions:**
  - Pattern matching against known intent types
  - Entity extraction (what, who, when, where)
  - Intent classification (what category of task)
- **Outputs:** `ParsedIntent` with confidence score

#### Stage 3: TRANSFORM
- **Purpose:** Convert parsed intent into structured meaning
- **Actions:**
  - Map to domain-agnostic semantic structure
  - Resolve ambiguity through context
  - Infer implicit parameters
- **Outputs:** `StructuredMeaning` (domain-agnostic)

#### Stage 4: PLAN
- **Purpose:** Generate actionable sequence from goal
- **Actions:**
  - Goal decomposition into sub-tasks
  - Dependency resolution (ordering)
  - Skill selection for each sub-task
  - Resource estimation
- **Outputs:** `ActionPlan` (sequence of skill invocations)

#### Stage 5: VALIDATE (Plan)
- **Purpose:** Verify plan soundness before execution
- **Actions:**
  - Check skill availability
  - Verify resource constraints
  - Detect circular dependencies
  - Assess risk factors
- **Outputs:** `ValidationResult` (pass/fail with reasons)

#### Stage 6: APPROVE (Plan)
- **Purpose:** Authorize plan execution
- **Actions:**
  - Human-in-loop approval (if required by policy)
  - Automated approval (default, trust threshold)
  - Permission verification
- **Outputs:** `ApprovedPlan`

#### Stage 7: EXECUTE
- **Purpose:** Dispatch skills and collect results
- **Actions:**
  - Skill dispatch (parallel where independent)
  - Result aggregation
  - Error handling and retry
  - Progress tracking
- **Outputs:** `ExecutionResult` with intermediate traces

#### Stage 8: EVALUATE
- **Purpose:** Assess outcome against original intent
- **Actions:**
  - Compare result to success criteria
  - Calculate quality metrics
  - Identify gaps or deviations
- **Outputs:** `EvaluationReport`

#### Stage 9: REFINE (Conditional)
- **Purpose:** Improve outcome if evaluation fails thresholds
- **Actions:**
  - Diagnose failure mode
  - Adjust plan or parameters
  - Retry with modifications
- **Outputs:** Refined plan or escalation

#### Stage 10: TERMINATE
- **Purpose:** End task, clean up resources
- **Actions:**
  - Finalize traces
  - Archive context
  - Release resources
  - Notify completion
- **Outputs:** `TaskCompletion` with final state

### 3.3 Task State Model

```python
class TaskState(Enum):
    PENDING      = "pending"       # Received, not yet processed
    INTERPRETED  = "interpreted"   # Intent parsed
    TRANSFORMED  = "transformed"   # Meaning structured
    PLANNED      = "planned"       # Action plan created
    VALIDATED    = "validated"     # Plan validated
    APPROVED     = "approved"      # Plan approved
    EXECUTING    = "executing"     # Skills dispatching
    EVALUATING   = "evaluating"    # Outcome assessment
    COMPLETED    = "completed"     # Success
    FAILED       = "failed"        # Terminal failure
    CANCELLED    = "cancelled"     # User/cancel requested
    REFINING     = "refining"      # Retrying with modifications
```

## 4. Boundaries Between Reasoning and Execution

### 4.1 The Reasoning Layer

**Purpose:** Understand, plan, and prepare — no side effects.

| Responsibility | Description |
|----------------|-------------|
| Intent parsing | Convert text to structured intent |
| Context building | Assemble relevant context |
| Planning | Generate action sequences |
| Validation | Verify plan soundness |
| Approval | Authorize execution |
| Abstraction | Hide implementation details |

**Guarantees:**
- No external system mutations
- Deterministic (same input → same reasoning)
- Time-bounded (configurable reasoning timeout)
- Observable (full trace of reasoning steps)

### 4.2 The Execution Layer

**Purpose:** Safely invoke skills and produce results — side effects allowed here.

| Responsibility | Description |
|----------------|-------------|
| Skill dispatch | Invoke reusable skills |
| Resource mgmt | Allocate/release resources |
| Error handling | Catch, classify, recover from errors |
| Result aggregation | Combine skill outputs |
| Progress tracking | Monitor execution state |

**Guarantees:**
- Side effects isolated and tracked
- Time-bounded (skill execution limits)
- Resource-capped (memory, CPU limits)
- Recoverable (checkpoint/restart where applicable)

### 4.3 Boundary Interface

```
┌─────────────────────────────────────────────────────────────────┐
│                      REASONING LAYER                            │
│                                                                 │
│   Input → Interpret → Transform → Plan → Validate → Approve     │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    OUTPUT: ActionPlan                   │   │
│   │   - Skill invocations with parameters                   │   │
│   │   - Dependencies and ordering                           │   │
│   │   - Success criteria                                    │   │
│   │   - Resource requirements                               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ [HARD BOUNDARY]                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    INPUT: ActionPlan                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                      EXECUTION LAYER                            │
│                                                                 │
│   Dispatch → Execute Skills → Aggregate → Evaluate → Report     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Crossing the Boundary

**From Reasoning to Execution:**
1. Reasoning produces `ActionPlan`
2. Boundary validation (plan format, skill availability)
3. Execution receives immutable plan copy
4. Execution begins (first skill invocation)

**From Execution to Reasoning:**
1. Execution produces `ExecutionResult`
2. Boundary validation (result format, completeness)
3. Reasoning receives result for evaluation
4. Reasoning may trigger REFINE (loop back)

**Boundary Rules:**
1. **Immutability:** Plans cannot change after crossing
2. **Idempotency:** Re-crossing produces same result
3. **Traceability:** Every crossing logged with trace ID
4. **Timeout:** Boundary crossing has max latency budget
5. **Atomicity:** Either full plan crosses or none

### 4.5 Separation Enforced By

| Mechanism | Reasoning | Execution |
|-----------|-----------|-----------|
| Code isolation | Separate module | Separate module |
| Type boundaries | `ActionPlan` (input) | `ExecutionResult` (output) |
| Runtime sandbox | No I/O, no syscalls | Controlled I/O |
| Permission model | Read-only context | Write-capable |
| Timeout policy | Reasoning budget | Skill budget |

## 5. Quality Criteria

### 5.1 Intelligence Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Intent recognition accuracy | >95% | Manual evaluation |
| Planning success rate | >90% | Plan validation pass rate |
| Execution success rate | >95% | Skills complete without fatal error |
| Refinement effectiveness | >80% | Refined plans succeed |
| Reasoning latency (p95) | <500ms | End-to-end reasoning time |

### 5.2 Safety Criteria

- No reasoning step performs external I/O
- All execution has timeout or resource cap
- Boundary crossing is always traceable
- Failed executions cannot corrupt state

## 6. Out of Scope

The following are intentionally excluded from this spec:

- **Specific skill implementations** — Defined elsewhere as reusable skills
- **LLM integration details** — Abstraction layer handles this
- **Domain-specific intent types** — Extensible registry
- **User interface concerns** — Presentation layer
- **Persistence implementation** — Storage abstraction

## 7. References

- **Constitution:** `.specify/memory/constitution.md`
- **Skills System:** `specs/reusable-skills-system/spec.md`
- **Context Model:** `specs/shared-context-model/spec.md`
- **Runtime Architecture:** `specs/004-core-runtime-architecture/spec.md`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
