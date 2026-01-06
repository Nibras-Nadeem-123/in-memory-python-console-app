"""Data models for Phase 2 intelligence system.

Defines core data structures for intent parsing, clarification,
planning, and execution in the Phase 2 intelligence system.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class IntentType(str, Enum):
    """Intent classification for Phase 2 reasoning."""
    ORGANIZE = "organize"
    PRIORITIZE = "prioritize"
    PLAN = "plan"
    QUERY = "query"


@dataclass
class Entity:
    """Extracted entity from natural language."""
    entity_type: str  # TASK, PRIORITY, TIMEFRAME, CONSTRAINT
    value: str  # Extracted value
    confidence: float = 0.0  # Extraction confidence
    position: tuple[int, int] = field(default_factory=tuple)  # Start/end position


@dataclass
class Ambiguity:
    """Detected ambiguity requiring clarification."""
    ambiguity_id: str
    ambiguity_type: str  # ambiguous_pronoun, vague_quantifier, uncertain_language, missing_info
    phrase: str  # The ambiguous phrase
    context: str  # Surrounding context
    suggestion: str  # How to resolve
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    position: tuple[int, int] = field(default_factory=tuple)  # Start/end position
    requires_clarification: bool = True  # Whether clarification is mandatory


@dataclass
class Intent:
    """Structured representation of parsed user intent for Phase 2."""
    type: IntentType
    description: str

    # Extracted entities
    parameters: Dict[str, Any] = field(default_factory=dict)
    # - tasks: List[str] - Task descriptions
    # - priorities: List[str] - Priority levels
    # - timeframes: List[str] - "today", "this week", etc.
    # - constraints: List[str] - Restrictions/requirements

    # Ambiguity tracking
    ambiguities: List[Ambiguity] = field(default_factory=list)
    clarifications: Dict[str, str] = field(default_factory=dict)  # field -> resolved value

    # Quality metrics
    confidence: float = 1.0  # 0.0 - 1.0
    completeness: float = 1.0  # 0.0 - 1.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClarificationRequest:
    """Request for user input to resolve ambiguity."""
    question_id: str
    question: str
    field: str  # Which intent field needs clarification
    options: Optional[List[str]] = None  # Suggested answers
    response: Optional[str] = None  # User's answer
    timestamp: str = ""


@dataclass
class Requirement:
    """Functional requirement from specification."""
    id: str  # FR-001, FR-002, etc.
    description: str
    priority: str = "P2"  # P1, P2, P3
    source: str = "derived"  # How requirement was derived


@dataclass
class Specification:
    """Formal specification document."""
    title: str
    description: str

    # Requirements
    requirements: List[Requirement] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanStep:
    """Individual step in execution plan."""
    id: str  # Unique step identifier
    description: str  # Human-readable description

    # Execution
    command: str  # Phase 1 command to execute
    command_type: str  # ADD, LIST, COMPLETE, DELETE, UPDATE

    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # IDs of dependent steps

    # Prioritization
    priority: str = "P2"  # P1, P2, P3

    # Estimation
    estimated_seconds: float = 0.0

    # Status
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED

    # Mapping
    source_requirement: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Multi-step execution plan."""
    title: str
    description: str

    # Steps
    steps: List[PlanStep] = field(default_factory=list)

    # Analysis
    total_estimated_seconds: float = 0.0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    dependencies_count: int = 0

    # Validation
    validation_status: str = "PENDING"  # PENDING, PASS, WARN, FAIL


@dataclass
class ValidationIssue:
    """Issue found during validation."""
    issue_id: str
    check_id: str
    issue_type: str  # MISSING_STEP, CIRCULAR_DEPENDENCY, INVALID_COMMAND, RISK
    severity: str  # LOW, MEDIUM, HIGH
    description: str
    location: str  # Where issue occurs
    suggestion: str
    block_execution: bool = False


@dataclass
class ValidationReport:
    """Result of plan validation."""
    status: str  # PASS, WARN, FAIL
    overall_score: float  # 0.0 - 1.0
    is_executable: bool = True

    # Validation checks
    checks: List[Any] = field(default_factory=list)
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0

    # Issues
    issues: List[ValidationIssue] = field(default_factory=list)
    critical_issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)

    # Risk assessment
    risk_level: str = "LOW"
    risk_factors: List[str] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewResult:
    """Result of review process."""
    status: str  # APPROVED, MODIFIED, REJECTED, REJECTED_WITH_FEEDBACK

    # Reviewed artifacts
    specification: Optional[Specification] = None
    plan: Optional[ExecutionPlan] = None

    # User feedback
    user_feedback: Optional[str] = None

    # Modifications
    modifications: List[Any] = field(default_factory=list)

    # Validation
    validation_result: str = "PASS"  # PASS, WARN, FAIL

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionError:
    """Error during step execution."""
    error_id: str
    step_id: str
    error_type: str  # VALIDATION, EXECUTION, TIMEOUT, API_ERROR
    error_message: str
    error_code: Optional[str] = None
    fatal: bool = False
    recoverable: bool = True
    occurred_at: str = ""


@dataclass
class StepResult:
    """Result of executing a single plan step."""
    step_id: str
    status: str  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    command: str
    output: str = ""
    error: Optional[ExecutionError] = None
    started_at: str = ""
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class ExecutionResult:
    """Result of executing an execution plan."""
    status: str  # COMPLETED, PARTIAL, FAILED, CANCELLED

    # Progress
    steps_completed: int = 0
    steps_total: int = 0
    completion_percentage: float = 0.0

    # Timing
    started_at: str = ""
    completed_at: Optional[str] = None
    total_duration_seconds: float = 0.0

    # Errors
    errors: List[ExecutionError] = field(default_factory=list)
    warnings: List[Any] = field(default_factory=list)

    # Rollback
    rollback_performed: bool = False
    rollback_status: Optional[str] = None

    # Results
    step_results: Dict[str, StepResult] = field(default_factory=dict)

    # State changes
    tasks_added: int = 0
    tasks_modified: int = 0
    tasks_deleted: int = 0
    tasks_completed: int = 0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of evaluating execution against original intent."""
    success: bool
    overall_quality_score: float  # 0.0 - 1.0
    quality_level: str  # EXCELLENT, GOOD, ACCEPTABLE, POOR, FAILED

    # Completion metrics
    steps_completed: int = 0
    steps_total: int = 0
    completion_rate: float = 0.0
    completion_time_seconds: float = 0.0
    efficiency_score: float = 0.0

    # Error analysis
    total_errors: int = 0
    fatal_errors: int = 0
    recoverable_errors: int = 0
    error_categories: Dict[str, int] = field(default_factory=dict)

    # Intent alignment
    intent_satisfied: bool = False
    intent_alignment_score: float = 0.0
    unfulfilled_requirements: List[str] = field(default_factory=list)

    # Acceptance criteria
    acceptance_criteria_met: List[str] = field(default_factory=list)
    acceptance_criteria_failed: List[str] = field(default_factory=list)
    acceptance_rate: float = 0.0

    # Recommendations
    recommended_action: str = "PROCEED"  # PROCEED, RETRY, FALLBACK, MANUAL_REVIEW
    retry_probability: float = 0.0
    retry_suggestions: List[str] = field(default_factory=list)

    # Report
    human_readable_report: str = ""
    summary: str = ""

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Phase2Context:
    """Long-lived reasoning artifact for Phase 2 intelligence."""
    execution_id: str

    # User input
    user_input: str = ""

    # Intent parsing
    intent: Optional[Intent] = None
    clarifications: List[ClarificationRequest] = field(default_factory=list)

    # Planning artifacts
    specification: Optional[Specification] = None
    plan: Optional[ExecutionPlan] = None

    # Execution
    execution_results: Optional[ExecutionResult] = None

    # Reasoning trace
    reasoning_trace: List[Dict[str, Any]] = field(default_factory=list)

    # Workflow state
    workflow_state: str = "initialized"

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.user_input = ""
        self.intent = None
        self.clarifications = []
        self.specification = None
        self.plan = None
        self.execution_results = None
        self.reasoning_trace = []
        self.workflow_state = "initialized"
        self.metadata = {}

    def add_intent(self, intent: Intent) -> None:
        """Store parsed intent."""
        self.intent = intent
        self.metadata["intent"] = {
            "type": intent.type.value,
            "confidence": intent.confidence,
            "completeness": intent.completeness,
            "timestamp": datetime.now().isoformat()
        }

    def add_clarification(self, clarification: ClarificationRequest) -> None:
        """Add clarification request."""
        self.clarifications.append(clarification)

    def add_specification(self, specification: Specification) -> None:
        """Store generated specification."""
        self.specification = specification
        self.metadata["specification"] = {
            "title": specification.title,
            "requirements_count": len(specification.requirements),
            "timestamp": datetime.now().isoformat()
        }

    def add_plan(self, plan: ExecutionPlan) -> None:
        """Store generated plan."""
        self.plan = plan
        self.metadata["plan"] = {
            "title": plan.title,
            "steps_count": len(plan.steps),
            "estimated_duration": plan.total_estimated_seconds,
            "timestamp": datetime.now().isoformat()
        }

    def add_execution_result(self, result: ExecutionResult) -> None:
        """Store execution result."""
        self.execution_results = result
        self.metadata["execution"] = {
            "status": result.status,
            "completion_percentage": result.completion_percentage,
            "timestamp": datetime.now().isoformat()
        }

    def add_reasoning_step(
        self,
        stage: str,
        action: str,
        details: Dict[str, Any]
    ) -> None:
        """Add step to reasoning trace."""
        self.reasoning_trace.append({
            "stage": stage,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def transition_to(self, state: str) -> None:
        """Transition workflow state."""
        old_state = self.workflow_state
        self.workflow_state = state
        self.add_reasoning_step(
            stage="transition",
            action="state_change",
            details={"from": old_state, "to": state}
        )
