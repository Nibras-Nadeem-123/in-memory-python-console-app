---
id: '001'
title: 'define-core-intelligence-engine'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'core-intelligence-engine'
branch: 'feat/core-intelligence-engine'
user: 'Claude Code User'
command: '/sp.specify'
labels: 'core-engine,orchestration,intelligence-layer,routing,context,memory'
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/core-intelligence-engine/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define the Core Intelligence Engine.

Purpose:
- Orchestrate skills, agents, and templates.
- Serve as the central reasoning controller.

Responsibilities:
- Accept user intent.
- Route intent to appropriate sub-agents.
- Maintain shared context and memory.
- Enforce execution order and constraints.
- Produce structured outputs.

Constraints:
- No domain-specific logic.
- Must be reusable across all projects.
- Must be deterministic and inspectable.

Output:
- Definition of the Core Engine interface.
- Inputs, outputs, and lifecycle.

## Response snapshot

Created `specs/core-intelligence-engine/spec.md` with:

1. **Core Engine Architecture**:
   - Intent Router - Routes intents to appropriate components
   - Context Manager - Maintains shared execution context
   - Memory Store - Persistent storage for learned information
   - Constraint Enforcer - Validates and enforces constraints
   - Execution Trace - Complete record for inspection
   - Component Registry - Discovers and manages components

2. **Key Interfaces**:
   - `CoreEngine` - Main orchestration controller
   - `EngineConfig` - Configuration with routing, memory, constraint settings
   - `EngineInput`/`EngineOutput` - Structured I/O
   - `ComponentRegistry` - Discovery and lifecycle management
   - `IntentRouter` - Multiple routing strategies (capability, priority, adaptive)
   - `ContextManager` - Session/user/global scope with TTL
   - `MemoryStore` - Persistent learned information
   - `ConstraintEnforcer` - Time, order, mutex, capacity constraints
   - `ExecutionTrace` - Full execution audit trail

3. **Core Engine Features**:
   - Deterministic execution with seedable RNG
   - Lifecycle management (CREATED → IDLE → RUNNING → BUSY → SHUTDOWN)
   - Hot-reload of components
   - Complete audit trail
   - Graceful and forced shutdown
   - Constraint validation before/during execution

## Outcome

- ✅ Impact: Defined central orchestration engine for skills, agents, and templates
- 📁 Files: 1 created (specs/core-intelligence-engine/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design engine implementation architecture
- 🧠 Reflection: Engine provides single entry point; deterministic routing enables reproducibility; trace enables debugging

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'
