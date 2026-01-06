# Reusable Skills Specification: Phase 2 Intelligence

**Feature Branch**: `007-phase2-intelligence-model`
**Created**: 2026-01-06
**Status**: Draft
**Related Spec**: `007-phase2-intelligence-model/spec.md`
**Related ADR**: `history/adr/004-phase2-intelligence-integration.adr.md`

## Overview

This specification defines reusable, stateless, domain-agnostic cognitive skills for Phase 2 intelligence. Skills are fundamental building blocks that agents orchestrate to accomplish reasoning tasks.

**Skill Properties:**
- **Stateless**: No memory between invocations - all state provided via context/inputs
- **Domain-agnostic**: No hardcoded domain logic - work across all intent types
- **Reusable**: Multiple agents can use the same skill
- **Composable**: Skill output can be input to another skill
- **Testable**: Pure functions with clear I/O - easy to unit test

---

## Skill 1: IntentAnalysisSkill

### Purpose

IntentAnalysisSkill performs deep semantic analysis of user input to extract structured understanding. It goes beyond simple keyword matching to derive meaning from natural language.

**Capabilities:**
- Classify high-level intent category (ORGANIZE, PRIORITIZE, PLAN, QUERY)
- Extract entities (tasks, priorities, timeframes, constraints)
- Derive implicit requirements from context
- Calculate confidence scores for parsing quality
- Identify missing critical information

### Inputs

**Required Inputs:**
- `user_input: str` - Raw natural language from user
- `conversation_history: List[Message]` - Previous messages for context

**Optional Inputs:**
- `domain_context: Dict[str, Any]` - Domain-specific knowledge (e.g., todo operations)
- `existing_state: Dict[str, Any]` - Current task state

**Input Validation:**
```python
def validate_inputs(self, user_input: str, **kwargs) -> None:
    if not user_input or not user_input.strip():
        raise SkillValidationError("user_input must be non-empty string")
    if len(user_input) > 10000:  # Reasonable limit
        raise SkillValidationError("user_input too long (>10000 characters)")
```

### Outputs

**Primary Output:**
```python
@dataclass
class IntentAnalysisResult:
    # Classification
    intent_type: IntentType  # ORGANIZE, PRIORITIZE, PLAN, QUERY
    confidence: float  # 0.0 - 1.0 - parsing confidence

    # Extracted entities
    entities: List[Entity]  # Extracted entities (tasks, priorities, etc.)

    # Requirements
    explicit_requirements: List[str]  # Explicitly stated requirements
    implicit_requirements: List[str]  # Inferred requirements

    # Information completeness
    completeness_score: float  # 0.0 - 1.0
    missing_information: List[str]  # Critical info not provided

    # Context
    timeframes: List[str]  # Extracted time references ("today", "this week")
    constraints: List[str]  # Identified constraints

    # Metadata
    metadata: Dict[str, Any]  # Analysis metadata (model, tokens, etc.)
```

**Entity Object:**
```python
@dataclass
class Entity:
    entity_type: str  # TASK, PRIORITY, TIMEFRAME, CONSTRAINT
    value: str  # Extracted value
    confidence: float  # Extraction confidence
    position: Tuple[int, int]  # Start/end position in text
```

### Failure Modes

| Failure Mode | Detection | Recovery | Error Type |
|--------------|------------|-----------|-------------|
| **Uninterpretable input** | Confidence < 0.3 | Return to user with rephrasing request | `SkillExecutionError` |
| **Empty input** | Input validation | Reject with "Please provide input" | `SkillValidationError` |
| **Timeout** | Execution > 30s | Abort and return partial result | `SkillTimeoutError` |
| **No entities found** | entities list empty | Flag as requiring clarification | Success with warnings |
| **Conflicting entities** | Same entity type with different values | Return conflict list for resolution | Success with warnings |

**Error Example:**
```python
if confidence < 0.3:
    raise SkillExecutionError(
        f"Cannot interpret intent: '{user_input}' (confidence: {confidence})",
        details={"confidence": confidence, "input": user_input}
    )
```

---

## Skill 2: AmbiguityDetectionSkill

### Purpose

AmbiguityDetectionSkill identifies phrases and constructs in natural language that are unclear or have multiple valid interpretations. It flags these for human clarification before proceeding.

**Capabilities:**
- Detect ambiguous pronouns (it, this, that) without clear antecedents
- Identify vague quantifiers (some, few, many)
- Find uncertain language (maybe, could, might)
- Spot incomplete phrases (etc., and so on)
- Detect missing critical information
- Rank ambiguities by severity

### Inputs

**Required Inputs:**
- `text: str` - Text to analyze for ambiguity

**Optional Inputs:**
- `conversation_history: List[Message]` - For pronoun resolution
- `domain_context: Dict[str, Any]` - Domain-specific ambiguity rules

**Input Validation:**
```python
def validate_inputs(self, text: str, **kwargs) -> None:
    if not text or not text.strip():
        raise SkillValidationError("text must be non-empty string")
    if len(text) > 5000:
        raise SkillValidationError("text too long (>5000 characters)")
```

### Outputs

**Primary Output:**
```python
@dataclass
class AmbiguityReport:
    # Overall assessment
    has_ambiguity: bool  # Whether any ambiguities detected
    ambiguity_score: float  # 0.0 - 1.0 - overall ambiguity level
    clarity_level: str  # CLEAR, MODERATE, UNCLEAR

    # Detected ambiguities
    ambiguities: List[Ambiguity]  # All detected ambiguities
    critical_ambiguities: List[Ambiguity]  # High-severity only

    # Suggestions
    clarification_questions: List[str]  # Suggested clarification questions
    required_clarifications: int  # Minimum clarifications needed

    # Metadata
    metadata: Dict[str, Any]  # Detection metadata
```

**Ambiguity Object:**
```python
@dataclass
class Ambiguity:
    ambiguity_id: str  # Unique identifier
    ambiguity_type: str  # ambiguous_pronoun, vague_quantifier, uncertain_language, missing_info
    phrase: str  # The ambiguous phrase
    position: Tuple[int, int]  # Start/end position
    severity: str  # LOW, MEDIUM, HIGH
    context: str  # Surrounding context (window)
    suggestion: str  # How to resolve
    requires_clarification: bool  # Whether clarification is mandatory
```

### Failure Modes

| Failure Mode | Detection | Recovery | Error Type |
|--------------|------------|-----------|-------------|
| **Empty text** | Input validation | Reject with error message | `SkillValidationError` |
| **Timeout** | Analysis > 15s | Return partial results | `SkillTimeoutError` |
| **No text language** | Non-ASCII or no recognizable words | Flag as "needs review" | Success with warnings |
| **Excessive ambiguity** | ambiguity_score > 0.8 | Flag as "too unclear - please rephrase" | Success with severe warning |

**Example Output:**
```python
AmbiguityReport(
    has_ambiguity=True,
    ambiguity_score=0.65,
    clarity_level="UNCLEAR",
    ambiguities=[
        Ambiguity(
            ambiguity_type="ambiguous_pronoun",
            phrase="it",
            severity="HIGH",
            context="complete it today",
            suggestion="Specify which task you mean",
            requires_clarification=True
        ),
        Ambiguity(
            ambiguity_type="vague_quantifier",
            phrase="some tasks",
            severity="MEDIUM",
            context="organize some tasks",
            suggestion="Specify exact number of tasks",
            requires_clarification=True
        )
    ],
    clarification_questions=[
        "Which tasks do you want to organize?",
        "How many tasks are we talking about?"
    ],
    required_clarifications=2
)
```

---

## Skill 3: TaskDecompositionSkill

### Purpose

TaskDecompositionSkill breaks down high-level goals or requirements into actionable, executable steps. It transforms abstract intentions into concrete operations.

**Capabilities:**
- Decompose requirements into implementation steps
- Identify dependencies between steps
- Determine execution order (topological sort)
- Assign priorities to steps
- Estimate effort for each step
- Map abstract steps to concrete commands

### Inputs

**Required Inputs:**
- `requirements: List[str]` - List of requirements to decompose
- `target_operations: List[str]` - Available Phase 1 operations

**Optional Inputs:**
- `existing_tasks: List[Task]` - Current task state
- `complexity_level: str` - SIMPLE, MODERATE, COMPLEX
- `max_depth: int` - Maximum decomposition depth (default: 5)

**Input Validation:**
```python
def validate_inputs(self, requirements: List[str], **kwargs) -> None:
    if not requirements:
        raise SkillValidationError("requirements must be non-empty list")
    if len(requirements) > 100:
        raise SkillValidationError("too many requirements (>100)")
```

### Outputs

**Primary Output:**
```python
@dataclass
class DecompositionResult:
    # Decomposed steps
    steps: List[PlanStep]  # Ordered list of steps
    total_steps: int  # Total number of steps
    average_complexity: float  # Average step complexity

    # Dependencies
    dependency_graph: Dict[str, List[str]]  # step_id -> dependent step IDs
    has_circular_dependencies: bool  # Whether cycles detected
    critical_path: List[str]  # Longest dependency chain

    # Estimation
    total_estimated_duration: float  # Sum of all step estimates
    max_estimated_duration: float  # Longest individual step
    confidence: float  # 0.0 - 1.0 - estimation confidence

    # Mapping
    requirement_to_steps: Dict[str, List[str]]  # requirement -> step IDs

    # Metadata
    metadata: Dict[str, Any]  # Decomposition metadata
```

**PlanStep Object (from agents spec):**
```python
@dataclass
class PlanStep:
    id: str  # Unique step identifier
    description: str  # Human-readable description
    command: str  # Phase 1 command to execute
    command_type: str  # ADD, LIST, COMPLETE, DELETE, UPDATE
    dependencies: List[str]  # Step IDs this depends on
    priority: str  # P1, P2, P3
    estimated_seconds: float  # Time estimate
    source_requirement: Optional[str]  # Which requirement this fulfills
```

### Failure Modes

| Failure Mode | Detection | Recovery | Error Type |
|--------------|------------|-----------|-------------|
| **Unmappable requirement** | No valid Phase 1 command matches | Flag as "not implementable" | `SkillExecutionError` |
| **Circular dependencies** | Dependency graph has cycle | Alert and request resolution | Success with error flag |
| **Excessive depth** | Decomposition exceeds max_depth | Stop and request constraint | `SkillExecutionError` |
| **No valid steps** | All steps fail validation | Return empty with explanation | `SkillExecutionError` |
| **Timeout** | Decomposition > 60s | Return partial result | `SkillTimeoutError` |

**Example Output:**
```python
DecompositionResult(
    steps=[
        PlanStep(
            id="S001",
            description="Create task: 'Review PRs'",
            command="add task: Review PRs with priority HIGH",
            command_type="ADD",
            dependencies=[],
            priority="P1",
            estimated_seconds=2.0
        ),
        PlanStep(
            id="S002",
            description="Create task: 'Fix bugs'",
            command="add task: Fix bugs with priority HIGH",
            command_type="ADD",
            dependencies=[],
            priority="P1",
            estimated_seconds=2.0
        ),
        PlanStep(
            id="S003",
            description="List high-priority tasks",
            command="list tasks with priority HIGH",
            command_type="LIST",
            dependencies=["S001", "S002"],
            priority="P1",
            estimated_seconds=1.0
        )
    ],
    total_steps=3,
    dependency_graph={"S003": ["S001", "S002"]},
    has_circular_dependencies=False,
    total_estimated_duration=5.0,
    confidence=0.85
)
```

---

## Skill 4: PlanValidationSkill

### Purpose

PlanValidationSkill verifies that an execution plan is sound, complete, and executable before proceeding to execution. It catches issues early to prevent execution failures.

**Capabilities:**
- Validate plan completeness (all requirements addressed)
- Check for circular dependencies
- Verify command syntax against Phase 1 executor
- Assess risk factors (dangerous operations)
- Estimate likelihood of success
- Identify rollback strategies for failure recovery

### Inputs

**Required Inputs:**
- `plan: ExecutionPlan` - Plan to validate
- `phase1_schema: Dict[str, Any]` - Phase 1 command schema

**Optional Inputs:**
- `current_state: Dict[str, Any]` - Current task state for validation
- `validation_rules: List[Rule]` - Custom validation rules

**Input Validation:**
```python
def validate_inputs(self, plan: ExecutionPlan, **kwargs) -> None:
    if not plan or not plan.steps:
        raise SkillValidationError("plan must have at least one step")
    if len(plan.steps) > 1000:
        raise SkillValidationError("plan has too many steps (>1000)")
```

### Outputs

**Primary Output:**
```python
@dataclass
class ValidationReport:
    # Overall status
    status: str  # PASS, WARN, FAIL
    overall_score: float  # 0.0 - 1.0 - plan quality score
    is_executable: bool  # Whether plan can execute

    # Validation checks
    checks: List[ValidationCheck]  # All validation checks performed
    passed_checks: int  # Number of passed checks
    failed_checks: int  # Number of failed checks
    warning_checks: int  # Number of warnings

    # Issues found
    issues: List[ValidationIssue]  # Issues detected
    critical_issues: List[ValidationIssue]  # Must-fix before execution
    warnings: List[ValidationIssue]  # Should-fix before execution

    # Risk assessment
    risk_level: str  # LOW, MEDIUM, HIGH
    risk_factors: List[str]  # Identified risks

    # Recovery
    rollback_strategies: List[RollbackStrategy]  # Recovery strategies

    # Recommendations
    recommendations: List[str]  # Improvement suggestions

    # Metadata
    metadata: Dict[str, Any]  # Validation metadata
```

**ValidationCheck Object:**
```python
@dataclass
class ValidationCheck:
    check_id: str  # Unique identifier
    check_name: str  # Human-readable name
    check_type: str  # COMPLETENESS, DEPENDENCY, SYNTAX, RISK
    status: str  # PASS, FAIL, WARN
    message: str  # Result message
    severity: str  # LOW, MEDIUM, HIGH
    checked_at: str  # ISO timestamp
```

**ValidationIssue Object:**
```python
@dataclass
class ValidationIssue:
    issue_id: str  # Unique identifier
    check_id: str  # Which check found this issue
    issue_type: str  # MISSING_STEP, CIRCULAR_DEPENDENCY, INVALID_COMMAND, RISK
    severity: str  # LOW, MEDIUM, HIGH
    description: str  # Issue description
    location: str  # Where issue occurs (step ID, etc.)
    suggestion: str  # How to resolve
    block_execution: bool  # Whether this blocks execution
```

**RollbackStrategy Object:**
```python
@dataclass
class RollbackStrategy:
    strategy_id: str  # Unique identifier
    strategy_type: str  # REVERSE, SKIP, RETRY
    applicable_to: List[str]  # Step IDs or command types
    description: str  # Strategy description
    effectiveness: float  # Estimated effectiveness 0.0-1.0
```

### Failure Modes

| Failure Mode | Detection | Recovery | Error Type |
|--------------|------------|-----------|-------------|
| **Invalid plan structure** | Missing required fields | Return FAIL status with details | `SkillValidationError` |
| **Cannot validate commands** | Phase 1 schema unavailable | Return WARN with "manual verification needed" | Success with warnings |
| **Too many issues** | >50 issues found | Return FAIL with summary | Success with error flag |
| **Circular dependencies** | Graph cycle detected | Flag critical issue requiring resolution | Success with critical issues |
| **Timeout** | Validation > 30s | Return partial validation | `SkillTimeoutError` |

**Example Output:**
```python
ValidationReport(
    status="WARN",
    overall_score=0.75,
    is_executable=True,
    checks=[
        ValidationCheck(
            check_name="Completeness Check",
            check_type="COMPLETENESS",
            status="PASS",
            message="All requirements addressed",
            severity="LOW"
        ),
        ValidationCheck(
            check_name="Dependency Check",
            check_type="DEPENDENCY",
            status="PASS",
            message="No circular dependencies",
            severity="LOW"
        ),
        ValidationCheck(
            check_name="Syntax Check",
            check_type="SYNTAX",
            status="WARN",
            message="Step S004 command syntax unusual",
            severity="MEDIUM"
        )
    ],
    passed_checks=2,
    failed_checks=0,
    warning_checks=1,
    critical_issues=[],
    warnings=[
        ValidationIssue(
            issue_type="UNUSUAL_SYNTAX",
            severity="MEDIUM",
            description="Command syntax for S004 is unusual",
            location="S004",
            suggestion="Verify command format manually",
            block_execution=False
        )
    ],
    risk_level="MEDIUM",
    recommendations=["Verify unusual command syntax before execution"]
)
```

---

## Skill 5: ResultEvaluationSkill

### Purpose

ResultEvaluationSkill assesses execution results against original intent and specification to determine success, quality, and necessary next actions.

**Capabilities:**
- Compare execution results against acceptance criteria
- Calculate success metrics (completion rate, accuracy)
- Identify deviations from expected outcomes
- Classify errors by severity and recoverability
- Generate human-readable execution reports
- Recommend next actions (retry, proceed, fallback)

### Inputs

**Required Inputs:**
- `execution_result: ExecutionResult` - Results from ExecutorAgent
- `original_intent: Intent` - Original user intent
- `specification: Optional[Specification]` - Original specification (if available)

**Optional Inputs:**
- `plan: Optional[ExecutionPlan]` - Original execution plan
- `acceptance_criteria: Optional[List[str]]` - Success criteria

**Input Validation:**
```python
def validate_inputs(self, execution_result: ExecutionResult, **kwargs) -> None:
    if not execution_result:
        raise SkillValidationError("execution_result must be provided")
```

### Outputs

**Primary Output:**
```python
@dataclass
class EvaluationResult:
    # Overall assessment
    success: bool  # Whether execution succeeded overall
    overall_quality_score: float  # 0.0 - 1.0 - execution quality
    quality_level: str  # EXCELLENT, GOOD, ACCEPTABLE, POOR, FAILED

    # Completion metrics
    steps_completed: int  # Number of completed steps
    steps_total: int  # Total steps in plan
    completion_rate: float  # Percentage completed
    completion_time_seconds: float  # Total execution time
    efficiency_score: float  # 0.0 - 1.0 - time vs estimate

    # Error analysis
    total_errors: int  # Total errors encountered
    fatal_errors: int  # Fatal (blocking) errors
    recoverable_errors: int  # Recoverable (non-blocking) errors
    error_categories: Dict[str, int]  # Errors by type

    # Intent alignment
    intent_satisfied: bool  # Whether original intent was satisfied
    intent_alignment_score: float  # 0.0 - 1.0 - alignment with intent
    unfulfilled_requirements: List[str]  # Requirements not met

    # Acceptance criteria
    acceptance_criteria_met: List[str]  # Criteria satisfied
    acceptance_criteria_failed: List[str]  # Criteria not satisfied
    acceptance_rate: float  # Percentage of criteria met

    # Recommendations
    recommended_action: str  # PROCEED, RETRY, FALLBACK, MANUAL_REVIEW
    retry_probability: float  # Estimated success on retry (0.0-1.0)
    retry_suggestions: List[str]  # How to improve retry chances

    # Report
    human_readable_report: str  # Formatted report for user
    summary: str  # One-sentence summary

    # Metadata
    metadata: Dict[str, Any]  # Evaluation metadata
```

### Failure Modes

| Failure Mode | Detection | Recovery | Error Type |
|--------------|------------|-----------|-------------|
| **Missing execution result** | Input validation | Reject with error | `SkillValidationError` |
| **Invalid result structure** | Malformed ExecutionResult | Return FAILED with error | `SkillExecutionError` |
| **Cannot evaluate** | Missing intent/specification | Flag as "manual review needed" | Success with warnings |
| **Timeout** | Evaluation > 30s | Return partial evaluation | `SkillTimeoutError` |

**Example Output:**
```python
EvaluationResult(
    success=True,
    overall_quality_score=0.92,
    quality_level="EXCELLENT",
    steps_completed=5,
    steps_total=5,
    completion_rate=1.0,
    completion_time_seconds=4.5,
    efficiency_score=1.1,  # Faster than estimated
    total_errors=0,
    fatal_errors=0,
    recoverable_errors=0,
    error_categories={},
    intent_satisfied=True,
    intent_alignment_score=0.95,
    unfulfilled_requirements=[],
    acceptance_criteria_met=["All tasks created", "Dependencies resolved"],
    acceptance_criteria_failed=[],
    acceptance_rate=1.0,
    recommended_action="PROCEED",
    human_readable_report="""
    Execution Summary:
    - Status: SUCCESS
    - Steps completed: 5/5 (100%)
    - Time taken: 4.5s (estimated: 5.0s)
    - Errors: 0

    Quality Assessment:
    - Overall score: 0.92/1.0 (EXCELLENT)
    - Intent alignment: 95%
    - Acceptance criteria: 100% met

    Recommendation: Proceed with confidence
    """,
    summary="All 5 tasks completed successfully in 4.5 seconds with no errors"
)
```

---

## Skill Composition Examples

### Example 1: Intent Clarification Pipeline

```python
# ClarifierAgent using multiple skills
clarifier = ClarifierAgent()

# Step 1: Analyze intent
intent_result = IntentAnalysisSkill.execute(
    user_input="organize my tasks for today",
    conversation_history=history
)

# Step 2: Detect ambiguity
ambiguity_result = AmbiguityDetectionSkill.execute(
    text=intent_result.entities,
    conversation_history=history
)

# Step 3: Generate clarification if needed
if ambiguity_result.has_ambiguity:
    questions = ambiguity_result.clarification_questions
    # Present to user, collect responses
    clarifications = collect_user_responses(questions)

    # Re-analyze with clarifications
    intent_result = IntentAnalysisSkill.execute(
        user_input=clarified_input,
        conversation_history=updated_history
    )
```

### Example 2: Plan Generation Pipeline

```python
# PlannerAgent using multiple skills
planner = PlannerAgent()

# Step 1: Get clarified intent
intent = context.intent

# Step 2: Decompose requirements
decomposition_result = TaskDecompositionSkill.execute(
    requirements=extract_requirements(intent),
    target_operations=PHASE1_COMMANDS
)

# Step 3: Validate plan
validation_result = PlanValidationSkill.execute(
    plan=ExecutionPlan(steps=decomposition_result.steps),
    phase1_schema=PHASE1_SCHEMA
)

# Step 4: Handle validation result
if validation_result.status == "FAIL":
    # Replan or request constraints
    pass
elif validation_result.status == "WARN":
    # Present warnings, ask user to proceed
    pass
```

### Example 3: Execution Evaluation Pipeline

```python
# ExecutorAgent using ResultEvaluationSkill
executor = ExecutorAgent()

# Step 1: Execute plan
execution_result = execute_plan(plan)

# Step 2: Evaluate results
evaluation_result = ResultEvaluationSkill.execute(
    execution_result=execution_result,
    original_intent=context.intent,
    specification=context.specification
)

# Step 3: Determine next action
if evaluation_result.recommended_action == "PROCEED":
    print(evaluation_result.human_readable_report)
elif evaluation_result.recommended_action == "RETRY":
    # Retry with suggestions
    retry_plan = improve_plan(plan, evaluation_result.retry_suggestions)
elif evaluation_result.recommended_action == "FALLBACK":
    # Fallback to Phase 1 direct execution
    pass
```

---

## Skill Implementation Requirements

### Statelessness

All skills MUST be stateless:
- No instance variables storing state between invocations
- All state provided via `context` or `**kwargs`
- Return state updates via `SkillOutput.state_updates`

**Example - Stateless Implementation:**
```python
# ✅ CORRECT: Stateless
class IntentAnalysisSkill(Skill):
    def execute(self, context, user_input: str, **kwargs) -> IntentAnalysisResult:
        # All inputs provided as parameters
        return IntentAnalysisResult(...)

# ❌ INCORRECT: Stateful
class IntentAnalysisSkill(Skill):
    def __init__(self):
        self.last_intent = None  # STATE - NOT ALLOWED

    def execute(self, context, user_input: str, **kwargs) -> IntentAnalysisResult:
        self.last_intent = user_input  # MUTATING STATE - NOT ALLOWED
        return IntentAnalysisResult(...)
```

### Domain-Agnosticism

All skills MUST NOT contain domain-specific logic:
- No hardcoded todo-specific rules (use domain_context parameter)
- No assumption about specific task types
- Work across ORGANIZE, PRIORITIZE, PLAN, QUERY intents

**Example - Domain-Agnostic Implementation:**
```python
# ✅ CORRECT: Uses domain_context
class TaskDecompositionSkill(Skill):
    def execute(self, context, requirements: List[str],
                target_operations: List[str],
                domain_context: Dict[str, Any] = None,
                **kwargs):
        # Use provided domain context
        allowed_ops = target_operations
        # Generic decomposition logic
        return DecompositionResult(...)

# ❌ INCORRECT: Hardcoded domain logic
class TaskDecompositionSkill(Skill):
    def execute(self, context, requirements: List[str], **kwargs):
        # Hardcoded todo-specific logic
        if "todo" in req:
            return TodoDecomposition(...)  # NOT ALLOWED
```

### Reusability

Skills MUST be reusable across agents:
- Clear, single responsibility
- Output format compatible as input to other skills
- No dependency on specific agent workflows

**Example - Reusable Skill:**
```python
# Reusable by ClarifierAgent AND PlannerAgent
class AmbiguityDetectionSkill(Skill):
    def execute(self, context, text: str, **kwargs) -> AmbiguityReport:
        # Single responsibility: detect ambiguity
        # Output compatible with many uses
        return AmbiguityReport(...)
```

---

## Testing Requirements

### Unit Tests

Each skill MUST have comprehensive unit tests:

```python
# Example test structure
class TestIntentAnalysisSkill:
    def test_classifies_organize_intent(self):
        result = IntentAnalysisSkill.execute(
            user_input="organize my tasks"
        )
        assert result.intent_type == IntentType.ORGANIZE

    def test_extracts_entities(self):
        result = IntentAnalysisSkill.execute(
            user_input="add task: review PR with priority high"
        )
        assert len(result.entities) > 0
        task_entity = [e for e in result.entities if e.entity_type == "TASK"][0]
        assert "review PR" in task_entity.value

    def test_calculates_confidence(self):
        result = IntentAnalysisSkill.execute(
            user_input="organize tasks"
        )
        assert 0.0 <= result.confidence <= 1.0

    def test_handles_empty_input(self):
        with pytest.raises(SkillValidationError):
            IntentAnalysisSkill.execute(user_input="")

    def test_handles_timeout(self):
        with mock_timeout():
            with pytest.raises(SkillTimeoutError):
                IntentAnalysisSkill.execute(user_input="x"*10000)
```

### Integration Tests

Test skill composition in agent workflows:

```python
class TestClarifierAgentWorkflow:
    def test_ambiguous_intent_clarification(self):
        # Test IntentAnalysisSkill + AmbiguityDetectionSkill
        input = "organize it"
        intent_result = IntentAnalysisSkill.execute(user_input=input)
        ambiguity_result = AmbiguityDetectionSkill.execute(text=intent_result.description)
        assert ambiguity_result.has_ambiguity is True
        assert "ambiguous_pronoun" in [a.type for a in ambiguity_result.ambiguities]

    def test_plan_generation_and_validation(self):
        # Test TaskDecompositionSkill + PlanValidationSkill
        requirements = ["Create task: A", "Create task: B"]
        decomposition_result = TaskDecompositionSkill.execute(
            requirements=requirements,
            target_operations=["add", "list"]
        )
        validation_result = PlanValidationSkill.execute(
            plan=ExecutionPlan(steps=decomposition_result.steps),
            phase1_schema=PHASE1_SCHEMA
        )
        assert validation_result.status in ["PASS", "WARN"]
```

---

## References

- **Agent Specification**: `specs/007-phase2-intelligence-model/agents-spec.md`
- **ADR-004**: Phase 2 Intelligence Integration Architecture
- **Skill Interface**: `src/intelligence/skills/skill_interface.py`
- **Existing Skills**: `src/intelligence/sdd/skills/`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
