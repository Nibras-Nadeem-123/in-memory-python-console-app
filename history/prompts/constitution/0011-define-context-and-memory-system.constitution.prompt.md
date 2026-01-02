---
id: "0011"
title: "Define Context and Memory System"
stage: "constitution"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "context-memory-system"
branch: "005-intelligence-system-impl"
user: "/sp.specify"
command: "n/a"
labels:
  - "context"
  - "memory"
  - "state"
  - "persistence"
links:
  spec: "specs/context-memory-system/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/context-memory-system/spec.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.specify
Define the context and memory system.

Context should:
- Track state, goals, and history
- Be serializable
- Support inspection and rollback

Define:
- Data structures
- Read/write rules
- Persistence boundaries

# Response

Created `specs/context-memory-system/spec.md` defining the complete context and memory system.

**Context Hierarchy (3 Levels):**

| Level | Scope | Lifetime | Contents |
|-------|-------|----------|----------|
| **Global** | Engine-wide | Engine start→shutdown | Config, registries, policies |
| **Session** | Per user | Session creation→end | User profile, history, variables |
| **Execution** | Per request | Request→completion | State, history, outputs, checkpoints |

**Core Data Structures:**
1. GlobalContext — Engine config, skill/agent registries
2. SessionContext — User profile, execution history
3. ExecutionContext — Goal, state, history, checkpoints
4. MutableState — Key-value store with versioning
5. HistoryLog — Append-only event log
6. Checkpoint — State snapshot for rollback

**Read/Write Rules:**
- Immutable: execution_id, session_id, goal, history.events
- Mutable: state, checkpoints, outputs, metadata
- State access validated (system keys protected)
- Full isolation enforced between contexts

**Serialization:**
- Formats: JSON, YAML, MessagePack
- Non-serializable types rejected (file handles, connections, etc.)
- Full round-trip with no data loss

**Inspection:**
- Full state dump, history summary, state diff
- Checkpoint retrieval, history search
- Debug view for human readability

**Rollback:**
- Create checkpoints at any state
- Rollback to event or checkpoint
- Rollback history preserved
- Atomic operation (full success or no changes)

**Persistence Boundaries:**
- Level 0: Ephemeral (in-memory, default)
- Level 1: Short-term (session duration)
- Level 2: Long-term (archive with retention)

**Performance Targets:**
- State read/write: <1ms
- Checkpoint: <5ms
- Rollback: <10ms
- Serialize/deserialize: <50ms
