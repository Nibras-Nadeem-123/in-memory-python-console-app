---
id: "0007"
title: "Define Core Intelligence Model"
stage: "constitution"
date: "2025-12-29"
model: "sonnet-4-5-20250929"
feature: "core-intelligence-model"
branch: "005-intelligence-system-impl"
user: "/sp.specify"
command: "n/a"
labels:
  - "intelligence-model"
  - "reasoning"
  - "lifecycle"
  - "architecture"
links:
  spec: "specs/core-intelligence-model/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "specs/core-intelligence-model/spec.md"
tests:
  - "none"
outcome: "completed"
evaluation: "n/a"
---

# Prompt

/sp.specify
Define the core intelligence model.

The system must:
- Interpret intent.
- Transform intent into structured meaning.
- Plan actions.
- Execute actions through reusable skills.
- Evaluate and refine outcomes.

Define:
- What "intelligence" means in this system.
- The lifecycle of a reasoning task.
- Boundaries between reasoning and execution.

# Response

Created `specs/core-intelligence-model/spec.md` defining the core intelligence model with:

**What is Intelligence:**
- Adaptive capability to transform ambiguous intent into structured, executable plans
- NOT raw computation or pre-programmed responses
- IS interpretive, transformative, planning, evaluative, refinable
- Five components: Interpreter, Transformer, Planner, Executor, Evaluator

**Task Lifecycle (10 stages):**
1. INPUT → 2. INTERPRET → 3. TRANSFORM → 4. PLAN → 5. VALIDATE → 6. APPROVE → 7. EXECUTE → 8. EVALUATE → 9. REFINE (conditional) → 10. TERMINATE

**Reasoning/Execution Boundaries:**
- Reasoning: Understand, plan, prepare — no side effects
- Execution: Safely invoke skills — side effects allowed here
- Hard boundary at `ActionPlan` crossing
- Enforced by: code isolation, type boundaries, runtime sandbox, permission model, timeouts

**Quality Targets:**
- Intent recognition >95%
- Planning success >90%
- Execution success >95%
- Reasoning latency (p95) <500ms
