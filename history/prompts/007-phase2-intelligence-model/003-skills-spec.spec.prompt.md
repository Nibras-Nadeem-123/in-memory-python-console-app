---
id: 004
title: Phase 2 Reusable Skills Specification
stage: spec
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-phase2-intelligence-model
branch: main
user: DELL
command: /sp.specify
labels: ["spec","skills","phase2","reusable","stateless"]
links:
  spec: specs/007-phase2-intelligence-model/skills-spec.md
  ticket: null
  adr: history/adr/004-phase2-intelligence-integration.adr.md
  pr: null
files:
 - specs/007-phase2-intelligence-model/skills-spec.md
tests:
 - none
---

## Prompt

/sp.specify
Define reusable skills for Phase 2.

Skills must be:
- Stateless
- Domain-agnostic
- Reusable across agents

Required skills:
- Intent analysis
- Ambiguity detection
- Task decomposition
- Plan validation
- Result evaluation

Define:
- Purpose
- Inputs
- Outputs
- Failure modes

## Response snapshot

Created comprehensive reusable skills specification for Phase 2 intelligence system (spec: 007-phase2-intelligence-model/skills-spec.md)

**Five Skills Fully Specified:**

### 1. IntentAnalysisSkill

**Purpose:** Deep semantic analysis of user input to extract structured understanding beyond simple keyword matching.

**Inputs:**
- Required: `user_input` (str), `conversation_history` (List[Message])
- Optional: `domain_context` (Dict), `existing_state` (Dict)

**Outputs:**
- `IntentAnalysisResult` with intent_type, confidence, entities (tasks, priorities, timeframes), explicit/implicit requirements, completeness_score, missing_information, constraints

**Failure Modes:**
- Uninterpretable input (confidence < 0.3) → Return with rephrasing request
- Empty input → SkillValidationError
- Timeout (>30s) → SkillTimeoutError
- No entities found → Success with warnings
- Conflicting entities → Return conflict list

### 2. AmbiguityDetectionSkill

**Purpose:** Identifies phrases with multiple valid interpretations or unclear constructs requiring human clarification.

**Inputs:**
- Required: `text` (str)
- Optional: `conversation_history` (List[Message]), `domain_context` (Dict)

**Outputs:**
- `AmbiguityReport` with has_ambiguity flag, ambiguity_score (0.0-1.0), clarity_level (CLEAR/MODERATE/UNCLEAR), list of ambiguities with severity/context/suggestions, clarification_questions, required_clarifications count

**Failure Modes:**
- Empty text → SkillValidationError
- Timeout (>15s) → SkillTimeoutError with partial results
- No recognizable language → Success with "needs review" warning
- Excessive ambiguity (score > 0.8) → Flag as "too unclear - please rephrase"

### 3. TaskDecompositionSkill

**Purpose:** Breaks down high-level goals into actionable, ordered steps with dependencies and concrete command mappings.

**Inputs:**
- Required: `requirements` (List[str]), `target_operations` (List[str] - Phase 1 commands)
- Optional: `existing_tasks` (List[Task]), `complexity_level` (str), `max_depth` (int)

**Outputs:**
- `DecompositionResult` with ordered PlanStep list, dependency graph, circular dependency flag, critical path, estimated duration, confidence score, requirement-to-steps mapping

**Failure Modes:**
- Unmappable requirement (no valid Phase 1 command) → Flag as "not implementable"
- Circular dependencies → Alert and request resolution
- Excessive depth (> max_depth) → SkillExecutionError
- No valid steps → SkillExecutionError
- Timeout (>60s) → SkillTimeoutError with partial result

### 4. PlanValidationSkill

**Purpose:** Verifies execution plan is sound, complete, and executable before proceeding to prevent execution failures.

**Inputs:**
- Required: `plan` (ExecutionPlan), `phase1_schema` (Dict)
- Optional: `current_state` (Dict), `validation_rules` (List[Rule])

**Outputs:**
- `ValidationReport` with status (PASS/WARN/FAIL), quality score, executable flag, list of validation checks (passed/failed/warning counts), issues (critical/warnings), risk level, rollback strategies, recommendations

**Failure Modes:**
- Invalid plan structure → SkillValidationError with details
- Cannot validate commands (schema unavailable) → Success with "manual verification needed" warning
- Too many issues (>50) → FAIL status with summary
- Circular dependencies → Success with critical issues flag
- Timeout (>30s) → SkillTimeoutError with partial validation

### 5. ResultEvaluationSkill

**Purpose:** Assesses execution results against original intent and specification to determine success, quality, and next actions.

**Inputs:**
- Required: `execution_result` (ExecutionResult)
- Optional: `original_intent` (Intent), `specification` (Specification), `plan` (ExecutionPlan), `acceptance_criteria` (List[str])

**Outputs:**
- `EvaluationResult` with success flag, quality score/level, completion metrics (steps, rate, time), error analysis (total, fatal, recoverable, by category), intent alignment (satisfied, score, unfulfilled requirements), acceptance criteria met/failed/rate, recommended action (PROCEED/RETRY/FALLBACK), retry probability and suggestions, human-readable report and summary

**Failure Modes:**
- Missing execution result → SkillValidationError
- Invalid result structure → SkillExecutionError (FAILED status)
- Cannot evaluate (missing intent/spec) → Success with "manual review needed" warning
- Timeout (>30s) → SkillTimeoutError with partial evaluation

**Skill Properties Enforced:**

1. **Statelessness**: No instance variables storing state - all state via context/kwargs
2. **Domain-Agnosticism**: No hardcoded domain rules - use domain_context parameter
3. **Reusability**: Clear single responsibility, output compatible with other skills
4. **Composability**: Skills can be chained (IntentAnalysis → AmbiguityDetection → Decomposition)

**Skill Composition Examples:**
- Intent clarification pipeline (IntentAnalysis → AmbiguityDetection with re-analysis)
- Plan generation pipeline (Decomposition → Validation with handling results)
- Execution evaluation pipeline (Execute → ResultEvaluation with action determination)

**Testing Requirements:**
- Unit tests for each skill (input validation, output structure, failure modes)
- Integration tests for skill composition in agent workflows
- Example test structure provided for all skills

## Outcome

- ✅ Impact: Comprehensive skills specification defines stateless, domain-agnostic, reusable building blocks for Phase 2 intelligence
- 🧪 Tests: none (spec-only artifact)
- 📁 Files: 1 new spec file (007-phase2-intelligence-model/skills-spec.md)
- 🔁 Next prompts: Implementation tasks, skill development plan, testing strategy
- 🧠 Reflection: All five skills fully specified with clear I/O contracts, failure modes, and composition patterns. Specification enforces skill properties (stateless, domain-agnostic, reusable) with examples and testing requirements.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
