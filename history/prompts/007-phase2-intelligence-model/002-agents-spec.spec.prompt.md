---
id: 003
title: Phase 2 Agents Specification
stage: spec
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-phase2-intelligence-model
branch: main
user: DELL
command: /sp.specify
labels: ["spec","agents","phase2","intelligence"]
links:
  spec: specs/007-phase2-intelligence-model/agents-spec.md
  ticket: null
  adr: history/adr/004-phase2-intelligence-integration.adr.md
  pr: null
files:
 - specs/007-phase2-intelligence-model/agents-spec.md
tests:
 - none
---

## Prompt

/sp.specify
Define agents introduced in Phase 2.

Agents:
- ClarifierAgent
- PlannerAgent
- ExecutorAgent
- ReviewerAgent

For each agent define:
- Responsibility
- Inputs
- Outputs
- When it is invoked
- How it interacts with context

## Response snapshot

Created comprehensive agent specification for Phase 2 intelligence system (spec: 007-phase2-intelligence-model/agents-spec.md)

**Four Agents Fully Specified:**

### 1. ClarifierAgent (Stage 1: Intent Parsing & Clarification)

**Responsibility:** Transforms raw natural language into structured, clarified Intent object through parsing, ambiguity detection, and clarification dialog.

**When Invoked:**
- Initial user input received
- Ambiguous intent detected
- User provides clarification
- Conversation continues (multi-turn dialog)
- Fallback from other agents

**Inputs:** Raw user input, conversation history, context (intent, clarifications)

**Outputs:** Intent object (type, description, parameters, ambiguities, clarifications, confidence, completeness), ClarificationRequest objects

**Context Interaction:**
- Reads: context.intent, context.clarifications, context.workflow_state
- Updates: context.intent, context.clarifications, workflow_state (initialized → clarifying → resolved)
- Logs all updates to context.reasoning_trace

### 2. PlannerAgent (Stage 2 & 3: Specification & Planning)

**Responsibility:** Transforms clarified intent into validated execution plan through specification generation, task decomposition, dependency resolution, and plan validation.

**When Invoked:**
- Intent is resolved (workflow_state == "intent_resolved")
- User requests replanning
- User modifies specification
- Plan validation fails
- Previous plan rejected

**Inputs:** Clarified intent, context (clarifications, existing spec/plan), Phase 1 capabilities

**Outputs:** Specification object (title, requirements, acceptance criteria), ExecutionPlan object (steps, dependencies, priorities), ValidationReport

**Context Interaction:**
- Reads: context.intent, context.clarifications, context.specification, context.plan
- Updates: context.specification, context.plan, workflow_state (intent_resolved → spec_generation → plan_generation → validation → plan_ready)
- Stores both spec and plan as artifacts
- Logs all decisions to context.reasoning_trace

### 3. ReviewerAgent (Stage 4: Plan Review & Approval)

**Responsibility:** Facilitates user review and approval through presenting artifacts, collecting feedback, validating modifications, and managing approval checkpoints.

**When Invoked:**
- Plan is ready (workflow_state == "plan_ready")
- User requests review
- User submits modifications
- User rejects plan
- After spec generation (first review point)

**Inputs:** Specification, ExecutionPlan, context (specification, plan, conversation history)

**Outputs:** ReviewResult (APPROVED, MODIFIED, REJECTED, REJECTED_WITH_FEEDBACK), modified artifacts, user feedback

**Context Interaction:**
- Reads: context.specification, context.plan, conversation_history, review_history
- Updates: context.specification, context.plan (if modified), workflow_state (plan_ready → reviewing_spec → reviewing_plan → awaiting_approval → plan_approved)
- Ensures explicit approval before execution
- Logs all modifications to context.reasoning_trace

### 4. ExecutorAgent (Stage 5: Plan Execution)

**Responsibility:** Executes approved plans using Phase 1 capabilities through step orchestration, command dispatch, progress tracking, error handling, and result aggregation.

**When Invoked:**
- Plan is approved (workflow_state == "plan_approved")
- User requests plan execution (manual trigger)
- Partial execution resume (after interruption)
- Retry after error

**Inputs:** Approved ExecutionPlan, Phase1Executor (existing Phase 1), context (plan, previous results)

**Outputs:** ExecutionResult (COMPLETED, PARTIAL, FAILED, CANCELLED), step results, error reports, final state changes, rollback status

**Context Interaction:**
- Reads: context.plan, context.execution_results, Phase1Executor
- Updates: context.execution_results, workflow_state (plan_approved → executing → completed/failed), task state via Phase1
- Stores ExecutionResult as artifact
- Logs every step execution to context.reasoning_trace

**Key Data Models Defined:**
- Intent (type, description, parameters, ambiguities, clarifications, confidence, completeness)
- ClarificationRequest (question_id, question, field, options, response, timestamp)
- Specification (title, description, requirements, acceptance_criteria, constraints, assumptions)
- ExecutionPlan (title, steps, estimated_duration, validation_status)
- PlanStep (id, description, command, dependencies, priority, estimated_seconds, status)
- ReviewResult (status, specification, plan, user_feedback, modifications, validation_result)
- ExecutionResult (status, steps_completed/total, timing, errors, rollback, step_results, state changes)
- StepResult (step_id, status, command, output, error, duration)
- ExecutionError (error_id, step_id, error_type, error_message, fatal, recoverable, timestamp)

**Agent Interaction Flow Documented:**
Complete flow from user input → Clarifier → Planner → Reviewer → Executor → results, with all state transitions and decision points clearly defined.

**Error Handling for Each Agent:**
- Clarifier: Low confidence → rephrase; ambiguity timeout → defaults/Phase1 fallback
- Planner: Invalid spec → more clarification; validation fails → replan
- Reviewer: Invalid modifications → reject; rejection without feedback → ask clarification
- Executor: Non-fatal failure → continue; fatal failure → stop; all failed → rollback

## Outcome

- ✅ Impact: Comprehensive agent specification defines complete Phase 2 intelligence pipeline
- 🧪 Tests: none (spec-only artifact)
- 📁 Files: 1 new spec file (007-phase2-intelligence-model/agents-spec.md)
- 🔁 Next prompts: Skill specifications, implementation planning, task breakdown
- 🧠 Reflection: All four agents fully specified with clear responsibilities, I/O contracts, invocation conditions, and context interaction patterns. Specification provides complete blueprint for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
