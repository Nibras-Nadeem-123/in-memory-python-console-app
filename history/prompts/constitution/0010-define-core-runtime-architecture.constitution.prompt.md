---
id: "0010"
title: "Define Core Runtime Architecture"
stage: "constitution"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "core-runtime-architecture"
branch: "005-intelligence-system-impl"
user: "/sp.specify"
command: "n/a"
labels:
  - "runtime"
  - "architecture"
  - "engine"
  - "lifecycle"
links:
  spec: "specs/core-runtime-architecture/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/core-runtime-architecture/spec.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.specify
Define the core runtime architecture.

Include:
- Engine lifecycle
- Context management
- Agent routing
- Skill invocation
- Error handling
- Logging and introspection

Output should describe the full runtime flow.

# Response

Created `specs/core-runtime-architecture/spec.md` defining the complete runtime architecture.

**Core Components:**
1. Engine Core — Lifecycle management (start/shutdown)
2. Context Manager — Session/execution context hierarchy
3. Agent Router — Task-to-agent routing with scoring
4. Agent Dispatcher — Agent invocation management
5. Skill Executor — Safe skill execution with sandbox
6. Skill Registry — Skill discovery and loading
7. Error Handler — Error classification and recovery
8. Introspection — Logging, metrics, tracing

**Engine Lifecycle:**
- States: CREATED → INITIALIZED → RUNNING → IDLE/EXECUTING/PAUSED → SHUTDOWN
- Methods: start(), shutdown(), submit()
- Health monitoring with configurable checks

**Context Hierarchy:**
- GlobalContext — Engine-wide shared state
- SessionContext — Per-user session data
- ExecutionContext — Per-request isolated state
- Guarantees: Session isolation, execution isolation, clean lifecycle

**Agent Routing:**
- Selection: capability match → availability → performance history → session affinity
- Routing table maps task types to default/fallback agents

**Skill Invocation:**
- Flow: Validate → Prepare Sandbox → Execute (with monitoring) → Validate Output
- Safety: timeout enforcement, memory limits, import filtering, resource caps
- Retry policy with exponential backoff

**Error Handling:**
- Taxonomy: FATAL (halt), RETRYABLE (retry), WARN (log and continue)
- 18 error types classified
- Recovery actions per error type

**Full Runtime Flow:**
1. Request Receipt → 2. Reasoning (no side effects) → 3. Execution (side effects) → 4. Evaluation → 5. Completion

**Performance Targets:**
- Request to first skill: <100ms
- Agent routing: <10ms
- Concurrent executions: 100+
- Success rate: >99%
