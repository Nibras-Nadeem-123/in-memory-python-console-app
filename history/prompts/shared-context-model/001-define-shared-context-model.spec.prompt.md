---
id: '001'
title: 'define-shared-context-model'
stage: 'spec'
date: '2025-12-28'
surface: 'agent'
model: 'claude-sonnet-4-5-20250929'
feature: 'shared-context-model'
branch: 'main'
user: 'Claude Code User'
command: '/sp.specify'
labels: ['context-model,conversation-state,goals,constraints,artifacts,execution-history,serialization']
links:
  spec: 'null'
  ticket: 'null'
  adr: 'null'
  pr: 'null'
files:
  - 'specs/shared-context-model/spec.md'
tests:
  - 'none'
---

## Prompt

/sp.specify
Define a shared Context model.

Context must:
- Store conversation state
- Track goals and constraints
- Hold intermediate artifacts
- Store execution history
- Be serializable and restorable

Define:
- Context schema
- Read/write rules
- Mutability rules
- Access patterns for agents

## Response snapshot

Created `specs/shared-context-model/spec.md` with complete Shared Context Model:

**Core Schema**:
- `ContextState`: Root container with conversation, goals, artifacts, execution, custom
- `Goal`: Tracks objectives with status, priority, dependencies, constraints
- `Constraint`: Validates inputs (MAX_TOKENS, MAX_TIME, REQUIRED_FIELDS, PATTERN_MATCH, VALUE_RANGE, MUTEX)
- `Artifact`: Versioned intermediate outputs with parent/child derivation
- `ExecutionStep`: Step-level history with status, timing, error details
- `ConversationTurn`: Individual conversation entries with intent/entity extraction

**Access Control**:
- Scope-based visibility: GLOBAL (engine), SESSION (session), TASK (task)
- Permission levels: READ, WRITE, DELETE, ADMIN
- Role-based rules: all agents read conversation/goals; creators own artifacts/custom
- Access matrix for all data categories

**Mutability Rules**:
- Immutable: execution history, artifact versions, goal definitions, conversation turns
- Mutable: goal status, artifact new versions, conversation state, custom data
- Atomic operations: CompareAndSwap, IncrementCounter
- Conflict resolution: LWW, CAS, or merge

**Access Patterns**:
- Standard pattern: read → validate → execute → record → snapshot
- Goal-oriented pattern: claim → validate → complete with result
- Conversation pattern: get summary → extend → record intent

**Serialization**:
- JSON schema with full type definitions
- Snapshot/restore for persistence
- 5ms read, 10ms write performance targets

## Outcome

- ✅ Impact: Defined comprehensive shared context model with conversation state, goals/constraints, artifacts, execution history, and serialization
- 📁 Files: 1 created (specs/shared-context-model/spec.md)
- 🔁 Next prompts: Run `/sp.plan` to design context implementation, `/sp.tasks` for implementation tasks
- 🧠 Reflection: Context model provides the stateful backbone for the frozen intelligence layer; agents can now share state through structured access patterns

## Evaluation notes (flywheel)

- Failure modes observed: 'none'
- Graders run and results (PASS/FAIL): 'N/A'
- Prompt variant (if applicable): 'N/A'
- Next experiment (smallest change to try): 'N/A'
