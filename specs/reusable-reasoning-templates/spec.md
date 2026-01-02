# Reusable Reasoning Templates Specification

**Feature Branch**: `feat/reusable-reasoning-templates`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Create reusable reasoning templates..."

## User Scenarios & Testing

### User Story 1 - Problem Understanding (Priority: P1)

As a developer, I want a structured template for understanding problems so that I can ensure I fully grasp the problem before solving it.

**Why this priority**: Understanding the problem correctly prevents wasted effort on wrong solutions.

**Independent Test**: Can be tested by applying template to problems and verifying completeness.

**Acceptance Scenarios**:

1. **Given** a problem statement, **When** Problem Understanding Template applied, **Then** output identifies stakeholders, constraints, and success criteria
2. **Given** ambiguous problem, **When** template applied, **Then** ambiguities are surfaced
3. **Given** simple problem, **When** template applied, **Then** template produces proportional output

---

### User Story 2 - Planning (Priority: P1)

As a developer, I want a structured planning template so that I can create comprehensive, actionable plans.

**Why this priority**: Good planning leads to successful execution and fewer surprises.

**Independent Test**: Can be tested by creating plans and verifying all required elements are present.

**Acceptance Scenarios**:

1. **Given** understood problem, **When** Planning Template applied, **Then** output includes tasks, dependencies, and resources
2. **Given** resource constraints, **When** template applied, **Then** constraints are factored into plan
3. **Given** plan created, **When** reviewed, **Then** critical path is identified

---

### User Story 3 - Execution (Priority: P1)

As a developer, I want a structured execution template so that I can track progress and maintain focus.

**Why this priority**: Execution without structure leads to drift and missed objectives.

**Independent Test**: Can be tested by simulating execution and verifying progress tracking.

**Acceptance Scenarios**:

1. **Given** a plan, **When** Execution Template applied, **Then** execution is tracked against milestones
2. **Given** unexpected issue, **When** template used, **Then** issue is captured and plan adjusted
3. **Given** execution complete, **When** template reviewed, **Then** all steps accounted for

---

### User Story 4 - Evaluation (Priority: P1)

As a developer, I want a structured evaluation template so that I can assess results against criteria.

**Why this priority**: Evaluation closes the loop on whether objectives were met.

**Independent Test**: Can be tested by evaluating completed work and verifying assessment completeness.

**Acceptance Scenarios**:

1. **Given** completed work, **When** Evaluation Template applied, **Then** all acceptance criteria are assessed
2. **Given** criteria with different priorities, **When** evaluated, **Then** priority is factored into overall score
3. **Given** evaluation complete, **When** reviewed, **Then** gaps are clearly identified

---

### User Story 5 - Reflection (Priority: P2)

As a developer, I want a structured reflection template so that I can extract lessons learned for future work.

**Why this priority**: Reflection enables continuous improvement and knowledge capture.

**Independent Test**: Can be tested by reflecting on completed work and verifying lessons are actionable.

**Acceptance Scenarios**:

1. **Given** completed project, **When** Reflection Template applied, **Then** what worked and what didn't are identified
2. **Given** patterns identified, **When** template used, **Then** patterns are documented with context
3. **Given** reflection complete, **When** applied to future work, **Then** improvements are observed

---

## Requirements

### Functional Requirements

- **FR-RT-001**: System MUST provide Problem Understanding Template for structured problem analysis
- **FR-RT-002**: System MUST provide Planning Template for comprehensive plan creation
- **FR-RT-003**: System MUST provide Execution Template for progress tracking
- **FR-RT-004**: System MUST provide Evaluation Template for results assessment
- **FR-RT-005**: System MUST provide Reflection Template for lessons learned
- **FR-RT-006**: Each template MUST define required inputs, reasoning steps, and output structure
- **FR-RT-007**: Each template MUST be applicable to problems of varying complexity
- **FR-RT-008**: Each template output MUST be machine-readable and human-comprehensible

### Non-Functional Requirements

- **NFR-RT-001**: Template application MUST complete within 5 seconds for typical inputs
- **NFR-RT-002**: Templates MUST support partial application (not all inputs required)
- **NFR-RT-003**: Template outputs MUST be serializable to structured formats

### Key Entities

- **ReasoningTemplate** - Base template structure
- **TemplateInput** - Inputs required by template
- **ReasoningStep** - Individual step in reasoning process
- **TemplateOutput** - Structured output from template
- **TemplateRegistry** - Discovery and management of templates

---

## 1. Problem Understanding Template

### Purpose
Provides structured approach to understanding and defining problems before attempting solutions.

### Required Inputs

```python
@dataclass
class ProblemUnderstandingInput:
    """Input for Problem Understanding Template."""
    problem_statement: str  # Raw problem description
    context: Optional[str] = None  # Background information
    stakeholders: List[str] = None  # People/teams affected
    existing_solutions: List[str] = None  # Already tried approaches
    constraints: List[str] = None  # Known limitations
    success_criteria: List[str] = None  # What success looks like
    priority: Optional[str] = None  # P0, P1, P2, P3
    deadline: Optional[str] = None  # Target completion date

    def validate(self) -> tuple[bool, str]:
        if not self.problem_statement or not self.problem_statement.strip():
            return False, "Problem statement is required"
        if len(self.problem_statement) > 10000:
            return False, "Problem statement exceeds maximum length"
        return True, "Valid"
```

### Expected Reasoning Steps

| Step | Description | Questions to Answer |
|------|-------------|-------------------|
| 1 | Extract Core Problem | What is the fundamental issue? |
| 2 | Identify Stakeholders | Who is affected? Who can help? |
| 3 | Define Success | What does success look like? |
| 4 | List Constraints | What limits our approach? |
| 5 | Analyze Existing Solutions | What has been tried? Why failed? |
| 6 | Surface Ambiguities | What is unclear? |
| 7 | Prioritize | What is the priority? |
| 8 | Define Scope | What's in/out of scope? |

### Output Structure

```python
@dataclass
class CoreProblem:
    """Identified core problem."""
    summary: str
    root_cause: Optional[str]
    symptoms: List[str]
    impact: str  # "critical", "major", "minor", "cosmetic"


@dataclass
class StakeholderInfo:
    """Stakeholder analysis."""
    name: str
    role: str  # "affected", "decision_maker", "contributor", "observer"
    interests: List[str]
    concerns: List[str]


@dataclass
class ProblemUnderstandingOutput:
    """Output from Problem Understanding Template."""
    core_problem: CoreProblem
    stakeholders: List[StakeholderInfo]
    success_criteria: List[str]
    constraints: List[str]
    scope_in: List[str]
    scope_out: List[str]
    ambiguities: List[str]  # Items needing clarification
    risks: List[str]  # Potential issues
    priority: str
    confidence: float  # 0-1 confidence in understanding
    refined_problem_statement: str
    questions_for_stakeholders: List[str]
    related_problems: List[str]  # Problems this is related to

    def validate(self) -> tuple[bool, str]:
        if not self.core_problem.summary:
            return False, "Core problem summary is required"
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        return True, "Valid"
```

### Template Representation

```yaml
template:
  name: "Problem Understanding Template"
  version: "1.0.0"
  purpose: "Structured approach to understanding problems"
  inputs:
    - name: "problem_statement"
      type: "string"
      required: true
      max_length: 10000
    - name: "context"
      type: "string"
      required: false
    - name: "stakeholders"
      type: "list[string]"
      required: false
    - name: "constraints"
      type: "list[string]"
      required: false
    - name: "success_criteria"
      type: "list[string]"
      required: false
  steps:
    - id: "extract_core"
      description: "Extract the core problem"
      questions: ["What is the fundamental issue?", "What is the root cause?"]
    - id: "identify_stakeholders"
      description: "Identify stakeholders"
      questions: ["Who is affected?", "Who are decision makers?"]
    - id: "define_success"
      description: "Define success criteria"
      questions: ["What does success look like?", "How is it measured?"]
    - id: "list_constraints"
      description: "List constraints"
      questions: ["What limits our approach?", "What resources are available?"]
    - id: "analyze_existing"
      description: "Analyze existing solutions"
      questions: ["What has been tried?", "Why did it fail?"]
    - id: "surface_ambiguities"
      description: "Surface ambiguities"
      questions: ["What is unclear?", "What assumptions are we making?"]
    - id: "prioritize"
      description: "Determine priority"
      questions: ["How urgent?", "How important?"]
    - id: "define_scope"
      description: "Define scope"
      questions: ["What is included?", "What is excluded?"]
  output:
    type: "ProblemUnderstandingOutput"
    schema: "..."
```

---

## 2. Planning Template

### Purpose
Provides structured approach to creating comprehensive, actionable plans.

### Required Inputs

```python
@dataclass
class PlanningInput:
    """Input for Planning Template."""
    understood_problem: ProblemUnderstandingOutput  # From Problem Understanding
    available_resources: List[str] = None  # Resources available
    team_capabilities: List[str] = None  # What the team can do
    timeline_constraints: List[str] = None  # Time limitations
    dependencies: List[str] = None  # External dependencies
    risks: List[str] = None  # Identified risks
    quality_standards: List[str] = None  # Quality requirements
    budget_constraints: Optional[str] = None  # Budget limits

    def validate(self) -> tuple[bool, str]:
        if not self.understood_problem:
            return False, "Understood problem is required"
        return True, "Valid"
```

### Expected Reasoning Steps

| Step | Description | Questions to Answer |
|------|-------------|-------------------|
| 1 | Define Objectives | What specifically must be achieved? |
| 2 | Identify Deliverables | What outputs are needed? |
| 3 | Break Down Work | What tasks are needed? |
| 4 | Sequence Tasks | What order? What's parallelizable? |
| 5 | Estimate Effort | How long for each task? |
| 6 | Identify Resources | Who/what is needed? |
| 7 | Assess Risks | What could go wrong? |
| 8 | Create Schedule | When will each task happen? |

### Output Structure

```python
@dataclass
class PlanObjective:
    """Plan objective."""
    objective_id: str
    description: str
    success_metric: str
    target_date: Optional[str]


@dataclass
class PlanTask:
    """Plan task."""
    task_id: str
    name: str
    description: str
    objective_id: str  # Which objective this serves
    dependencies: List[str]  # Task IDs
    estimated_hours: float
    assigned_to: Optional[str]
    priority: str  # "P0", "P1", "P2", "P3"
    status: str = "pending"  # "pending", "in_progress", "completed", "blocked"
    subtasks: List["PlanTask"] = None  # Nested subtasks


@dataclass
class ResourceRequirement:
    """Resource requirement."""
    resource_type: str  # "person", "tool", "infrastructure", "budget"
    name: str
    quantity: int
    availability: str  # "available", "limited", "unavailable"
    cost_estimate: Optional[float]


@dataclass
class RiskMitigation:
    """Risk with mitigation strategy."""
    risk_id: str
    description: str
    probability: str  # "high", "medium", "low"
    impact: str  # "high", "medium", "low"
    mitigation_strategy: str
    contingency_plan: str


@dataclass
class PlanningOutput:
    """Output from Planning Template."""
    plan_id: str
    objectives: List[PlanObjective]
    tasks: List[PlanTask]
    task_order: List[str]  # Task IDs in execution order
    critical_path: List[str]  # Task IDs on critical path
    parallel_groups: List[List[str]]  # Tasks that can run in parallel
    resources: List[ResourceRequirement]
    risk_mitigations: List[RiskMitigation]
    timeline: str  # Human-readable timeline
    total_estimated_hours: float
    milestones: List[Dict[str, Any]]  # Key checkpoints
    assumptions: List[str]
    dependencies_external: List[str]
    confidence: float  # 0-1 confidence in plan

    def validate(self) -> tuple[bool, str]:
        if not self.objectives:
            return False, "At least one objective is required"
        if not self.tasks:
            return False, "At least one task is required"
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        return True, "Valid"
```

---

## 3. Execution Template

### Purpose
Provides structured approach to executing plans and tracking progress.

### Required Inputs

```python
@dataclass
class ExecutionInput:
    """Input for Execution Template."""
    plan: PlanningOutput  # From Planning Template
    actual_start: Optional[str] = None  # ISO timestamp
    checkpoints: List[str] = None  # Milestone names to track
    tracking_frequency: str = "daily"  # "hourly", "daily", "weekly"
    auto_checkpoint: bool = True  # Auto-create checkpoints

    def validate(self) -> tuple[bool, str]:
        if not self.plan:
            return False, "Plan is required"
        return True, "Valid"
```

### Expected Reasoning Steps

| Step | Description | Questions to Answer |
|------|-------------|-------------------|
| 1 | Initialize Tracking | What are we tracking? How often? |
| 2 | Execute Tasks | What is happening now? |
| 3 | Monitor Progress | Are we on track? |
| 4 | Handle Blockers | What is blocked? Why? |
| 5 | Adjust Plan | Do we need changes? |
| 6 | Document Progress | What has been done? |
| 7 | Report Status | What is the current state? |

### Output Structure

```python
@dataclass
class TaskProgress:
    """Progress on a single task."""
    task_id: str
    status: str  # "pending", "in_progress", "completed", "blocked", "cancelled"
    progress_percent: float  # 0-100
    started_at: Optional[str]
    completed_at: Optional[str]
    actual_hours: float
    notes: List[str]
    blockers: List[str] = None
    dependencies_met: bool = True


@dataclass
class ExecutionCheckpoint:
    """Execution checkpoint snapshot."""
    checkpoint_id: str
    timestamp: str
    completed_tasks: List[str]
    in_progress_tasks: List[str]
    pending_tasks: List[str]
    blockers: List[str]
    progress_percent: float
    summary: str


@dataclass
class PlanAdjustment:
    """Adjustment made to the plan."""
    adjustment_id: str
    adjustment_type: str  # "schedule", "scope", "resource", "priority"
    description: str
    reason: str
    impact_assessment: str
    approved_by: Optional[str]
    timestamp: str


@dataclass
class ExecutionOutput:
    """Output from Execution Template."""
    execution_id: str
    plan_id: str
    status: str  # "in_progress", "completed", "paused", "cancelled"
    task_progress: Dict[str, TaskProgress]  # task_id -> progress
    checkpoints: List[ExecutionCheckpoint]
    plan_adjustments: List[PlanAdjustment]
    current_progress_percent: float
    estimated_completion: Optional[str]
    total_actual_hours: float
    blockers_active: List[str]
    next_actions: List[str]
    completion_summary: Optional[str] = None  # Filled when completed

    def validate(self) -> tuple[bool, str]:
        if self.progress_percent < 0 or self.progress_percent > 100:
            return False, "Progress must be 0-100"
        return True, "Valid"
```

---

## 4. Evaluation Template

### Purpose
Provides structured approach to evaluating results against criteria.

### Required Inputs

```python
@dataclass
class EvaluationInput:
    """Input for Evaluation Template."""
    completed_work: Dict[str, Any]  # Results to evaluate
    original_objectives: List[PlanObjective]  # From Planning
    acceptance_criteria: List[str]  # From Problem Understanding
    evaluation_framework: Optional[str] = None  # Custom framework
    metrics_data: Dict[str, float] = None  # Quantitative metrics
    stakeholder_feedback: List[str] = None  # Qualitative feedback

    def validate(self) -> tuple[bool, str]:
        if not self.completed_work:
            return False, "Completed work is required"
        if not self.original_objectives:
            return False, "Original objectives are required"
        return True, "Valid"
```

### Expected Reasoning Steps

| Step | Description | Questions to Answer |
|------|-------------|-------------------|
| 1 | Review Objectives | What were we trying to achieve? |
| 2 | Assess Criteria | Which criteria are met? |
| 3 | Measure Metrics | What do the numbers say? |
| 4 | Gather Feedback | What do stakeholders say? |
| 5 | Identify Gaps | What is missing? |
| 6 | Calculate Scores | How did we score? |
| 7 | Document Findings | What did we learn? |

### Output Structure

```python
@dataclass
class CriterionResult:
    """Result for a single criterion."""
    criterion_id: str
    description: str
    target: Any
    actual: Any
    met: bool  # True if met
    gap: Optional[Any]  # Gap if not met
    evidence: str
    weight: float  # For scoring
    score: float  # 0-1 score for this criterion


@dataclass
class ObjectiveResult:
    """Result for a single objective."""
    objective_id: str
    description: str
    success_metric: str
    target_value: Any
    actual_value: Any
    met: bool
    criteria_results: List[CriterionResult]
    overall_score: float


@dataclass
class MetricAssessment:
    """Assessment of a quantitative metric."""
    metric_name: str
    target: float
    actual: float
    unit: str
    percent_achieved: float
    trend: str  # "improving", "stable", "declining"


@dataclass
class EvaluationOutput:
    """Output from Evaluation Template."""
    evaluation_id: str
    overall_score: float  # Weighted average 0-1
    overall_status: str  # "exceeds", "meets", "partial", "fails"
    objective_results: List[ObjectiveResult]
    criteria_results: List[CriterionResult]
    metrics_assessment: List[MetricAssessment]
    stakeholder_satisfaction: float  # 0-1 if available
    gaps_identified: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    pass_fail_decision: str  # "pass", "conditional_pass", "fail"
    conditions_for_conditional: Optional[str] = None
    detailed_report: str  # Human-readable report

    def validate(self) -> tuple[bool, str]:
        if self.overall_score < 0 or self.overall_score > 1:
            return False, "Overall score must be 0-1"
        if self.overall_status not in ["exceeds", "meets", "partial", "fails"]:
            return False, "Invalid overall status"
        return True, "Valid"
```

---

## 5. Reflection Template

### Purpose
Provides structured approach to reflecting on completed work and capturing lessons learned.

### Required Inputs

```python
@dataclass
class ReflectionInput:
    """Input for Reflection Template."""
    evaluation_result: EvaluationOutput  # From Evaluation Template
    execution_summary: ExecutionOutput  # From Execution Template
    original_plan: PlanningOutput  # Original plan for comparison
    team_feedback: List[str] = None  # Team observations
    time_actual_vs_estimated: Dict[str, float] = None  # Time comparison
    unexpected_events: List[str] = None  # What surprised us
    tools_used: List[str] = None  # What worked/didn't

    def validate(self) -> tuple[bool, str]:
        if not self.evaluation_result:
            return False, "Evaluation result is required"
        return True, "Valid"
```

### Expected Reasoning Steps

| Step | Description | Questions to Answer |
|------|-------------|-------------------|
| 1 | Review What Worked | What went well? Why? |
| 2 | Review What Didn't | What didn't go well? Why? |
| 3 | Analyze Surprises | What was unexpected? |
| 4 | Compare Plan vs Actual | What changed? Why? |
| 5 | Identify Patterns | What recurring themes? |
| 6 | Extract Lessons | What did we learn? |
| 7 | Document Actions | What should we do differently? |

### Output Structure

```python
@dataclass
class WhatWorkedItem:
    """Item that worked well."""
    area: str
    description: str
    contributing_factors: List[str]
    repeatable: bool
    recommendation: str


@dataclass
class WhatDidntWorkItem:
    """Item that didn't work well."""
    area: str
    description: str
    root_cause: str
    impact: str  # "high", "medium", "low"
    alternative_approaches: List[str]
    lesson_learned: str


@dataclass
class PatternIdentified:
    """Pattern identified across the project."""
    pattern_name: str
    occurrences: List[str]
    frequency: str  # "once", "sometimes", "often"
    implications: str
    suggested_action: str


@dataclass
class ActionItem:
    """Action item for future work."""
    action_id: str
    description: str
    priority: str  # "high", "medium", "low"
    owner: Optional[str]
    target_project: Optional[str]  # When to apply
    rationale: str


@dataclass
class ReflectionOutput:
    """Output from Reflection Template."""
    reflection_id: str
    project_summary: str
    what_worked: List[WhatWorkedItem]
    what_didnt_work: List[WhatDidntWorkItem]
    unexpected_events: List[Dict[str, Any]]  # event, impact, response
    plan_vs_actual: Dict[str, Any]  # Key comparisons
    patterns_identified: List[PatternIdentified]
    lessons_learned: List[str]
    action_items: List[ActionItem]
    knowledge_to_preserve: List[str]
    would_do_different: List[str]
    recommendations_for_future: List[str]
    overall_assessment: str  # Brief summary
    confidence: float  # 0-1 confidence in reflection

    def validate(self) -> tuple[bool, str]:
        if self.confidence < 0 or self.confidence > 1:
            return False, "Confidence must be 0-1"
        return True, "Valid"
```

---

## Template Registry

```python
class ReasoningTemplateRegistry:
    """Registry for reasoning templates."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, template: Dict[str, Any]) -> bool:
        """Register a template."""
        self._templates[name] = template
        return True

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name."""
        return self._templates.get(name)

    def list_all(self) -> List[str]:
        """List all registered templates."""
        return list(self._templates.keys())

    def apply(self, name: str, input: Any) -> Any:
        """Apply a template to input."""
        template = self.get(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        # Apply template logic
        ...
```

---

## Template Composition

### Reasoning Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Reasoning Workflow                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Problem ─────► Planning ─────► Execution ─────► Evaluation  │
│  Understanding                                                      │
│       │              │              │              │          │
│       └──────────────┴──────────────┴──────────────┘          │
│                           │                                   │
│                           ▼                                   │
│                    Reflection                                 │
│                           │                                   │
│                           ▼                                   │
│              Improved Problem Understanding                   │
│                      (Cycle Repeats)                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

| Template | Purpose | Input | Output |
|----------|---------|-------|--------|
| **Problem Understanding** | Structure problem analysis | Problem statement | Core problem, stakeholders, scope |
| **Planning** | Create actionable plans | Understood problem | Tasks, dependencies, timeline |
| **Execution** | Track and execute | Plan | Progress, checkpoints, adjustments |
| **Evaluation** | Assess results | Completed work | Scores, gaps, pass/fail |
| **Reflection** | Capture lessons | Evaluation + Execution | Lessons, actions, patterns |

**PHR**: `history/prompts/reusable-reasoning-templates/001-define-reusable-reasoning-templates.spec.prompt.md`
