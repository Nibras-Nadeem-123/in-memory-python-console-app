# Reusable Skill Modules Specification

**Feature Branch**: `feat/reusable-skills`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define reusable skill modules..."

## User Scenarios & Testing

### User Story 1 - Intent Parsing (Priority: P1)

As a user, I want my natural language input to be parsed into structured intent so that the system can understand and act on it.

**Why this priority**: Intent parsing is the entry point for all interactions. Without it, the system cannot understand user requests.

**Independent Test**: Can be tested by providing text inputs and verifying structured intent output.

**Acceptance Scenarios**:

1. **Given** text "create a user authentication module", **When** parsed, **Then** action="create", target="user authentication module"
2. **Given** text "show me the current architecture", **When** parsed, **Then** action="show", target="architecture"
3. **Given** ambiguous text "fix the bug", **When** parsed, **Then** ambiguity is flagged with options

---

### User Story 2 - Specification Building (Priority: P1)

As a user, I want my intent to be converted into a formal specification so that the system can plan and execute systematically.

**Why this priority**: Specifications bridge intent and execution, providing a contract for downstream processing.

**Independent Test**: Can be tested by providing intent and verifying specification completeness.

**Acceptance Scenarios**:

1. **Given** intent with all required fields, **When** specification built, **Then** output includes all requirement fields
2. **Given** incomplete intent, **When** specification built, **Then** missing fields are marked for clarification
3. **Given** conflicting requirements, **When** specification built, **Then** conflicts are identified

---

### User Story 3 - Task Decomposition (Priority: P1)

As a user, I want complex specifications broken into actionable tasks so that I can track progress and execute systematically.

**Why this priority**: Decomposition enables parallel work and progress tracking.

**Independent Test**: Can be tested by providing specifications and verifying task breakdown.

**Acceptance Scenarios**:

1. **Given** specification with 3 requirements, **When** decomposed, **Then** at least 3 tasks are generated
2. **Given** dependent tasks, **When** ordered, **Then** dependencies are correctly identified
3. **Given** specification with gaps, **When** decomposed, **Then** gaps are flagged

---

### User Story 4 - Constraint Validation (Priority: P1)

As a user, I want my specifications validated against constraints so that errors are caught early.

**Why this priority**: Early validation prevents wasted effort on invalid specifications.

**Independent Test**: Can be tested by providing valid/invalid specs and verifying validation results.

**Acceptance Scenarios**:

1. **Given** spec satisfying all constraints, **When** validated, **Then** result is valid
2. **Given** spec violating constraints, **When** validated, **Then** violations are reported
3. **Given** conflicting constraints, **When** validated, **Then** conflict is identified

---

### User Story 5 - State Tracking (Priority: P2)

As a user, I want the system to track execution state so that I can resume or audit progress.

**Why this priority**: State tracking enables resumability and auditability.

**Independent Test**: Can be tested by simulating execution and verifying state updates.

**Acceptance Scenarios**:

1. **Given** initial state, **When** transition executed, **Then** state is updated correctly
2. **Given** invalid transition, **When** attempted, **Then** transition is rejected
3. **Given** multiple sessions, **When** states tracked, **Then** each session has independent state

---

### User Story 6 - Feedback Synthesis (Priority: P2)

As a user, I want feedback synthesized from multiple sources so that I understand overall quality and issues.

**Why this priority**: Synthesized feedback provides actionable insights from complex data.

**Independent Test**: Can be tested by providing feedback items and verifying synthesis.

**Acceptance Scenarios**:

1. **Given** 5 findings, **When** synthesized, **Then** summary captures all themes
2. **Given** contradictory feedback, **When** synthesized, **Then** conflict is highlighted
3. **Given** empty feedback, **When** synthesized, **Then** empty result is returned

---

## Requirements

### Functional Requirements

- **FR-SKL-001**: System MUST provide IntentParser skill for natural language parsing
- **FR-SKL-002**: System MUST provide SpecBuilder skill for intent-to-spec conversion
- **FR-SKL-003**: System MUST provide TaskDecomposer skill for specification breakdown
- **FR-SKL-004**: System MUST provide ConstraintValidator skill for constraint checking
- **FR-SKL-005**: System MUST provide StateTracker skill for execution state management
- **FR-SKL-006**: System MUST provide FeedbackSynthesizer skill for multi-source synthesis
- **FR-SKL-007**: Each skill MUST define input format, output format, validation rules, failure behavior
- **FR-SKL-008**: Each skill MUST be independently testable
- **FR-SKL-009**: Each skill MUST be composable with other skills

### Non-Functional Requirements

- **NFR-SKL-001**: Each skill MUST respond within 50ms for typical inputs
- **NFR-SKL-002**: Each skill MUST handle errors gracefully
- **NFR-SKL-003**: Each skill output MUST be deterministic

### Key Entities

- **Skill**: Reusable capability module
- **InputFormat**: Schema for skill inputs
- **OutputFormat**: Schema for skill outputs
- **ValidationRules**: Rules for input/output validation
- **FailureBehavior**: How skill handles failure

---

## 1. IntentParser Skill

### Purpose
Parses natural language text into structured intent.

### Input Format

```python
@dataclass
class IntentParserInput:
    """Input to IntentParser skill."""
    text: str
    context: Optional[Dict[str, Any]] = None
    language: str = "en"
    confidence_threshold: float = 0.7

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.text or not self.text.strip():
            return False, "Text cannot be empty"
        if len(self.text) > 10000:
            return False, "Text exceeds maximum length"
        if self.confidence_threshold < 0 or self.confidence_threshold > 1:
            return False, "Confidence threshold must be 0-1"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class IntentEntity:
    """Extracted entity from text."""
    type: str
    value: str
    position: Tuple[int, int]  # start, end
    confidence: float


@dataclass
class IntentConstraint:
    """Extracted constraint from text."""
    dimension: str
    operator: str  # "equals", "greater_than", "contains", etc.
    value: Any


@dataclass
class IntentParserOutput:
    """Output from IntentParser skill."""
    action: str  # Primary action (create, read, update, delete, show, etc.)
    target: str  # Primary target (noun/phrase)
    entities: List[IntentEntity]  # Extracted entities
    constraints: List[IntentConstraint]  # Extracted constraints
    confidence: float  # Overall confidence 0-1
    ambiguity_detected: bool
    possible_interpretations: List[Dict[str, Any]]  # If ambiguous
    raw_intent: str  # Original text
    tokens: List[str]  # Tokenized words

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if not self.action:
            return False, "Action cannot be empty"
        if not self.target:
            return False, "Target cannot be empty"
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        if self.ambiguity_detected and not self.possible_interpretations:
            return False, "Ambiguity detected but no interpretations provided"
        return True, "Valid"
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| text_not_empty | text.strip() | "Text cannot be empty" |
| text_length_max | len(text) <= 10000 | "Text exceeds maximum length" |
| confidence_threshold_valid | 0 <= threshold <= 1 | "Confidence threshold must be 0-1" |
| action_required | action is not empty | "Action cannot be empty" |
| target_required | target is not empty | "Target cannot be empty" |
| confidence_range | 0 <= confidence <= 1 | "Confidence must be 0-1" |
| ambiguity_requires_options | ambiguity_detected → options | "Ambiguity requires interpretations" |

### Failure Behavior

```python
class IntentParserFailure(Enum):
    EMPTY_INPUT = "empty_input"
    TEXT_TOO_LONG = "text_too_long"
    UNKNOWN_ACTION = "unknown_action"
    PARSING_FAILED = "parsing_failed"
    AMBIGUITY_UNRESOLVED = "ambiguity_unresolved"


class IntentParserResult:
    def __init__(self, success: bool, output: Optional[IntentParserOutput], failure: Optional[IntentParserFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message

    @staticmethod
    def from_failure(failure: IntentParserFailure, message: str) -> "IntentParserResult":
        return IntentParserResult(success=False, output=None, failure=failure, error_message=message)
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| EMPTY_INPUT | text is empty | Return failure, no processing | Request non-empty input |
| TEXT_TOO_LONG | len(text) > 10000 | Truncate or reject | Reject with max length |
| UNKNOWN_ACTION | No action detected | Return with low confidence | Request clarification |
| PARSING_FAILED | Parsing exception | Return failure with error | Log error, request retry |
| AMBIGUITY_UNRESOLVED | Multiple options, no selection | Return all options | Present options to user |

---

## 2. SpecBuilder Skill

### Purpose
Converts structured intent into formal specification.

### Input Format

```python
@dataclass
class SpecBuilderInput:
    """Input to SpecBuilder skill."""
    intent: IntentParserOutput  # From IntentParser
    context: Optional[Dict[str, Any]] = None
    spec_template: Optional[str] = None  # Template name or inline
    required_fields: List[str] = None  # Fields that must be present
    optional_fields: List[str] = None  # Fields that can be added

    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = ["title", "description", "requirements"]
        if self.optional_fields is None:
            self.optional_fields = ["acceptance_criteria", "dependencies", "notes"]

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.intent:
            return False, "Intent cannot be empty"
        is_valid, error = self.intent.validate()
        if not is_valid:
            return False, f"Invalid intent: {error}"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class SpecRequirement:
    """Individual requirement in specification."""
    req_id: str
    description: str
    priority: str  # "MUST", "SHOULD", "COULD"
    validation_method: str  # How to validate this requirement


@dataclass
class SpecBuilderOutput:
    """Output from SpecBuilder skill."""
    spec_id: str  # Unique identifier
    title: str
    description: str
    requirements: List[SpecRequirement]
    acceptance_criteria: List[str]
    constraints: List[str]  # From intent
    dependencies: List[str]  # Identified dependencies
    notes: List[str]  # Additional notes
    missing_fields: List[str]  # Fields that need clarification
    completeness_score: float  # 0-1 how complete
    consistency_warnings: List[str]  # Potential issues
    created_at: str  # ISO timestamp
    version: str = "1.0.0"

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if not self.title:
            return False, "Title cannot be empty"
        if not self.description:
            return False, "Description cannot be empty"
        if self.completeness_score < 0 or self.completeness_score > 1:
            return False, "Completeness score must be 0-1"
        return True, "Valid"
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| intent_required | intent is not None | "Intent cannot be empty" |
| intent_valid | intent.validate() passes | "Invalid intent: {error}" |
| title_required | title is not empty | "Title cannot be empty" |
| description_required | description is not empty | "Description cannot be empty" |
| completeness_score_range | 0 <= score <= 1 | "Completeness score must be 0-1" |
| requirements_have_ids | each req has req_id | "All requirements must have IDs" |

### Failure Behavior

```python
class SpecBuilderFailure(Enum):
    INVALID_INTENT = "invalid_intent"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INCONSISTENT_SPEC = "inconsistent_spec"
    GENERATION_FAILED = "generation_failed"
    TEMPLATE_ERROR = "template_error"


class SpecBuilderResult:
    def __init__(self, success: bool, output: Optional[SpecBuilderOutput], failure: Optional[SpecBuilderFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message

    @staticmethod
    def from_failure(failure: SpecBuilderFailure, message: str) -> "SpecBuilderResult":
        return SpecBuilderResult(success=False, output=None, failure=failure, error_message=message)
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| INVALID_INTENT | intent validation fails | Return failure, don't generate | Fix intent first |
| MISSING_REQUIRED_FIELD | required field missing | Add to missing_fields list | Request field value |
| INCONSISTENT_SPEC | contradictions detected | Add warnings, continue | Review warnings |
| GENERATION_FAILED | Exception during generation | Return failure with error | Retry or manual |
| TEMPLATE_ERROR | Template invalid/missing | Return failure | Use default template |

---

## 3. TaskDecomposer Skill

### Purpose
Breaks specifications into atomic, ordered tasks.

### Input Format

```python
@dataclass
class TaskDecomposerInput:
    """Input to TaskDecomposer skill."""
    specification: SpecBuilderOutput  # From SpecBuilder
    context: Optional[Dict[str, Any]] = None
    decomposition_strategy: str = "sequential"  # "sequential", "parallel", "hybrid"
    max_depth: int = 3  # Maximum decomposition depth
    min_task_size: str = "medium"  # "small", "medium", "large"
    include_validation: bool = True  # Include validation tasks

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.specification:
            return False, "Specification cannot be empty"
        is_valid, error = self.specification.validate()
        if not is_valid:
            return False, f"Invalid specification: {error}"
        if self.max_depth < 1 or self.max_depth > 10:
            return False, "Max depth must be 1-10"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class TaskStep:
    """Individual step within a task."""
    step_id: str
    description: str
    command_template: Optional[str] = None
    validation_criteria: List[str] = None
    estimated_duration: Optional[str] = None


@dataclass
class TaskDependency:
    """Task dependency."""
    task_id: str
    depends_on: List[str]  # Task IDs this depends on
    dependency_type: str = "finish_to_start"  # finish_to_start, start_to_start, etc.


@dataclass
class TaskDecomposerOutput:
    """Output from TaskDecomposer skill."""
    tasks: List[Dict[str, Any]]  # Each task with id, name, description, steps, etc.
    dependencies: List[TaskDependency]
    execution_order: List[str]  # Task IDs in execution order
    critical_path: List[str]  # Task IDs on critical path
    parallel_groups: List[List[str]]  # Tasks that can run in parallel
    total_tasks: int
    total_estimated_duration: Optional[str]
    decomposition_depth: int  # Actual depth achieved
    gaps_identified: List[str]  # Requirements not covered
    validation_tasks_included: bool

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if not self.tasks:
            return False, "At least one task must be generated"
        if len(self.execution_order) != self.total_tasks:
            return False, "Execution order must include all tasks"
        # Check no circular dependencies
        if self._has_circular_dependency():
            return False, "Circular dependency detected"
        return True, "Valid"

    def _has_circular_dependency(self) -> bool:
        """Check for circular dependencies."""
        # Build dependency graph
        graph = {t["task_id"]: set() for t in self.tasks}
        for dep in self.dependencies:
            graph[dep.task_id].update(dep.depends_on)
        # Check for cycles using DFS
        visited = set()
        recursion_stack = set()
        for node in graph:
            if node not in visited:
                if self._detect_cycle(node, graph, visited, recursion_stack):
                    return True
        return False
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| specification_required | specification is not None | "Specification cannot be empty" |
| specification_valid | spec.validate() passes | "Invalid specification: {error}" |
| max_depth_valid | 1 <= max_depth <= 10 | "Max depth must be 1-10" |
| at_least_one_task | len(tasks) >= 1 | "At least one task must be generated" |
| execution_order_complete | len(execution_order) == total_tasks | "Execution order must include all tasks" |
| no_circular_dependencies | No cycles in dependency graph | "Circular dependency detected" |
| all_deps_valid | All dependency refs exist | "Invalid dependency reference" |

### Failure Behavior

```python
class TaskDecomposerFailure(Enum):
    INVALID_SPECIFICATION = "invalid_specification"
    DECOMPOSITION_FAILED = "decomposition_failed"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MAX_DEPTH_EXCEEDED = "max_depth_exceeded"
    NO_VALID_TASKS = "no_valid_tasks"


class TaskDecomposerResult:
    def __init__(self, success: bool, output: Optional[TaskDecomposerOutput], failure: Optional[TaskDecomposerFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| INVALID_SPECIFICATION | spec validation fails | Return failure | Fix specification |
| DECOMPOSITION_FAILED | Exception during decomposition | Return failure with error | Retry with different strategy |
| CIRCULAR_DEPENDENCY | Cycle detected | Break cycle, warn user | Review dependencies |
| MAX_DEPTH_EXCEEDED | Can't decompose within depth | Return partial decomposition | Increase max_depth |
| NO_VALID_TASKS | No tasks generated | Return failure | Check specification completeness |

---

## 4. ConstraintValidator Skill

### Purpose
Validates specifications and plans against constraints.

### Input Format

```python
@dataclass
class ConstraintValidatorInput:
    """Input to ConstraintValidator skill."""
    target: Any  # Specification, plan, or other object to validate
    target_type: str  # "specification", "plan", "task", "intent"
    constraints: List[Dict[str, Any]]  # Constraints to validate against
    context: Optional[Dict[str, Any]] = None
    strict_mode: bool = True  # Fail on warnings if True

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.target:
            return False, "Target cannot be empty"
        if not self.target_type:
            return False, "Target type cannot be empty"
        if not self.constraints:
            return False, "At least one constraint required"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class ConstraintViolation:
    """Individual constraint violation."""
    constraint_id: str
    constraint_description: str
    severity: str  # "blocking", "warning", "info"
    current_value: Any
    expected_value: Any
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class ConstraintValidatorOutput:
    """Output from ConstraintValidator skill."""
    is_valid: bool  # Overall validity
    violations: List[ConstraintViolation]
    blocking_count: int
    warning_count: int
    info_count: int
    validated_constraints: List[str]  # IDs of constraints checked
    skipped_constraints: List[str]  # IDs of constraints skipped
    validation_summary: str  # Human-readable summary
    confidence: float  # Confidence in validation result

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if not isinstance(self.is_valid, bool):
            return False, "is_valid must be boolean"
        if self.blocking_count < 0:
            return False, "Blocking count cannot be negative"
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        return True, "Valid"
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| target_required | target is not None | "Target cannot be empty" |
| target_type_required | target_type is not empty | "Target type cannot be empty" |
| constraints_required | len(constraints) >= 1 | "At least one constraint required" |
| is_valid_boolean | isinstance(is_valid, bool) | "is_valid must be boolean" |
| confidence_range | 0 <= confidence <= 1 | "Confidence must be 0-1" |
| blocking_count_valid | blocking_count >= 0 | "Blocking count cannot be negative" |

### Failure Behavior

```python
class ConstraintValidatorFailure(Enum):
    INVALID_TARGET = "invalid_target"
    INVALID_CONSTRAINT = "invalid_constraint"
    VALIDATION_FAILED = "validation_failed"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    EVALUATION_TIMEOUT = "evaluation_timeout"


class ConstraintValidatorResult:
    def __init__(self, success: bool, output: Optional[ConstraintValidatorOutput], failure: Optional[ConstraintValidatorFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| INVALID_TARGET | target validation fails | Return failure | Fix target |
| INVALID_CONSTRAINT | constraint schema invalid | Skip constraint, warn | Fix constraint |
| VALIDATION_FAILED | Exception during validation | Return failure with error | Retry |
| CONSTRAINT_CONFLICT | Constraints contradict | Report conflict, continue | Resolve conflict |
| EVALUATION_TIMEOUT | Constraint takes too long | Skip, report timeout | Increase timeout |

---

## 5. StateTracker Skill

### Purpose
Tracks execution state and state transitions.

### Input Format

```python
@dataclass
class StateTrackerInput:
    """Input to StateTracker skill."""
    operation: str  # "get", "set", "transition", "snapshot", "restore"
    session_id: str
    state_key: Optional[str] = None  # For get/set
    state_value: Optional[Any] = None  # For set
    transition: Optional[Dict[str, Any]] = None  # For transition
    snapshot_id: Optional[str] = None  # For snapshot/restore
    context: Optional[Dict[str, Any]] = None

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.session_id:
            return False, "Session ID cannot be empty"
        valid_operations = ["get", "set", "transition", "snapshot", "restore"]
        if self.operation not in valid_operations:
            return False, f"Operation must be one of {valid_operations}"
        if self.operation in ["get", "set"] and not self.state_key:
            return False, "state_key required for get/set operations"
        if self.operation == "set" and self.state_value is None:
            return False, "state_value required for set operation"
        if self.operation == "transition" and not self.transition:
            return False, "transition required for transition operation"
        if self.operation == "restore" and not self.snapshot_id:
            return False, "snapshot_id required for restore operation"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class StateTransition:
    """State transition record."""
    from_state: str
    to_state: str
    trigger: str
    timestamp: str
    succeeded: bool
    error: Optional[str] = None


@dataclass
class StateTrackerOutput:
    """Output from StateTracker skill."""
    operation: str
    success: bool
    current_state: Optional[Any] = None  # For get
    previous_value: Optional[Any] = None  # For set
    transition_record: Optional[StateTransition] = None  # For transition
    snapshot_id: Optional[str] = None  # For snapshot
    restored_values: Optional[Dict[str, Any]] = None  # For restore
    state_history: List[StateTransition] = None  # History if requested
    error_message: Optional[str] = None

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if not isinstance(self.success, bool):
            return False, "success must be boolean"
        if self.operation not in ["get", "set", "transition", "snapshot", "restore"]:
            return False, f"Invalid operation: {self.operation}"
        return True, "Valid"
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| session_id_required | session_id is not empty | "Session ID cannot be empty" |
| operation_valid | operation in valid_ops | "Invalid operation: {operation}" |
| state_key_required | For get/set, state_key present | "state_key required for get/set" |
| state_value_required | For set, state_value present | "state_value required for set" |
| transition_required | For transition, transition present | "transition required" |
| snapshot_id_required | For restore, snapshot_id present | "snapshot_id required" |
| success_boolean | isinstance(success, bool) | "success must be boolean" |

### Failure Behavior

```python
class StateTrackerFailure(Enum):
    INVALID_SESSION = "invalid_session"
    INVALID_OPERATION = "invalid_operation"
    STATE_KEY_NOT_FOUND = "state_key_not_found"
    INVALID_TRANSITION = "invalid_transition"
    SNAPSHOT_NOT_FOUND = "snapshot_not_found"
    CONCURRENT_MODIFICATION = "concurrent_modification"


class StateTrackerResult:
    def __init__(self, success: bool, output: Optional[StateTrackerOutput], failure: Optional[StateTrackerFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| INVALID_SESSION | session_id empty/invalid | Return failure | Provide valid session |
| INVALID_OPERATION | Unknown operation | Return failure | Use valid operation |
| STATE_KEY_NOT_FOUND | Key doesn't exist | Return None/missing | Create key first |
| INVALID_TRANSITION | Transition not allowed | Reject transition | Check valid transitions |
| SNAPSHOT_NOT_FOUND | Snapshot doesn't exist | Return failure | Use existing snapshot |
| CONCURRENT_MODIFICATION | Race condition detected | Retry or fail | Retry with lock |

---

## 6. FeedbackSynthesizer Skill

### Purpose
Synthesizes feedback from multiple sources into coherent summary.

### Input Format

```python
@dataclass
class FeedbackItem:
    """Individual feedback item."""
    id: str
    source: str  # "reviewer", "validator", "executor", "user"
    category: str  # "quality", "error", "suggestion", "warning"
    severity: str  # "critical", "major", "minor", "info"
    title: str
    description: str
    evidence: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FeedbackSynthesizerInput:
    """Input to FeedbackSynthesizer skill."""
    items: List[FeedbackItem]
    synthesis_type: str = "summary"  # "summary", "actionable", "prioritized"
    group_by: str = "category"  # "category", "severity", "source"
    include_suggestions: bool = True
    max_suggestions: int = 10
    context: Optional[Dict[str, Any]] = None

    def validate(self) -> tuple[bool, str]:
        """Validate input requirements."""
        if not self.items:
            return False, "At least one feedback item required"
        if self.max_suggestions < 1:
            return False, "max_suggestions must be >= 1"
        valid_types = ["summary", "actionable", "prioritized"]
        if self.synthesis_type not in valid_types:
            return False, f"synthesis_type must be one of {valid_types}"
        valid_groupings = ["category", "severity", "source"]
        if self.group_by not in valid_groupings:
            return False, f"group_by must be one of {valid_groupings}"
        return True, "Valid"
```

### Output Format

```python
@dataclass
class FeedbackGroup:
    """Group of related feedback items."""
    group_key: str  # Category, severity, or source
    item_count: int
    items: List[FeedbackItem]
    synthesized_summary: str


@dataclass
class ActionableRecommendation:
    """Actionable recommendation from feedback."""
    title: str
    description: str
    priority: int  # 1 = highest
    effort: str  # "low", "medium", "high"
    impact: str  # "low", "medium", "high"
    affected_items: List[str]  # IDs of feedback items


@dataclass
class FeedbackSynthesizerOutput:
    """Output from FeedbackSynthesizer skill."""
    total_items: int
    groups: List[FeedbackGroup]  # Grouped feedback
    recommendations: List[ActionableRecommendation]  # Prioritized actions
    summary: str  # Executive summary
    critical_issues: List[str]  # IDs of critical issues
    quick_wins: List[str]  # Recommendations with low effort/high impact
    patterns_identified: List[str]  # Recurring themes
    contradictions: List[Dict[str, Any]]  # Contradictory feedback
    confidence: float  # Confidence in synthesis

    def validate(self) -> tuple[bool, str]:
        """Validate output requirements."""
        if self.total_items != len(self.groups[0].items) if self.groups else self.total_items != 0:
            # Note: this is approximate, actual count is across all groups
            pass
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        return True, "Valid"
```

### Validation Rules

| Rule | Condition | Error Message |
|------|-----------|---------------|
| items_required | len(items) >= 1 | "At least one feedback item required" |
| max_suggestions_positive | max_suggestions >= 1 | "max_suggestions must be >= 1" |
| synthesis_type_valid | in ["summary", "actionable", "prioritized"] | "Invalid synthesis_type" |
| group_by_valid | in ["category", "severity", "source"] | "Invalid group_by" |
| confidence_range | 0 <= confidence <= 1 | "Confidence must be 0-1" |

### Failure Behavior

```python
class FeedbackSynthesizerFailure(Enum):
    NO_FEEDBACK_ITEMS = "no_feedback_items"
    INVALID_SYNTHESIS_TYPE = "invalid_synthesis_type"
    SYNTHESIS_FAILED = "synthesis_failed"
    CONTRADICTION_DETECTED = "contradiction_detected"
    ITEM_NOT_FOUND = "item_not_found"


class FeedbackSynthesizerResult:
    def __init__(self, success: bool, output: Optional[FeedbackSynthesizerOutput], failure: Optional[FeedbackSynthesizerFailure], error_message: str):
        self.success = success
        self.output = output
        self.failure = failure
        self.error_message = error_message
```

**Failure Modes**:

| Failure | Trigger | Behavior | Recovery |
|---------|---------|----------|----------|
| NO_FEEDBACK_ITEMS | items list empty | Return empty synthesis | Provide items |
| INVALID_SYNTHESIS_TYPE | Unknown type | Return failure | Use valid type |
| SYNTHESIS_FAILED | Exception during synthesis | Return failure with error | Retry |
| CONTRADICTION_DETECTED | Contradictory feedback | Mark contradictions, continue | Review contradictions |
| ITEM_NOT_FOUND | Referenced item missing | Skip reference, warn | Fix reference |

---

## Skill Composition

### Composition Chain

```
User Input
    ↓
IntentParser → IntentParserOutput
    ↓
SpecBuilder → SpecBuilderOutput
    ↓
ConstraintValidator → ValidationResult
    ↓ (if valid)
TaskDecomposer → TaskList
    ↓
StateTracker → ExecutionState
    ↓
Executor → Results
    ↓
FeedbackSynthesizer → SynthesizedFeedback
```

### Skill Registry

```python
class SkillRegistry:
    """Registry for reusable skills."""

    def __init__(self):
        self._skills: Dict[str, Any] = {}

    def register(self, name: str, skill: Any) -> bool:
        """Register a skill."""
        self._skills[name] = skill
        return True

    def get(self, name: str) -> Optional[Any]:
        """Get a skill by name."""
        return self._skills.get(name)

    def list_all(self) -> List[str]:
        """List all registered skills."""
        return list(self._skills.keys())

    def compose(self, chain: List[str], input: Any) -> Any:
        """Compose skills into a chain."""
        result = input
        for skill_name in chain:
            skill = self.get(skill_name)
            if skill:
                result = skill.execute(result)
        return result
```

---

## Summary

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| **IntentParser** | Parse NL to intent | Raw text | Structured intent |
| **SpecBuilder** | Intent to spec | Intent | Formal specification |
| **TaskDecomposer** | Spec to tasks | Specification | Task list with dependencies |
| **ConstraintValidator** | Check constraints | Target + constraints | Validation result |
| **StateTracker** | Track execution state | Operation + session | State changes |
| **FeedbackSynthesizer** | Synthesize feedback | Feedback items | Synthesized summary |

**PHR**: `history/prompts/reusable-skills/001-define-reusable-skills-modules.spec.prompt.md`
