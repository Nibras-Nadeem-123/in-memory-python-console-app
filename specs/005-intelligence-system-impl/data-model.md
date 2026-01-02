# SDD Data Models

This document describes the core data structures used in the Spec-Driven Development system.

## Overview

SDD uses a set of dataclass models to represent the flow of information through the development pipeline:
- **Intent**: Parsed user intent with classification
- **Spec**: Generated specification document
- **Plan**: Implementation plan with tasks
- **Task**: Individual implementation task
- **Guide**: Execution guidance document
- **Artifact**: Generic container for generated outputs
- **Decision**: Architectural decision record

## Models

### Intent

Represents a parsed user's intent with classification and confidence.

```python
@dataclass
class Intent:
    type: IntentType           # The intent category (CLARIFY, SPECIFY, PLAN, GUIDE)
    description: str              # Original natural language input
    confidence: float = 1.0       # Confidence score 0.0-1.0
    metadata: Dict[str, Any] = field(default_factory=dict)  # Entities, keywords
```

**Usage Example:**
```python
intent = Intent(
    type=IntentType.SPECIFY,
    description="Create a user authentication system with login and registration",
    confidence=0.85,
    metadata={
        "entities": ["user authentication", "login", "registration"],
        "keywords": ["create", "system", "authentication"]
    }
)
```

### Spec

Formal specification document with requirements and acceptance criteria.

```python
@dataclass
class Spec:
    title: str                                    # Human-readable title
    description: str                               # Original description
    requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    architecture_notes: str = ""                 # Design notes to fill in
```

**Usage Example:**
```python
spec = Spec(
    title="User Authentication System",
    description="Create a user authentication system...",
    requirements=[
        "FR-001: Users must be able to register with email and password",
        "FR-002: Users must be able to login with existing credentials"
    ],
    acceptance_criteria=[
        "SC-001: Registration validates email format",
        "SC-002: Login returns JWT token on success"
    ]
)
```

### Plan

Implementation plan with tasks and dependencies.

```python
@dataclass
class Plan:
    title: str                          # Plan title
    architecture: str = ""                # Architecture type (REST, etc)
    tasks: List[Task] = field(default_factory=list)
```

**Usage Example:**
```python
plan = Plan(
    title="Authentication System Implementation",
    architecture="REST API",
    tasks=[
        Task(id="T001", description="Implement user model", priority="P1"),
        Task(id="T002", description="Implement auth service", priority="P1", dependencies=["T001"])
    ]
)
```

### Task

Individual implementation task with metadata.

```python
@dataclass
class Task:
    id: str                                    # Unique task identifier
    description: str                             # Task description
    status: str = "pending"                 # pending, in_progress, complete
    priority: str = "P3"                      # P1, P2, P3
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    estimated_hours: Optional[float] = None     # Time estimate
```

**Task Dependencies:**
- Tasks can depend on multiple prerequisite tasks
- Circular dependencies are detected and reported
- Execution order is derived from dependency graph

### Guide

Execution guidance document with implementation recommendations.

```python
@dataclass
class Guide:
    title: str
    getting_started: str = ""           # Initial steps
    implementation_order: str = ""       # Suggested task order
    code_patterns: str = ""            # Best practices and patterns
    testing_recommendations: str = ""     # Testing guidance
```

### Artifact

Generic container for any generated output.

```python
@dataclass
class Artifact:
    artifact_type: str                      # Type identifier (intent, spec, plan, guide)
    content: Any                           # The actual content
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Unique ID
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

### IntentType

Enum classifying intent categories.

```python
class IntentType(str, Enum):
    CLARIFY = "clarify"      # User needs clarification
    SPECIFY = "specify"      # User wants specification
    PLAN = "plan"             # User wants implementation plan
    GUIDE = "guide"            # User wants execution guidance
```

### Decision

Architectural decision record for significant design choices.

```python
@dataclass
class Decision:
    type: str                          # Decision type/category
    rationale: str                       # Why this decision was made
    alternatives: List[str] = field(default_factory=list)  # Options considered
    consequences: str = ""                # Impact of this decision
```

## Context Model

### SDDContext

Extended execution context with SDD-specific fields:

```python
class SDDContext(ExecutionContext):
    intent: Optional[Intent] = None                # Parsed intent
    artifacts: Dict[str, Artifact] = field(default_factory=dict)  # Generated artifacts
    workflow_state: str = "initialized"          # Current workflow stage
```

**Context Lifecycle:**
1. `initialized` - Ready to parse intent
2. `clarification` - Intent parsed, awaiting clarification
3. `specification` - Spec generated, ready for planning
4. `planning` - Plan generated, ready for guidance
5. `guide_generation` - Guide being created
6. `complete` - Pipeline complete

## Workflow Flow

```
User Input
    ↓
IntentAgent → Intent
    ↓
SpecAgent → Spec (spec.md)
    ↓
PlanAgent → Plan (plan.md)
    ↓
GuideAgent → Guide (guide.md)
    ↓
Complete
```

## Artifact Relationships

- **Intent** → **Spec**: Intent.type determines if spec generation occurs
- **Spec** → **Plan**: Spec requirements become plan tasks
- **Plan** → **Guide**: Plan architecture determines scaffolding and practices
- **Artifacts**: All stored in context with unique IDs for tracking

## Error Handling

Each model type has corresponding exception:
- `IntentParsingError`: Failed to parse user intent
- `SpecGenerationError`: Failed to generate specification
- `PlanGenerationError`: Failed to create plan
- `GuideGenerationError`: Failed to create guide
- `WorkflowError`: Generic workflow execution failure
- `ValidationError`: Artifact validation failed
- `AmbiguityError`: Ambiguous input detected
- `CircularDependencyError`: Circular task dependencies detected
