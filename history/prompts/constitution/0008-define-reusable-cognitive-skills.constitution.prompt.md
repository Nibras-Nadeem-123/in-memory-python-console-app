---
id: "0008"
title: "Define Reusable Cognitive Skills"
stage: "constitution"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "reusable-cognitive-skills"
branch: "005-intelligence-system-impl"
user: "/sp.specify"
command: "n/a"
labels:
  - "skills"
  - "cognitive"
  - "reusability"
  - "architecture"
links:
  spec: "specs/reusable-cognitive-skills/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/reusable-cognitive-skills/spec.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.specify
Define reusable cognitive skills.

Skills should be:
- Stateless
- Domain-agnostic
- Composable

Required skills:
- Intent Parsing
- Specification Generation
- Task Decomposition
- Constraint Validation
- Execution Planning
- Result Evaluation

For each skill, define:
- Purpose
- Inputs
- Outputs
- Failure modes

# Response

Created `specs/reusable-cognitive-skills/spec.md` defining six core cognitive skills.

**Skill Design Principles:**
- Stateless: No internal state between invocations
- Domain-agnostic: No hardcoded business logic
- Composable: Output is valid input to other skills
- Contract: Idempotent, deterministic, pure (no side effects)

**Defined Skills:**

| Skill | ID | Purpose |
|-------|-----|---------|
| Intent Parsing | `cognitive.intent.parse` | Extract structured intent from raw input |
| Specification Generation | `cognitive.spec.generate` | Transform intent into formal spec |
| Task Decomposition | `cognitive.task.decompose` | Break goals into hierarchical tasks |
| Constraint Validation | `cognitive.constraint.validate` | Validate plan against constraints |
| Execution Planning | `cognitive.plan.generate` | Generate skill invocation sequence |
| Result Evaluation | `cognitive.result.evaluate` | Compare results against intent |

**Each skill defines:**
- Purpose (what it does)
- Inputs (with schema)
- Outputs (with schema)
- Failure modes (classification + handling)

**Composition Patterns:**
- Linear pipeline (sequential chain)
- Parallel execution (independent validators)
- Conditional branching (clarification)
- Iteration (refinement loop)

**Performance Targets:**
- Latency p95: 100-300ms per skill
- Memory: 10-30MB per skill
- Accuracy: 90-95% targets
