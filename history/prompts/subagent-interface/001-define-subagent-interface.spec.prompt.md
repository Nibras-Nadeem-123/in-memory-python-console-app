---
id: '001'
title: 'define-subagent-interface'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'subagent-interface'
branch: 'main'
user: 'Claude Code User'
command: '/sp.specify'
labels: ['subagent,interface,agent-contract,error-handling,lifecycle,skills,capabilities']
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/subagent-interface/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define a standard SubAgent interface.

Each sub-agent must define:
- name
- responsibility
- accepted inputs
- produced outputs
- required skills
- error handling strategy

Agents must be callable by the engine and return structured results.

## Response snapshot

Created `specs/subagent-interface/spec.md` with complete SubAgent Interface:

**Core Interface (`SubAgent` abstract base class)**:
- `metadata`: AgentMetadata with name, responsibility, capabilities, schemas
- `execute(input)`: Primary execution method returning AgentResult
- `validate_input/output`: Schema validation hooks
- `can_handle`: Confidence-based task routing
- `get_capabilities`: List of AgentCapability enums

**Input/Output Contracts**:
- `AgentInput`: task_type, payload, session_id, context, options
- `AgentOutput`: task_type, payload, confidence, artifacts, metrics
- `AgentResult`: Structured result with status, error, duration, artifacts

**Error Handling**:
- 5 strategies: RETRY, FALLBACK, SKIP, ESCALATE, ERROR
- `ErrorResponse` with error_code, category, message, recovery_action
- `ErrorHandler` with exponential backoff and retry logic

**Lifecycle**:
- States: CREATED → INITIALIZING → READY → RUNNING → SHUTDOWN → ERROR
- Hooks: on_start, on_progress, on_complete, on_error, cleanup

**Skills & Dependencies**:
- `SkillDependency` with name, version, required flag, injection_method
- Registry validation before execution

**Engine Integration**:
- `AgentEngine` interface: register, invoke, parallel execution, shutdown
- Agent invocation flow: route → validate → initialize → execute → validate → aggregate

**Complete Example**: `ArchitectAgent` with full implementation demonstrating all interfaces.

## Outcome

- ✅ Impact: Defined standardized SubAgent interface with identity, contracts, error handling, lifecycle, and engine integration
- 📁 Files: 1 created (specs/subagent-interface/spec.md)
- 🔁 Next prompts: Run `/sp.plan` for agent implementation patterns, `/sp.tasks` for implementation
- 🧠 Reflection: Standard interface enables pluggable agents; error strategies provide predictable failure modes; skill dependencies enable dynamic composition

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'
