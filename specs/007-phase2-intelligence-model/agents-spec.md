# Agent Specification: Phase 2 Intelligence Agents

**Feature Branch**: `007-phase2-intelligence-model`
**Created**: 2026-01-06
**Status**: Draft
**Related Spec**: `007-phase2-intelligence-model/spec.md`
**Related ADR**: `history/adr/004-phase2-intelligence-integration.adr.md`

## Overview

This specification defines the four intelligence agents introduced in Phase 2 of the Spec-Driven Todo Console Application. These agents orchestrate the reasoning pipeline that transforms high-level user intent into executed multi-step plans using Phase 1 capabilities.

**Agent Hierarchy:**

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  ClarifierAgent (Stage 1)                         │
│  Parse intent → Detect ambiguity → Clarify with user  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  PlannerAgent (Stage 2 & 3)                     │
│  Generate spec → Create plan → Validate             │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  ReviewerAgent (Stage 4)                          │
│  Review artifacts → Request approval → Update         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  ExecutorAgent (Stage 5)                          │
│  Execute plan → Track results → Report               │
└─────────────────────────────────────────────────────────┘
```

---

## ClarifierAgent

### Responsibility

ClarifierAgent is responsible for **Stage 1: Intent Parsing & Clarification**. It transforms raw natural language input into a structured, clarified Intent object by:

- Parsing natural language to classify intent type
- Extracting entities (tasks, priorities, timeframes, constraints)
- Detecting ambiguities in user understanding
- Generating clarifying questions when ambiguity is detected
- Engaging in clarification dialog with the user
- Collecting and integrating user clarifications
- Validating that intent is sufficiently clear for planning

**Key Insight**: ClarifierAgent is the only agent that directly interacts with users through the CLI. It owns the clarification conversation and must manage dialog state.

### When It Is Invoked

ClarifierAgent is invoked when:

1. **Initial user input received** - First entry point into Phase 2
2. **Ambiguous intent detected** - When previous parsing was unclear
3. **User provides clarification** - After clarifying question asked
4. **Conversation continues** - Multi-turn clarification dialog
5. **Fallback from other agents** - When higher stages cannot proceed

**Invocation Conditions:**
```python
def should_invoke(context: Phase2Context) -> bool:
    # Entry point - no intent parsed yet
    if context.intent is None:
        return True

    # Clarification in progress
    if context.workflow_state == "needs_clarification":
        return True

    # Intent has unresolved ambiguities
    if context.intent and context.intent.ambiguities:
        return True

    # User just provided clarification
    if context.last_event_type == "clarification_response":
        return True

    return False
```

**Workflow State Transitions:**
- `initialized` → `clarifying` (when parsing starts)
- `clarifying` → `needs_clarification` (when ambiguity detected)
- `needs_clarification` → `clarifying` (when user responds)
- `clarifying` → `intent_resolved` (when clear enough)

### Inputs

**Primary Inputs:**
- `user_input: str` - Raw natural language from CLI
- `conversation_history: List[Message]` - Previous messages in this session
- `current_context: Phase2Context` - Existing reasoning state

**Secondary Inputs (Context Fields):**
- `context.user_input` - Original raw input
- `context.intent` - Previously parsed intent (if any)
- `context.clarifications` - List of existing clarification requests
- `conversation_history` - Full message history for context

**External Dependencies:**
- `AmbiguityDetectionSkill` - Detect unclear aspects
- `IntentClassificationSkill` - Classify intent type
- `EntityExtractionSkill` - Extract tasks, priorities, etc.
- `QuestionGenerationSkill` - Generate clarifying questions

### Outputs

**Primary Outputs:**
- `intent: Intent` - Structured, clarified intent object
- `clarifications: List[ClarificationRequest]` - Questions asked and responses
- `conversation_state: ConversationState` - Current dialog state

**Intent Object Structure:**
```python
@dataclass
class Intent:
    # Core classification
    type: IntentType  # ORGANIZE, PRIORITIZE, PLAN, QUERY

    # Natural language representation
    description: str  # Original or refined user intent

    # Parsed entities
    parameters: Dict[str, Any]  # Extracted parameters:
                                  # - tasks: List[str] - Task descriptions
                                  # - priorities: List[str] - Priority levels
                                  # - timeframes: List[str] - "today", "this week", etc.
                                  # - constraints: List[str] - Restrictions/requirements

    # Ambiguity tracking
    ambiguities: List[Ambiguity]  # Detected ambiguities requiring clarification
    clarifications: Dict[str, str]  # Resolved ambiguities (field -> value)

    # Quality metrics
    confidence: float  # 0.0 - 1.0 - parsing confidence
    completeness: float  # 0.0 - 1.0 - information completeness

    # Metadata
    metadata: Dict[str, Any]  # Additional metadata (model, timestamp, tokens)
```

**ClarificationRequest Object:**
```python
@dataclass
class ClarificationRequest:
    question_id: str  # Unique identifier
    question: str  # Natural language question to user
    field: str  # Which intent field needs clarification
    options: Optional[List[str]]  # Suggested answers (optional)
    response: Optional[str]  # User's answer (once provided)
    timestamp: str  # When question was asked
```

**Output Types:**

1. **Clarified Intent** (`completeness > 0.8`):
   - Intent is clear enough for planning
   - Proceed to PlannerAgent

2. **Needs Clarification** (`completeness <= 0.8`):
   - Generate clarifying questions
   - Wait for user response
   - Re-invoke with user response

3. **Uninterpretable** (`confidence < 0.3`):
   - Cannot understand intent
   - Request rephrasing or fallback to Phase 1

4. **Contradictory** (`has_conflicting_clarifications`):
   - User provided contradictory answers
   - Flag for resolution or fallback

### How It Interacts with Context

**Context Reads:**
```python
# Read existing state
intent = context.intent  # Check for existing parsed intent
clarifications = context.clarifications  # Previous clarifications
user_input = context.user_input  # Original input
conversation_history = context.conversation_history  # Dialog history

# Check workflow state
workflow_state = context.workflow_state
if workflow_state == "initialized":
    # First-time parsing
elif workflow_state == "needs_clarification":
    # Resuming clarification dialog
elif workflow_state == "clarifying":
    # In progress - collect response
```

**Context Updates:**
```python
# Update with parsed intent
context.intent = parsed_intent
context.add_artifact("intent", parsed_intent, {
    "source": "clarifier_agent",
    "model": "claude-sonnet-4.5",
    "timestamp": datetime.now().isoformat()
})

# Update clarification history
for clarification in generated_questions:
    context.clarifications.append(clarification)
    context._log_event("clarification_asked", {
        "question_id": clarification.question_id,
        "field": clarification.field
    })

# Process user response to clarification
if user_response:
    for clarification in context.clarifications:
        if clarification.question_id == responding_to:
            clarification.response = user_response
            context._log_event("clarification_resolved", {
                "question_id": clarification.question_id,
                "response": user_response
            })

# Transition workflow state
if parsed_intent.completeness > 0.8:
    context.transition_to("intent_resolved")
else:
    context.transition_to("needs_clarification")

# Update reasoning trace
context.reasoning_trace.append({
    "stage": "clarifier",
    "action": "intent_parsed",
    "intent_type": parsed_intent.type.value,
    "confidence": parsed_intent.confidence,
    "completeness": parsed_intent.completeness,
    "ambiguities_count": len(parsed_intent.ambiguities),
    "timestamp": datetime.now().isoformat()
})
```

**Context Invariants:**
- `context.intent` is only updated when `confidence > 0.3`
- `context.clarifications` grows monotonically (never removed)
- `context.workflow_state` always transitions forward (initialized → clarifying → resolved)
- All updates are logged to `context.reasoning_trace`

---

## PlannerAgent

### Responsibility

PlannerAgent is responsible for **Stage 2 & 3: Specification Generation & Planning**. It transforms a clarified intent into a validated execution plan by:

- Generating formal specification from intent
- Extracting requirements and acceptance criteria
- Decomposing specification into actionable steps
- Identifying dependencies between steps
- Mapping abstract steps to Phase 1 commands
- Assigning priorities and effort estimates
- Validating plan feasibility

**Key Insight**: PlannerAgent bridges the gap between high-level intent and concrete execution. It must understand both the user's intent AND Phase 1's capabilities.

### When It Is Invoked

PlannerAgent is invoked when:

1. **Intent is resolved** (`context.workflow_state == "intent_resolved"`)
2. **User requests replanning** (after reviewing plan)
3. **User modifies specification** (after spec review)
4. **Plan validation fails** (needs regeneration)
5. **Previous plan rejected** by ReviewerAgent

**Invocation Conditions:**
```python
def should_invoke(context: Phase2Context) -> bool:
    # Ready for planning - intent resolved
    if context.workflow_state == "intent_resolved":
        return True

    # User requested replanning
    if context.last_event_type == "replan_requested":
        return True

    # User modified spec (regenerate plan)
    if context.last_event_type == "spec_modified":
        return True

    # Plan validation failed
    if context.last_event_type == "validation_failed":
        return True

    # Previous plan rejected
    if context.last_event_type == "plan_rejected":
        return True

    return False
```

**Workflow State Transitions:**
- `intent_resolved` → `spec_generation` (when planning starts)
- `spec_generation` → `plan_generation` (when spec complete)
- `plan_generation` → `plan_validation` (when plan drafted)
- `plan_validation` → `plan_ready` (when validation passes)
- `plan_validation` → `spec_generation` (if validation fails, restart)

### Inputs

**Primary Inputs:**
- `clarified_intent: Intent` - Resolved intent from ClarifierAgent
- `context: Phase2Context` - Full reasoning state including clarifications

**Secondary Inputs (Context Fields):**
- `context.intent` - Clarified intent with parameters
- `context.clarifications` - All clarifications made
- `context.specification` - Existing spec (if replanning)
- `context.plan` - Existing plan (if modifying)
- `conversation_history` - Full conversation for context

**External Dependencies:**
- `RequirementDerivationSkill` - Extract requirements from intent
- `AcceptanceCriteriaSkill` - Generate testable criteria
- `RequirementDecompositionSkill` - Break into steps
- `DependencyResolutionSkill` - Identify dependencies
- `CommandMappingSkill` - Map to Phase 1 commands
- `PriorityAssignmentSkill` - Assign priorities
- `PlanValidationSkill` - Validate plan feasibility

### Outputs

**Primary Outputs:**
- `specification: Specification` - Formal spec document
- `plan: ExecutionPlan` - Validated execution plan

**Specification Object Structure:**
```python
@dataclass
class Specification:
    # Identity
    title: str
    description: str

    # Requirements
    requirements: List[Requirement]  # Functional requirements
    acceptance_criteria: List[str]  # Testable acceptance criteria
    constraints: List[Constraint]  # Non-functional constraints
    assumptions: List[str]  # Assumptions made

    # Metadata
    metadata: Dict[str, Any]  # Generation info (model, tokens, etc.)
```

**ExecutionPlan Object Structure:**
```python
@dataclass
class ExecutionPlan:
    # Identity
    title: str
    description: str

    # Steps
    steps: List[PlanStep]  # Ordered list of steps (by dependencies)

    # Analysis
    total_estimated_seconds: float  # Sum of all step estimates
    risk_level: str  # LOW, MEDIUM, HIGH (based on operations)
    dependencies_count: int  # Total dependency edges

    # Validation
    validation_status: str  # PENDING, PASS, WARN, FAIL
    validation_report: Optional[ValidationReport]  # Detailed validation results

    # Metadata
    metadata: Dict[str, Any]  # Generation info
```

**PlanStep Object Structure:**
```python
@dataclass
class PlanStep:
    # Identity
    id: str  # Unique step identifier (e.g., "S001")
    description: str  # Human-readable description

    # Execution
    command: str  # Phase 1 command to execute
    command_type: str  # ADD, LIST, COMPLETE, DELETE, UPDATE, SEARCH

    # Dependencies
    dependencies: List[str]  # IDs of steps this depends on

    # Prioritization
    priority: str  # P1, P2, P3

    # Estimation
    estimated_seconds: float  # Time estimate for execution

    # Status
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED

    # Mapping
    source_requirement: Optional[str]  # Which requirement this fulfills

    # Metadata
    metadata: Dict[str, Any]  # Additional info
```

**Output Types:**

1. **Validated Plan** (`validation_status == "PASS"`):
   - Plan is ready for review
   - Proceed to ReviewerAgent

2. **Plan with Warnings** (`validation_status == "WARN"`):
   - Plan valid but has risks
   - Proceed to ReviewerAgent with warnings

3. **Invalid Plan** (`validation_status == "FAIL"`):
   - Plan has critical issues
   - Replan or request more clarification

4. **Planning Failed** (exception/error):
   - Cannot generate feasible plan
   - Request additional clarification or fallback to Phase 1

### How It Interacts with Context

**Context Reads:**
```python
# Read clarified intent
intent = context.intent
if intent is None:
    raise ValueError("No resolved intent for planning")

# Read clarifications (provide context for spec generation)
clarifications = context.clarifications

# Read existing spec (if replanning)
existing_spec = context.specification

# Read existing plan (if modifying)
existing_plan = context.plan

# Read Phase 1 capabilities (for command mapping)
phase1_commands = context.metadata.get("phase1_capabilities", {})
```

**Context Updates:**
```python
# Store generated specification
specification = generate_specification(intent, clarifications)
context.specification = specification
context.add_artifact("specification", specification, {
    "source": "planner_agent",
    "intent_type": intent.type.value,
    "model": "claude-sonnet-4.5",
    "timestamp": datetime.now().isoformat()
})

# Store generated plan
plan = generate_plan(specification, phase1_capabilities)
context.plan = plan
context.add_artifact("plan", plan, {
    "source": "planner_agent",
    "spec_id": get_artifact_id(specification),
    "model": "claude-sonnet-4.5",
    "timestamp": datetime.now().isoformat()
})

# Update workflow state
context.transition_to("plan_ready")

# Log planning decisions
context._log_event("specification_generated", {
    "title": specification.title,
    "requirements_count": len(specification.requirements),
    "acceptance_criteria_count": len(specification.acceptance_criteria)
})

context._log_event("plan_generated", {
    "title": plan.title,
    "steps_count": len(plan.steps),
    "estimated_duration": plan.total_estimated_seconds,
    "validation_status": plan.validation_status
})

# Update reasoning trace
context.reasoning_trace.append({
    "stage": "planner",
    "action": "spec_and_plan_generated",
    "spec_title": specification.title,
    "plan_steps": len(plan.steps),
    "validation_status": plan.validation_status,
    "timestamp": datetime.now().isoformat()
})
```

**Context Invariants:**
- `context.specification` is always stored before `context.plan`
- `context.plan.steps` are always topologically sorted (by dependencies)
- All `plan.steps[i].command` are valid Phase 1 commands
- Circular dependencies never exist in `plan.steps`
- All updates logged to `context.reasoning_trace`

---

## ReviewerAgent

### Responsibility

ReviewerAgent is responsible for **Stage 4: Plan Review & Approval**. It facilitates user review and approval of generated artifacts by:

- Presenting specification to user for review
- Presenting plan to user for review
- Collecting user feedback and modifications
- Validating user-provided changes
- Requesting explicit approval before execution
- Generating approval checkpoints

**Key Insight**: ReviewerAgent is the human-in-the-loop guardrail. It prevents autonomous execution of potentially incorrect or dangerous plans.

### When It Is Invoked

ReviewerAgent is invoked when:

1. **Plan is ready** (`context.workflow_state == "plan_ready"`)
2. **User requests review** of spec or plan
3. **User submits modifications** to spec or plan
4. **User rejects plan** (requires replanning)
5. **After spec generation** (before planning)

**Invocation Conditions:**
```python
def should_invoke(context: Phase2Context) -> bool:
    # Plan ready for review
    if context.workflow_state == "plan_ready":
        return True

    # Spec generated (first review point)
    if context.workflow_state == "specification" and not context.specification_reviewed:
        return True

    # User requested review
    if context.last_event_type == "review_requested":
        return True

    # User submitted modifications
    if context.last_event_type == "modifications_submitted":
        return True

    # User rejected plan (may need replanning)
    if context.last_event_type == "plan_rejected":
        return True

    return False
```

**Workflow State Transitions:**
- `plan_ready` → `reviewing_spec` (when reviewing specification)
- `reviewing_spec` → `reviewing_plan` (when spec approved)
- `reviewing_plan` → `awaiting_approval` (when plan reviewed)
- `awaiting_approval` → `plan_approved` (when user approves)
- `reviewing_plan` → `plan_ready` (when user modifies plan)

### Inputs

**Primary Inputs:**
- `specification: Specification` - Generated specification to review
- `plan: ExecutionPlan` - Generated plan to review
- `context: Phase2Context` - Full reasoning state

**Secondary Inputs (Context Fields):**
- `context.specification` - Specification document
- `context.plan` - Execution plan
- `conversation_history` - Review dialog history
- `context.last_event_type` - What triggered review

**External Dependencies:**
- `SpecificationPresentationSkill` - Format spec for display
- `PlanPresentationSkill` - Format plan for display
- `ModificationValidationSkill` - Validate user changes
- `ApprovalTrackingSkill` - Track approval state

### Outputs

**Primary Outputs:**
- `review_result: ReviewResult` - Outcome of review process
- `approved_artifacts: Dict[str, Any]` - Approved spec and plan

**ReviewResult Object Structure:**
```python
@dataclass
class ReviewResult:
    # Outcome
    status: str  # APPROVED, MODIFIED, REJECTED, REJECTED_WITH_FEEDBACK

    # Reviewed artifacts
    specification: Specification  # Final specification (may be modified)
    plan: ExecutionPlan  # Final plan (may be modified)

    # User feedback
    user_feedback: Optional[str]  # Feedback provided by user
    modifications: List[Modification]  # Changes made by user

    # Validation
    validation_result: str  # PASS, WARN, FAIL (validates user changes)

    # Metadata
    metadata: Dict[str, Any]  # Review metadata
```

**Modification Object Structure:**
```python
@dataclass
class Modification:
    id: str  # Unique modification ID
    artifact_type: str  # "specification" or "plan"
    target: str  # What was modified (field name or step ID)
    action: str  # "add", "update", "delete"
    old_value: Any  # Original value
    new_value: Any  # New value
    rationale: str  # User's reason for modification
    timestamp: str  # When modification was made
```

**Output Types:**

1. **Approved** (`status == "APPROVED"` and `validation_result == "PASS"`):
   - Artifacts approved without changes
   - Proceed to ExecutorAgent

2. **Approved with Modifications** (`status == "MODIFIED"` and `validation_result == "PASS"`):
   - User made valid changes
   - Proceed to ExecutorAgent with modified artifacts

3. **Rejected** (`status == "REJECTED"`):
   - User rejected plan completely
   - Return to PlannerAgent for replanning

4. **Rejected with Feedback** (`status == "REJECTED_WITH_FEEDBACK"`):
   - User rejected with specific feedback
   - Return to PlannerAgent or ClarifierAgent

5. **Invalid Modifications** (`validation_result == "FAIL"`):
   - User's changes invalid
   - Reject modifications and request correction

### How It Interacts with Context

**Context Reads:**
```python
# Read artifacts to review
specification = context.specification
plan = context.plan

# Read review history
review_history = [e for e in context.history if e.type.startswith("review_")]

# Check if already reviewed
already_reviewed = context.metadata.get("specification_reviewed", False)
```

**Context Updates:**
```python
# Mark specification as reviewed
context.specification_reviewed = True

# Store review result
review_result = conduct_review(specification, plan, user_input)
context.review_result = review_result
context.add_artifact("review_result", review_result, {
    "reviewer": "user",
    "timestamp": datetime.now().isoformat()
})

# Handle modifications
if review_result.status == "MODIFIED":
    # Update specification
    context.specification = review_result.specification
    context.add_artifact("specification_modified", review_result.specification, {
        "source": "reviewer_agent",
        "modification_count": len(review_result.modifications)
    })

    # Update plan
    context.plan = review_result.plan
    context.add_artifact("plan_modified", review_result.plan, {
        "source": "reviewer_agent",
        "modification_count": len(review_result.modifications)
    })

# Handle rejection
if review_result.status == "REJECTED":
    context.transition_to("plan_rejected")
    context._log_event("plan_rejected", {
        "feedback": review_result.user_feedback,
        "reason": "user_rejection"
    })

# Handle approval
if review_result.status in ["APPROVED", "MODIFIED"]:
    context.transition_to("plan_approved")
    context._log_event("plan_approved", {
        "specification_title": review_result.specification.title,
        "plan_title": review_result.plan.title,
        "modification_count": len(review_result.modifications) if review_result.modifications else 0
    })

# Update reasoning trace
context.reasoning_trace.append({
    "stage": "reviewer",
    "action": "review_completed",
    "review_status": review_result.status,
    "validation_result": review_result.validation_result,
    "modifications_count": len(review_result.modifications) if review_result.modifications else 0,
    "timestamp": datetime.now().isoformat()
})
```

**Context Invariants:**
- `context.specification` only updated after validation passes
- `context.plan` only updated after validation passes
- Approval only granted after explicit user confirmation
- All modifications logged to `context.reasoning_trace`

---

## ExecutorAgent

### Responsibility

ExecutorAgent is responsible for **Stage 5: Plan Execution**. It executes approved plans using Phase 1 capabilities by:

- Orchestrating step execution in dependency order
- Dispatching Phase 1 commands for each step
- Tracking execution progress and results
- Handling errors and applying rollback strategies
- Aggregating results and generating reports
- Updating Phase 2 context with execution outcomes

**Key Insight**: ExecutorAgent is the bridge between intelligence reasoning and deterministic Phase 1 execution. It does NOT reason - it executes.

### When It Is Invoked

ExecutorAgent is invoked when:

1. **Plan is approved** (`context.workflow_state == "plan_approved"`)
2. **User requests plan execution** (manual trigger)
3. **Partial execution resume** (after interruption)
4. **Retry after error** (with updated plan)

**Invocation Conditions:**
```python
def should_invoke(context: Phase2Context) -> bool:
    # Plan approved and ready for execution
    if context.workflow_state == "plan_approved":
        return True

    # User explicitly requested execution
    if context.last_event_type == "execute_requested":
        return True

    # Resume partial execution
    if context.last_event_type == "resume_requested":
        return True

    # Retry after error (if plan still valid)
    if context.last_event_type == "retry_requested" and context.plan:
        return True

    return False
```

**Workflow State Transitions:**
- `plan_approved` → `executing` (when execution starts)
- `executing` → `completed` (when all steps succeed)
- `executing` → `failed` (when step fails)
- `failed` → `rolling_back` (if rollback possible)
- `rolling_back` → `completed` (rollback successful)
- `rolling_back` → `failed` (rollback failed)

### Inputs

**Primary Inputs:**
- `approved_plan: ExecutionPlan` - Approved plan to execute
- `phase1_executor: Phase1Executor` - Phase 1 command executor
- `context: Phase2Context` - Full reasoning state

**Secondary Inputs (Context Fields):**
- `context.plan` - Approved execution plan
- `context.execution_results` - Previous results (if resuming)
- `conversation_history` - For progress reporting

**External Dependencies:**
- `Phase1Executor` - Execute individual commands (existing Phase 1)
- `StepExecutionSkill` - Execute individual steps
- `ProgressTrackingSkill` - Track execution state
- `ErrorHandlingSkill` - Handle and classify errors
- `RollbackExecutionSkill` - Apply rollback strategies
- `ResultAggregationSkill` - Compile final report

### Outputs

**Primary Outputs:**
- `execution_result: ExecutionResult` - Complete execution outcome
- `final_state: Dict[str, Any]` - Updated task store state

**ExecutionResult Object Structure:**
```python
@dataclass
class ExecutionResult:
    # Outcome
    status: str  # COMPLETED, PARTIAL, FAILED, CANCELLED

    # Progress
    steps_completed: int  # Number of successfully completed steps
    steps_total: int  # Total steps in plan
    completion_percentage: float  # 0.0 - 100.0

    # Timing
    started_at: str  # ISO timestamp
    completed_at: Optional[str]  # ISO timestamp (if completed)
    total_duration_seconds: float  # Total execution time

    # Errors
    errors: List[ExecutionError]  # Errors encountered during execution
    warnings: List[ExecutionWarning]  # Warnings during execution

    # Rollback
    rollback_performed: bool  # Whether rollback was executed
    rollback_status: Optional[str]  # SUCCESS, PARTIAL, FAILED

    # Results
    step_results: Dict[str, StepResult]  # Results per step (step_id -> result)

    # State changes
    tasks_added: int  # Tasks created
    tasks_modified: int  # Tasks updated
    tasks_deleted: int  # Tasks deleted
    tasks_completed: int  # Tasks marked complete

    # Metadata
    metadata: Dict[str, Any]  # Execution metadata
```

**StepResult Object Structure:**
```python
@dataclass
class StepResult:
    step_id: str  # Step identifier
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    command: str  # Phase 1 command executed
    output: str  # Command output
    error: Optional[ExecutionError]  # Error if failed
    started_at: str  # ISO timestamp
    completed_at: Optional[str]  # ISO timestamp (if completed)
    duration_seconds: float  # Execution duration
```

**ExecutionError Object Structure:**
```python
@dataclass
class ExecutionError:
    error_id: str  # Unique error identifier
    step_id: str  # Which step failed
    error_type: str  # VALIDATION, EXECUTION, TIMEOUT, API_ERROR
    error_message: str  # Human-readable error message
    error_code: Optional[str]  # Machine-readable error code
    fatal: bool  # Whether error is fatal (cannot continue)
    recoverable: bool  # Whether recovery/rollback possible
    occurred_at: str  # ISO timestamp
```

**Output Types:**

1. **Completed Successfully** (`status == "COMPLETED"`):
   - All steps executed successfully
   - Report success and final state

2. **Partially Completed** (`status == "PARTIAL"`):
   - Some steps succeeded, some failed
   - Report partial results and errors

3. **Failed** (`status == "FAILED"`):
   - Critical failure prevented completion
   - Report errors and rollback status

4. **Cancelled** (`status == "CANCELLED"`):
   - User interrupted execution
   - Report partial results and cancelled steps

### How It Interacts with Context

**Context Reads:**
```python
# Read approved plan
plan = context.plan
if plan.validation_status != "PASS":
    raise ValueError("Cannot execute unapproved plan")

# Read Phase 1 executor
executor = context.phase1_executor

# Read previous results (if resuming)
previous_results = context.execution_results
```

**Context Updates:**
```python
# Mark execution in progress
context.transition_to("executing")
context._log_event("execution_started", {
    "plan_title": plan.title,
    "steps_count": len(plan.steps),
    "estimated_duration": plan.total_estimated_seconds
})

# Execute each step
step_results = {}
for step in plan.steps:
    # Update step status
    step.status = "IN_PROGRESS"
    context._log_event("step_started", {
        "step_id": step.id,
        "command": step.command
    })

    # Execute step using Phase 1
    try:
        result = executor.execute(step.command)

        # Step completed successfully
        step.status = "COMPLETED"
        step_results[step.id] = StepResult(
            step_id=step.id,
            status="COMPLETED",
            command=step.command,
            output=result.message,
            started_at=start_time,
            completed_at=end_time,
            duration_seconds=duration
        )

        context._log_event("step_completed", {
            "step_id": step.id,
            "duration_seconds": duration
        })

    except Exception as e:
        # Step failed
        step.status = "FAILED"
        step_results[step.id] = StepResult(
            step_id=step.id,
            status="FAILED",
            command=step.command,
            error=ExecutionError(
                error_id=generate_error_id(),
                step_id=step.id,
                error_type="EXECUTION",
                error_message=str(e),
                fatal=is_fatal(e),
                recoverable=is_recoverable(e),
                occurred_at=datetime.now().isoformat()
            )
        )

        context._log_event("step_failed", {
            "step_id": step.id,
            "error": str(e),
            "fatal": is_fatal(e)
        })

        # Handle error
        if is_fatal(e):
            break  # Stop execution
        elif is_recoverable(e):
            continue  # Try next step
        else:
            rollback_and_break()  # Rollback and stop

# Store execution results
execution_result = ExecutionResult(
    status=determine_status(step_results),
    steps_completed=len([r for r in step_results.values() if r.status == "COMPLETED"]),
    steps_total=len(plan.steps),
    completion_percentage=len([r for r in step_results.values() if r.status == "COMPLETED"]) / len(plan.steps) * 100,
    started_at=start_time,
    completed_at=end_time,
    total_duration_seconds=total_duration,
    errors=extract_errors(step_results),
    step_results=step_results,
    tasks_added=count_tasks_by_type(step_results, "add"),
    tasks_modified=count_tasks_by_type(step_results, "update"),
    tasks_deleted=count_tasks_by_type(step_results, "delete"),
    tasks_completed=count_tasks_by_type(step_results, "complete"),
    metadata={"executor": "phase1", "model": "deterministic"}
)

context.execution_results = execution_result
context.add_artifact("execution_result", execution_result, {
    "source": "executor_agent",
    "plan_id": get_artifact_id(plan),
    "timestamp": datetime.now().isoformat()
})

# Update workflow state
if execution_result.status == "COMPLETED":
    context.transition_to("completed")
    context._log_event("execution_completed", {
        "steps_completed": execution_result.steps_completed,
        "steps_total": execution_result.steps_total,
        "total_duration_seconds": execution_result.total_duration_seconds
    })
else:
    context.transition_to("failed")
    context._log_event("execution_failed", {
        "status": execution_result.status,
        "errors_count": len(execution_result.errors),
        "steps_completed": execution_result.steps_completed
    })

# Update reasoning trace
context.reasoning_trace.append({
    "stage": "executor",
    "action": "execution_completed",
    "status": execution_result.status,
    "steps_completed": execution_result.steps_completed,
    "steps_total": execution_result.steps_total,
    "completion_percentage": execution_result.completion_percentage,
    "errors_count": len(execution_result.errors),
    "timestamp": datetime.now().isoformat()
})
```

**Context Invariants:**
- `context.execution_results` only set after execution completes (full or partial)
- `context.workflow_state` reflects final outcome (completed or failed)
- All step results logged to `context.reasoning_trace`
- Rollback results logged if performed

---

## Agent Interaction Flow

```
User: "organize my tasks for today"
    │
    ▼
┌──────────────────────────────────────┐
│  ClarifierAgent                  │
│  • Parse intent                  │
│  • Detect ambiguity              │
│  • Ask: "Which tasks?"         │
└──────────────────────────────────────┘
    │
    ▼
User: "the project tasks" + "urgent ones first"
    │
    ▼
┌──────────────────────────────────────┐
│  ClarifierAgent (resume)         │
│  • Collect clarifications        │
│  • Intent resolved!             │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  PlannerAgent                   │
│  • Generate specification       │
│  • Create plan                 │
│  • Validate plan               │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  ReviewerAgent                  │
│  • Show spec & plan            │
│  • Request approval            │
└──────────────────────────────────────┘
    │
    ▼
User: "looks good, approve"
    │
    ▼
┌──────────────────────────────────────┐
│  ReviewerAgent (approve)         │
│  • Mark approved                │
│  • Update context              │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  ExecutorAgent                  │
│  • Execute steps               │
│  • Track progress             │
│  • Report results              │
└──────────────────────────────────────┘
    │
    ▼
User: "3 tasks organized, 2 completed!"
```

---

## Error Handling and Recovery

### ClarifierAgent Errors

| Error | Recovery |
|-------|----------|
| Confidence < 0.3 | Request rephrasing or fallback to Phase 1 |
| Ambiguity timeout | Assume defaults or fallback to Phase 1 |
| Contradictory clarifications | Flag for user resolution |
| Max clarifications exceeded | Use best guess or fallback |

### PlannerAgent Errors

| Error | Recovery |
|-------|----------|
| Cannot generate spec | Request more clarification |
| Plan validation fails | Replan or ask user for constraints |
| Circular dependencies | Alert user and request constraints |
| Unmappable requirement | Flag as not implementable |

### ReviewerAgent Errors

| Error | Recovery |
|-------|----------|
| Invalid modifications | Reject and request correction |
| User rejects without feedback | Ask for clarification on rejection |
| Approval timeout | Request explicit confirmation |

### ExecutorAgent Errors

| Error | Recovery |
|-------|----------|
| Non-fatal step failure | Continue with next step |
| Fatal step failure | Stop and request user decision |
| All steps failed | Rollback and report |
| User interrupt | Stop gracefully and report partial |

---

## References

- **Phase 2 Intelligence Model Spec**: `specs/007-phase2-intelligence-model/spec.md`
- **ADR-004**: Phase 2 Intelligence Integration Architecture
- **Spec 006**: Todo Console App (Phase 1)
- **Agent Base Interface**: `src/intelligence/sdd/agent_base.py`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
