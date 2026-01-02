# Reusable Sub-Agents Specification

**Feature Branch**: `feat/reusable-agents`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define reusable sub-agents with clear responsibilities..."

## User Scenarios & Testing

### User Story 1 - Architect Agent (Priority: P1)

As a developer, I want an Architect Agent that designs system structure and abstractions so that I can establish solid foundations before implementation.

**Why this priority**: Architecture decisions are foundational. Getting them wrong leads to costly refactoring later.

**Independent Test**: Can be tested by providing requirements and verifying architectural output matches expected structure.

**Acceptance Scenarios**:

1. **Given** feature requirements, **When** Architect Agent runs, **Then** output includes component diagram, interface contracts, and data flow
2. **Given** non-functional requirements, **When** architecting, **Then** architecture addresses performance, security, and scalability
3. **Given** architectural decisions, **When** output validated, **Then** decisions are justified with trade-offs documented

---

### User Story 2 - Planner Agent (Priority: P1)

As a developer, I want a Planner Agent that converts specifications into actionable steps so that I can execute work systematically.

**Why this priority**: Planning bridges the gap between what to build and how to build it.

**Independent Test**: Can be tested by providing specs and verifying task breakdown output.

**Acceptance Scenarios**:

1. **Given** validated specification, **When** Planner Agent runs, **Then** output includes ordered task list with dependencies
2. **Given** task list, **When** validated, **Then** each task is atomic and independently testable
3. **Given** tasks, **When** estimated, **Then** effort estimates are provided with confidence levels

---

### User Story 3 - Executor Agent (Priority: P1)

As a developer, I want an Executor Agent that performs implementation actions so that I can achieve concrete outcomes from plans.

**Why this priority**: Execution is where value is delivered. Without execution, plans remain theoretical.

**Independent Test**: Can be tested by providing tasks and verifying implementation output.

**Acceptance Scenarios**:

1. **Given** task with clear steps, **When** Executor Agent runs, **Then** output includes implemented artifacts
2. **Given** implementation, **When** validated, **Then** output matches task requirements
3. **Given** execution failure, **When** error occurs, **Then** error is reported with context and recovery suggestions

---

### User Story 4 - Reviewer Agent (Priority: P1)

As a developer, I want a Reviewer Agent that audits quality, correctness, and alignment so that I can ensure standards are met before merge.

**Why this priority**: Reviews catch issues before they become technical debt. Manual reviews alone are inconsistent and unscalable.

**Independent Test**: Can be tested by providing implementation and verifying review output.

**Acceptance Scenarios**:

1. **Given** code implementation, **When** Reviewer Agent runs, **Then** output includes quality scores for each category
2. **Given** review findings, **When** categorized, **Then** findings are labeled blocking, warning, or informational
3. **Given** alignment check, **When** compared to spec, **Then** spec-compliance status is reported

---

### User Story 5 - Refiner Agent (Priority: P2)

As a developer, I want a Refiner Agent that improves clarity, efficiency, and robustness so that I can continuously enhance existing work.

**Why this priority**: Refinement turns good code into great code. It enables continuous improvement without new features.

**Independent Test**: Can be tested by providing implementation and verifying refinement suggestions.

**Acceptance Scenarios**:

1. **Given** implementation, **When** Refiner Agent runs, **Then** output includes specific improvement suggestions
2. **Given** refactoring suggestions, **When** prioritized, **Then** impact/effort ratios are provided
3. **Given** applied refinements, **When** re-reviewed, **Then** quality metrics show improvement

---

### Edge Cases

- What happens when agent input is incomplete or invalid?
- How do agents handle conflicting requirements?
- How are agent disagreements resolved?
- What happens when agents produce contradictory outputs?

## Requirements

### Functional Requirements

- **FR-AGT-001**: System MUST provide Architect Agent that designs system structure and abstractions
- **FR-AGT-002**: System MUST provide Planner Agent that converts specs into actionable steps
- **FR-AGT-003**: System MUST provide Executor Agent that performs implementation actions
- **FR-AGT-004**: System MUST provide Reviewer Agent that audits quality, correctness, and alignment
- **FR-AGT-005**: System MUST provide Refiner Agent that improves clarity, efficiency, and robustness
- **FR-AGT-006**: Each agent MUST operate independently without requiring other agents
- **FR-AGT-007**: Each agent MUST communicate via structured artifacts (not ad-hoc messages)
- **FR-AGT-008**: Each agent MUST be reusable across different projects without modification
- **FR-AGT-009**: Each agent MUST declare its input/output schemas explicitly
- **FR-AGT-010**: Each agent MUST provide audit trail of its reasoning and decisions

### Non-Functional Requirements

- **NFR-AGT-001**: Each agent MUST complete typical tasks within 30 seconds
- **NFR-AGT-002**: Agents MUST support parallel execution without interference
- **NFR-AGT-003**: Agent output MUST be deterministic for same inputs (no randomness)
- **NFR-AGT-004**: Each agent MUST support configuration for project-specific context

### Key Entities

- **Agent**: Independent cognitive entity with specific responsibility
- **AgentInput**: Structured input to an agent
- **AgentOutput**: Structured output from an agent
- **AgentContext**: Shared context for agent execution
- **Artifact**: Structured communication between agents
- **AuditTrail**: Record of agent reasoning and decisions

## Success Criteria

- **SC-AGT-001**: All 5 agents can be invoked independently
- **SC-AGT-002**: Agent outputs conform to declared schemas
- **SC-AGT-003**: Agents produce deterministic, reproducible results
- **SC-AGT-004**: Agent communication uses structured artifacts
- **SC-AGT-005**: Agents can be reused across different projects

---

## Agent Specifications

### Agent Base Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass
from enum import Enum
import json

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentContext:
    """Shared context available to all agents."""
    project_name: str
    project_root: str
    constitution_version: str
    current_phase: str
    artifacts: Dict[str, Any] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = {}


@dataclass
class AgentInput(Generic[InputT]):
    """Base input for all agents."""
    payload: InputT
    context: AgentContext
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class AuditTrailEntry:
    """Single entry in agent audit trail."""
    timestamp: str
    action: str
    reasoning: str
    decision: str
    artifacts_created: list[str] = None


@dataclass
class AgentOutput(Generic[OutputT]):
    """Base output for all agents."""
    status: AgentStatus
    payload: OutputT
    audit_trail: list[AuditTrailEntry] = None
    artifacts: Dict[str, str] = None  # artifact_name -> file_path
    errors: list[str] = None

    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []
        if self.artifacts is None:
            self.artifacts = {}
        if self.errors is None:
            self.errors = []


class Agent(ABC, Generic[InputT, OutputT]):
    """Base interface for all agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable agent description."""
        ...

    @property
    @abstractmethod
    def responsibility(self) -> str:
        """Clear statement of agent's responsibility."""
        ...

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for valid inputs."""
        ...

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """JSON schema for outputs."""
        ...

    @abstractmethod
    def execute(self, input: AgentInput[InputT]) -> AgentOutput[OutputT]:
        """Execute agent logic."""
        ...

    @abstractmethod
    def validate_input(self, input: AgentInput[InputT]) -> tuple[bool, str]:
        """Validate input against schema."""
        ...
```

---

### 1. Architect Agent

**Responsibility**: Designs system structure and abstractions.

**Input**: Requirements specification, constraints, non-functional requirements

**Output**: Architecture document with components, interfaces, data flow, trade-offs

**Input Schema**:

```python
architect_input_schema = {
    "type": "object",
    "properties": {
        "requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Feature or functional requirements"
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"},
            "description": "System constraints (performance, security, etc.)"
        },
        "non_functional_requirements": {
            "type": "object",
            "properties": {
                "performance": {"type": "string"},
                "security": {"type": "string"},
                "scalability": {"type": "string"},
                "reliability": {"type": "string"}
            }
        },
        "existing_architecture": {
            "type": "string",
            "description": "Path to existing architecture document (if any)"
        },
        "technology_preferences": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Preferred technologies or patterns"
        }
    },
    "required": ["requirements", "constraints"]
}
```

**Output Schema**:

```python
@dataclass
class Component:
    """Architecture component definition."""
    name: str
    responsibility: str
    interfaces: list[str]
    dependencies: list[str]
    technology: str = None


@dataclass
class Interface:
    """Component interface definition."""
    name: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    protocol: str


@dataclass
class DataFlow:
    """Data flow between components."""
    from_component: str
    to_component: str
    data_type: str
    frequency: str


@dataclass
class TradeOff:
    """Architectural trade-off decision."""
    dimension: str
    choice: str
    rationale: str
    alternative: str
    rejection_reason: str


@dataclass
class ArchitectureOutput:
    """Output from Architect Agent."""
    components: list[Component]
    interfaces: list[Interface]
    data_flows: list[DataFlow]
    trade_offs: list[TradeOff]
    architecture_diagram: str  # PlantUML or similar
    assumptions: list[str]
    risks: list[str]
```

**Agent Definition**:

```python
class ArchitectAgent(Agent[ArchitectInput, ArchitectureOutput]):
    """Designs system structure and abstractions."""

    @property
    def name(self) -> str:
        return "architect_agent"

    @property
    def description(self) -> str:
        return "Analyzes requirements and constraints to design system architecture"

    @property
    def responsibility(self) -> str:
        return "Design system structure, components, interfaces, and data flows while documenting trade-offs"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return architect_input_schema

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "responsibility": {"type": "string"},
                            "interfaces": {"type": "array", "items": {"type": "string"}},
                            "dependencies": {"type": "array", "items": {"type": "string"}},
                            "technology": {"type": "string"}
                        },
                        "required": ["name", "responsibility", "interfaces", "dependencies"]
                    }
                },
                "interfaces": {"type": "array"},
                "data_flows": {"type": "array"},
                "trade_offs": {"type": "array"},
                "architecture_diagram": {"type": "string"},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "risks": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["components", "interfaces", "data_flows", "trade_offs"]
        }

    def execute(self, input: AgentInput[ArchitectInput]) -> AgentOutput[ArchitectureOutput]:
        """Execute architecture design."""
        # Implementation
        ...
```

---

### 2. Planner Agent

**Responsibility**: Converts specifications into actionable steps.

**Input**: Validated specification, architecture context, constraints

**Output**: Task breakdown with dependencies, estimates, ordering

**Input Schema**:

```python
planner_input_schema = {
    "type": "object",
    "properties": {
        "specification": {
            "type": "object",
            "description": "Validated specification document"
        },
        "architecture": {
            "type": "object",
            "description": "Architecture context"
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Planning constraints (timeline, resources, etc.)"
        },
        "task_templates": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Available task templates to use"
        },
        "priority_order": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Order of priorities"
        }
    },
    "required": ["specification", "architecture"]
}
```

**Output Schema**:

```python
@dataclass
class TaskStep:
    """Individual step within a task."""
    step_id: str
    description: str
    command: str
    success_criteria: list[str]
    rollback_command: str = None


@dataclass
class Task:
    """Atomic unit of work."""
    task_id: str
    name: str
    description: str
    category: str  # "implementation", "testing", "documentation", "review"
    priority: str  # "P0", "P1", "P2", "P3"
    dependencies: list[str]
    steps: list[TaskStep]
    estimated_effort: str
    confidence: float  # 0.0 to 1.0
    validation_criteria: list[str]


@dataclass
class TaskOrder:
    """Execution order with justification."""
    task_ids: list[str]
    justification: str
    parallel_groups: list[list[str]]  # Tasks that can run in parallel


@dataclass
class PlanningOutput:
    """Output from Planner Agent."""
    tasks: list[Task]
    execution_order: TaskOrder
    total_tasks: int
    critical_path: list[str]
    resource_requirements: Dict[str, int]
    risk_assessment: Dict[str, str]
```

**Agent Definition**:

```python
class PlannerAgent(Agent[PlannerInput, PlanningOutput]):
    """Converts specs into actionable steps."""

    @property
    def name(self) -> str:
        return "planner_agent"

    @property
    def description(self) -> str:
        return "Transforms specifications into ordered, dependency-aware task lists"

    @property
    def responsibility(self) -> str:
        return "Break down specifications into atomic, prioritized tasks with clear dependencies"
```

---

### 3. Executor Agent

**Responsibility**: Performs implementation actions.

**Input**: Task with steps, execution context, available tools

**Output**: Implemented artifacts, execution log, status

**Input Schema**:

```python
executor_input_schema = {
    "type": "object",
    "properties": {
        "task": {
            "type": "object",
            "description": "Task to execute"
        },
        "context": {
            "type": "object",
            "description": "Execution context (project root, tools available, etc.)"
        },
        "dry_run": {
            "type": "boolean",
            "description": "If true, only simulate execution"
        },
        "checkpoint_frequency": {
            "type": "integer",
            "description": "Steps between checkpoints"
        }
    },
    "required": ["task", "context"]
}
```

**Output Schema**:

```python
@dataclass
class StepResult:
    """Result of executing a single step."""
    step_id: str
    status: str  # "completed", "failed", "skipped"
    output: str
    duration_ms: int
    artifacts_created: list[str]
    error: str = None


@dataclass
class ExecutionOutput:
    """Output from Executor Agent."""
    task_id: str
    overall_status: str  # "completed", "partial", "failed"
    step_results: list[StepResult]
    artifacts_created: Dict[str, str]  # artifact_name -> path
    total_duration_ms: int
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    checkpoints: list[Dict[str, Any]]
```

**Agent Definition**:

```python
class ExecutorAgent(Agent[ExecutorInput, ExecutionOutput]):
    """Performs implementation actions."""

    @property
    def name(self) -> str:
        return "executor_agent"

    @property
    def description(self) -> str:
        return "Executes implementation steps and creates artifacts"

    @property
    def responsibility(self) -> str:
        return "Perform implementation actions according to task specifications, tracking state and outcomes"
```

---

### 4. Reviewer Agent

**Responsibility**: Audits quality, correctness, and alignment.

**Input**: Implementation artifacts, specification, quality criteria

**Output**: Review report with findings, scores, recommendations

**Input Schema**:

```python
reviewer_input_schema = {
    "type": "object",
    "properties": {
        "artifacts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Paths to artifacts to review"
        },
        "specification": {
            "type": "object",
            "description": "Reference specification"
        },
        "quality_criteria": {
            "type": "object",
            "description": "Custom quality criteria (merged with defaults)"
        },
        "review_depth": {
            "type": "string",
            "enum": ["shallow", "standard", "deep"],
            "description": "Depth of review"
        }
    },
    "required": ["artifacts", "specification"]
}
```

**Output Schema**:

```python
@dataclass
class Finding:
    """Individual review finding."""
    category: str  # "correctness", "quality", "security", "performance"
    severity: str  # "blocking", "warning", "informational"
    title: str
    description: str
    location: str  # file:line
    suggestion: str
    evidence: str


@dataclass
class QualityScore:
    """Quality score for a category."""
    category: str
    score: float  # 0.0 to 1.0
    max_score: float
    findings_count: int


@dataclass
class AlignmentResult:
    """Spec alignment check result."""
    requirement_id: str
    status: str  # "compliant", "partial", "non-compliant", "not-applicable"
    evidence: str
    gaps: list[str]


@dataclass
class ReviewOutput:
    """Output from Reviewer Agent."""
    overall_score: float
    quality_scores: list[QualityScore]
    findings: list[Finding]
    alignment_results: list[AlignmentResult]
    summary: str
    recommendation: str  # "approve", "request-changes", "reject"
    files_reviewed: int
    lines_reviewed: int
```

**Agent Definition**:

```python
class ReviewerAgent(Agent[ReviewerInput, ReviewOutput]):
    """Audits quality, correctness, and alignment."""

    @property
    def name(self) -> str:
        return "reviewer_agent"

    @property
    def description(self) -> str:
        return "Reviews artifacts for quality, correctness, and spec alignment"

    @property
    def responsibility(self) -> str:
        return "Audit implementation against quality standards and specifications, providing actionable findings"
```

---

### 5. Refiner Agent

**Responsibility**: Improves clarity, efficiency, and robustness.

**Input**: Implementation, review findings, improvement criteria

**Output**: Refinement suggestions with impact assessments

**Input Schema**:

```python
refiner_input_schema = {
    "type": "object",
    "properties": {
        "artifacts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Paths to artifacts to refine"
        },
        "review_findings": {
            "type": "array",
            "items": {"type": "object"},
            "description": "Findings from Reviewer Agent"
        },
        "improvement_goals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific improvement goals"
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Constraints on refinements"
        }
    },
    "required": ["artifacts"]
}
```

**Output Schema**:

```python
@dataclass
class RefinementSuggestion:
    """Individual refinement suggestion."""
    category: str  # "clarity", "efficiency", "robustness", "security"
    title: str
    description: str
    current_state: str
    proposed_state: str
    impact_effort_ratio: str  # "high", "medium", "low"
    estimated_improvement: str
    implementation_steps: list[str]
    risks: list[str]


@dataclass
class RefinementOutput:
    """Output from Refiner Agent."""
    suggestions: list[RefinementSuggestion]
    prioritized_suggestions: list[RefinementSuggestion]
    quick_wins: list[RefinementSuggestion]
    architectural_concerns: list[str]
    overall_improvement_potential: str
    refactoring_roadmap: list[str]
```

**Agent Definition**:

```python
class RefinerAgent(Agent[RefinerInput, RefinementOutput]):
    """Improves clarity, efficiency, and robustness."""

    @property
    def name(self) -> str:
        return "refiner_agent"

    @property
    def description(self) -> str:
        return "Analyzes implementation and suggests improvements"

    @property
    def responsibility(self) -> str:
        return "Identify and suggest improvements for clarity, efficiency, and robustness with impact assessments"
```

---

## Agent Communication Protocol

### Artifact Structure

Agents communicate via structured artifacts:

```python
@dataclass
class AgentArtifact:
    """Structured communication between agents."""
    artifact_id: str
    artifact_type: str  # "specification", "architecture", "plan", "implementation", "review", "refinement"
    source_agent: str
    target_agent: str = None
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    version: str


@dataclass
class AgentMessage:
    """Message envelope for agent communication."""
    message_id: str
    from_agent: str
    to_agent: str
    artifacts: list[AgentArtifact]
    priority: str  # "normal", "high", "blocking"
    timestamp: str
    correlation_id: str = None
```

### Agent Registry

```python
class AgentRegistry:
    """Discovers and manages available agents."""

    def register(self, agent: Agent) -> None:
        """Register an agent."""
        ...

    def get(self, name: str) -> Agent:
        """Retrieve agent by name."""
        ...

    def list_all(self) -> list[Agent]:
        """List all registered agents."""
        ...

    def find_by_capability(self, capability: str) -> list[Agent]:
        """Find agents with specific capability."""
        ...

    def validate_compatibility(self, agent_a: str, agent_b: str) -> bool:
        """Check if two agents can work together."""
        ...
```

### Agent Orchestrator

```python
class AgentOrchestrator:
    """Coordinates multiple agents working together."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def run_workflow(self, workflow: list[str], initial_input: Any) -> list[AgentOutput]:
        """Run agents in sequence."""
        ...

    def run_parallel(self, agents: list[str], input: Any) -> list[AgentOutput]:
        """Run agents in parallel."""
        ...

    def detect_conflicts(self, outputs: list[AgentOutput]) -> list[str]:
        """Detect conflicting outputs from agents."""
        ...
```

## Agent Configuration

Each agent supports configuration for project-specific context:

```python
agent_config_schema = {
    "type": "object",
    "properties": {
        "project_root": {"type": "string"},
        "coding_standards": {"type": "string"},
        "preferred_patterns": {"type": "array", "items": {"type": "string"}},
        "forbidden_patterns": {"type": "array", "items": {"type": "string"}},
        "naming_conventions": {"type": "object"},
        "documentation_style": {"type": "string"},
        "custom_rules": {"type": "array"}
    }
}
```

## Audit Trail Format

All agents produce audit trails:

```python
audit_trail_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "action": {"type": "string"},
            "reasoning": {"type": "string"},
            "decision": {"type": "string"},
            "artifacts_created": {"type": "array", "items": {"type": "string"}},
            "duration_ms": {"type": "integer"}
        },
        "required": ["timestamp", "action", "reasoning", "decision"]
    }
}
```
