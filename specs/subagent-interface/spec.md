---
id: 'subagent-interface'
title: 'Standard SubAgent Interface'
version: '1.0.0'
date: '2025-12-28'
status: 'Draft'
feature: 'subagent-interface'
branch: 'main'
---

## Overview

The SubAgent Interface defines a standardized contract for all sub-agents in the intelligence layer. Every agent must declare its identity, capabilities, inputs, outputs, dependencies, and error handling strategy, enabling the Engine to orchestrate, validate, and compose agents dynamically.

## Purpose

- **Identity**: Clear naming and responsibility declaration for routing
- **Capability Declaration**: Explicit inputs, outputs, and required skills for composition
- **Structured Results**: Consistent result format for engine aggregation
- **Error Handling**: Predictable failure modes and recovery strategies
- **Engine Integration**: Callable interface with lifecycle hooks

## User Scenarios & Testing

### User Story 1 - Agent Discovery

As an orchestrator, I want to discover agent capabilities at runtime so that I can route tasks to appropriate agents.

**Priority**: P1

**Independent Test**: Query agent registry and verify capability matching.

**Acceptance Scenarios**:

1. **Given** agent registry with 5 agents, **When** querying for "planning" capability, **Then** only PlannerAgent returned
2. **Given** agent with input schema, **When** validating task against schema, **Then** validation passes or fails with clear error
3. **Given** agent with required skills, **When** checking skill availability, **Then** all required skills present or missing reported

### User Story 2 - Engine Invocation

As an engine, I want to invoke agents through a standard interface so that I can compose them in workflows.

**Priority**: P1

**Independent Test**: Invoke agent through interface and verify result format.

**Acceptance Scenarios**:

1. **Given** agent initialized, **When** engine calls `execute(input)`, **Then** structured Result returned
2. **Given** agent with output schema, **When** result produced, **Then** output matches schema
3. **Given** agent execution, **When** complete, **Then** result includes metrics (duration, confidence)

### User Story 3 - Error Handling

As a developer, I want agents to report errors consistently so that I can handle failures uniformly.

**Priority**: P1

**Independent Test**: Trigger agent errors and verify error format.

**Acceptance Scenarios**:

1. **Given** agent with ERROR strategy, **When** execution fails, **Then** Result with error_code and recovery_action returned
2. **Given** agent with RETRY strategy, **When** transient error occurs, **Then** automatic retry up to max_attempts
3. **Given** agent with ESCALATE strategy, **When** unrecoverable error, **Then** error propagated to supervisor

### User Story 4 - Skill Dependencies

As an agent, I want to declare required skills so that the engine can validate availability before execution.

**Priority**: P1

**Independent Test**: Declare skill dependency, verify engine validation.

**Acceptance Scenarios**:

1. **Given** agent requires "reasoning" skill, **When** skill unavailable, **Then** execution rejected before start
2. **Given** agent with optional skill, **When** skill available, **Then** skill injected into agent
3. **Given** skill version mismatch, **When** executing, **Then** warning or error raised

---

## Requirements

### Functional Requirements

- **FR-AGENT-001**: Every agent MUST declare a unique name and responsibility statement
- **FR-AGENT-002**: Every agent MUST define input schema (accepted data types)
- **FR-AGENT-003**: Every agent MUST define output schema (produced data types)
- **FR-AGENT-004**: Every agent MUST declare required and optional skills
- **FR-AGENT-005**: Every agent MUST define error handling strategy
- **FR-AGENT-006**: Every agent MUST return structured Result objects
- **FR-AGENT-007**: Every agent MUST implement lifecycle hooks (initialize, execute, cleanup)

### Non-Functional Requirements

- **NFR-AGENT-001**: Agent initialization MUST complete within 100ms
- **NFR-AGENT-002**: Agent execute call MUST have bounded latency (configurable per agent)
- **NFR-AGENT-003**: Agent interfaces MUST be type-safe (Python type hints or schema)
- **NFR-AGENT-004**: Agent results MUST be serializable to JSON
- **NFR-AGENT-005**: Agent names MUST be unique within a registry

---

## Agent Interface Definition

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type
import uuid


class AgentCapability(Enum):
    """Agent capability categories."""
    INTENT_UNDERSTANDING = "intent_understanding"
    SPECIFICATION_SYNTHESIS = "specification_synthesis"
    PLANNING_DECOMPOSITION = "planning_decomposition"
    REASONING_VALIDATION = "reasoning_validation"
    EXECUTION_ORCHESTRATION = "execution_orchestration"
    REFLECTION_IMPROVEMENT = "reflection_improvement"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"


class ErrorStrategy(Enum):
    """Error handling strategies."""
    RETRY = "retry"           # Retry with backoff, then fail
    FALLBACK = "fallback"     # Use alternative approach
    SKIP = "skip"             # Skip the failed step
    ESCALATE = "escalate"     # Propagate to supervisor
    ERROR = "error"           # Return error in result, no retry


class AgentStatus(Enum):
    """Agent lifecycle status."""
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    ERROR = "error"


@dataclass
class AgentInput:
    """Standard input to any agent."""
    task_type: str
    payload: Dict[str, Any]
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None  # SharedContext snapshot
    options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[bool, str]:
        """Validate input has required fields."""
        if not self.task_type:
            return False, "task_type is required"
        if self.payload is None:
            return False, "payload is required"
        return True, "Valid"


@dataclass
class AgentOutput:
    """Standard output from any agent."""
    task_type: str
    payload: Dict[str, Any]
    confidence: float = 1.0  # 0.0 to 1.0
    artifacts: List[str] = field(default_factory=list)  # Artifact IDs
    metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[bool, str]:
        """Validate output has required fields."""
        if not self.task_type:
            return False, "task_type is required"
        if self.payload is None:
            return False, "payload is required"
        if not 0.0 <= self.confidence <= 1.0:
            return False, "confidence must be between 0.0 and 1.0"
        return True, "Valid"


@dataclass
class AgentResult:
    """Structured result from agent execution."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    agent_name: str
    task_type: str
    status: "ResultStatus"  # Reuse from runtime spec
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output: Optional[AgentOutput] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_category: Optional[str] = None
    recovery_action: Optional[str] = None
    duration_ms: int = 0
    confidence: float = 0.0
    artifacts_created: List[str] = field(default_factory=list)
    steps_executed: List[str] = field(default_factory=list)
    context_updates: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        return self.status.value in ["success", "partial"]

    def is_failure(self) -> bool:
        return self.status.value in ["failure", "timeout", "cancelled"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "status": self.status.value,
            "error": self.error,
            "error_code": self.error_code,
            "duration_ms": self.duration_ms,
            "confidence": self.confidence,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class AgentConfig:
    """Configuration for agent initialization."""
    agent_name: str
    max_retries: int = 3
    retry_delay_ms: int = 1000
    timeout_seconds: int = 30
    enable_metrics: bool = True
    enable_tracing: bool = True
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillDependency:
    """Declaration of a skill dependency."""
    skill_name: str
    min_version: Optional[str] = None
    required: bool = True  # False = optional
    injection_method: str = "constructor"  # "constructor", "property", "method_param"


@dataclass
class AgentMetadata:
    """Metadata describing an agent."""
    name: str
    responsibility: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    required_skills: List[SkillDependency] = field(default_factory=list)
    error_strategy: ErrorStrategy = ErrorStrategy.ERROR
    max_input_size_kb: int = 1024
    supported_task_types: List[str] = field(default_factory=list)
    author: str = ""
    license: str = ""
    tags: List[str] = field(default_factory=list)


class SubAgent(ABC):
    """
    Abstract base class for all sub-agents.

    All agents in the intelligence layer MUST implement this interface.
    The engine uses this interface to orchestrate, validate, and compose agents.
    """

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Get agent metadata."""
        ...

    @property
    @abstractmethod
    def status(self) -> AgentStatus:
        """Get current agent status."""
        ...

    @abstractmethod
    def initialize(self, config: AgentConfig, context: "Optional[SharedContext]" = None) -> bool:
        """
        Initialize the agent.

        Called once before any execute calls.
        Load skills, validate dependencies, prepare resources.

        Args:
            config: Agent configuration
            context: Optional shared context for state

        Returns:
            True if initialization successful
        """
        ...

    @abstractmethod
    def execute(self, input: AgentInput) -> AgentResult:
        """
        Execute the agent's primary function.

        Args:
            input: Standardized agent input

        Returns:
            Structured AgentResult
        """
        ...

    @abstractmethod
    def validate_input(self, input: AgentInput) -> tuple[bool, str]:
        """
        Validate input against agent's input schema.

        Args:
            input: Input to validate

        Returns:
            (is_valid, error_message)
        """
        ...

    @abstractmethod
    def validate_output(self, output: AgentOutput) -> tuple[bool, str]:
        """
        Validate output against agent's output schema.

        Args:
            output: Output to validate

        Returns:
            (is_valid, error_message)
        """
        ...

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of capabilities this agent provides."""
        ...

    @abstractmethod
    def can_handle(self, task_type: str, payload: Dict[str, Any]) -> float:
        """
        Check if agent can handle a task.

        Args:
            task_type: Type of task
            payload: Task payload

        Returns:
            Confidence score (0.0 to 1.0)
        """
        ...

    # ==================== Lifecycle Hooks ====================

    @abstractmethod
    def on_start(self, input: AgentInput) -> None:
        """Called before execute begins."""
        ...

    @abstractmethod
    def on_progress(self, progress: float, step: str) -> None:
        """Called during execution to report progress."""
        ...

    @abstractmethod
    def on_complete(self, result: AgentResult) -> None:
        """Called after execute completes (success or failure)."""
        ...

    @abstractmethod
    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Called when an error occurs during execution."""
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources, called during shutdown."""
        ...

    # ==================== Context Integration ====================

    @abstractmethod
    def set_context(self, context: "SharedContext") -> None:
        """Set the shared context for this agent."""
        ...

    @abstractmethod
    def get_context_updates(self) -> Dict[str, Any]:
        """Get updates to apply to shared context."""
        ...

    # ==================== Metrics & Diagnostics ====================

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        ...

    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset execution metrics."""
        ...

    @abstractmethod
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information for debugging."""
        ...
```

---

## Agent Contract Declaration

```python
from dataclasses import dataclass
from typing import Type


@dataclass
class AgentContract:
    """
    Formal contract for an agent's capabilities and requirements.

    Used by the Engine to:
    - Route tasks to appropriate agents
    - Validate skill availability
    - Detect contract violations
    - Generate documentation
    """

    # Identity
    agent_class: Type[SubAgent]
    metadata: AgentMetadata

    # Dependencies
    skills_provided: List[str] = field(default_factory=list)
    skills_consumed: List[str] = field(default_factory=list)

    # Inter-agent contracts
    expects_from: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    produces_for: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Validation
    input_validators: List[str] = field(default_factory=list)
    output_validators: List[str] = field(default_factory=list)

    def validate_skill_availability(self, registry: "SkillRegistry") -> tuple[bool, List[str]]:
        """Check if all required skills are available."""
        missing = []
        for dep in self.metadata.required_skills:
            if dep.required and not registry.has_skill(dep.skill_name):
                missing.append(dep.skill_name)
        return len(missing) == 0, missing

    def validate_data_contract(self, producer: "AgentContract",
                                consumer: "AgentContract") -> bool:
        """Validate producer output matches consumer input."""
        for capability, output_spec in producer.produces_for.items():
            if capability in consumer.expects_from:
                consumer_spec = consumer.expects_from[capability]
                if not self._schemas_compatible(output_spec, consumer_spec):
                    return False
        return True

    def _schemas_compatible(self, a: Dict, b: Dict) -> bool:
        """Check if two schemas are compatible."""
        # Simplified: in practice, use JSON Schema compatibility check
        return True
```

---

## Error Handling Strategy

### Strategy Definitions

| Strategy | Behavior | When to Use |
|----------|----------|-------------|
| **RETRY** | Retry with exponential backoff up to max_retries | Transient failures (network, rate limit) |
| **FALLBACK** | Attempt alternative approach or default value | Multiple ways to achieve goal |
| **SKIP** | Skip this step, continue with next | Non-critical processing steps |
| **ESCALATE** | Propagate error to supervisor/manager | Unrecoverable or requires human input |
| **ERROR** | Return error in result, no retry | Validation errors, invalid input |

### Error Response Format

```python
@dataclass
class ErrorResponse:
    """Standard error response from agent."""
    error_code: str          # E001, E100, etc.
    error_category: str      # validation, routing, execution, timeout, etc.
    error_message: str       # Human-readable description
    recovery_action: str     # Suggested recovery
    retry_recommended: bool = False
    retry_after_seconds: Optional[int] = None
    escalation_target: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def validation_error(cls, message: str, field_name: str) -> "ErrorResponse":
        return cls(
            error_code="E001",
            error_category="validation",
            error_message=message,
            recovery_action=f"Fix field '{field_name}' and retry",
            context={"field_name": field_name}
        )

    @classmethod
    def timeout_error(cls, operation: str, duration: int) -> "ErrorResponse":
        return cls(
            error_code="E300",
            error_category="timeout",
            error_message=f"Operation '{operation}' timed out after {duration}s",
            recovery_action="Increase timeout or simplify operation",
            retry_recommended=True,
            retry_after_seconds=5
        )

    @classmethod
    def skill_not_found(cls, skill_name: str) -> "ErrorResponse":
        return cls(
            error_code="E400",
            error_category="resource",
            error_message=f"Required skill '{skill_name}' not available",
            recovery_action=f"Register skill '{skill_name}' before execution",
            escalation_target="SkillRegistry"
        )
```

### Error Handling Implementation

```python
class ErrorHandler:
    """Standard error handler for agents."""

    def __init__(self, strategy: ErrorStrategy, max_retries: int = 3):
        self.strategy = strategy
        self.max_retries = max_retries
        self.retry_count = 0

    def handle(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        """Handle an error according to the configured strategy."""
        if self.strategy == ErrorStrategy.RETRY:
            return self._handle_retry(error, context)
        elif self.strategy == ErrorStrategy.FALLBACK:
            return self._handle_fallback(error, context)
        elif self.strategy == ErrorStrategy.SKIP:
            return self._handle_skip(error, context)
        elif self.strategy == ErrorStrategy.ESCALATE:
            return self._handle_escalate(error, context)
        else:  # ERROR
            return self._handle_error(error, context)

    def _handle_retry(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            backoff = 2 ** self.retry_count  # Exponential backoff
            return ErrorResponse(
                error_code="E200",
                error_category="execution",
                error_message=str(error),
                recovery_action=f"Retrying in {backoff}s (attempt {self.retry_count}/{self.max_retries})",
                retry_recommended=True,
                retry_after_seconds=backoff
            )
        return ErrorResponse(
            error_code="E200",
            error_category="execution",
            error_message=f"Max retries exceeded: {error}",
            recovery_action="Manual intervention required",
            escalation_target="supervisor"
        )

    def _handle_fallback(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        return ErrorResponse(
            error_code="E200",
            error_category="execution",
            error_message=str(error),
            recovery_action="Using fallback approach",
            context={"fallback_triggered": True}
        )

    def _handle_skip(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        return ErrorResponse(
            error_code="E200",
            error_category="execution",
            error_message=str(error),
            recovery_action="Step skipped, continuing with next",
            context={"skipped": True}
        )

    def _handle_escalate(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        return ErrorResponse(
            error_code="E900",
            error_category="system",
            error_message=str(error),
            recovery_action="Escalated to supervisor",
            escalation_target=context.get("supervisor", "engine")
        )

    def _handle_error(self, error: Exception, context: Dict[str, Any]) -> ErrorResponse:
        return ErrorResponse(
            error_code="E999",
            error_category="execution",
            error_message=str(error),
            recovery_action="Check logs for details"
        )

    def reset(self) -> None:
        """Reset retry count for new execution."""
        self.retry_count = 0
```

---

## Engine Integration

### Agent Invocation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Engine Invocation                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ROUTE                                                        │
│     └── engine.dispatcher.route(task_type, payload)             │
│          └── Returns: (agent_name, confidence)                  │
│                                                                  │
│  2. VALIDATE                                                     │
│     └── agent.validate_input(input)                             │
│          └── Returns: (is_valid, error)                         │
│                                                                  │
│  3. INITIALIZE (first time)                                      │
│     └── agent.initialize(config, context)                       │
│          └── Returns: success                                   │
│                                                                  │
│  4. EXECUTE                                                      │
│     └── agent.execute(input)                                    │
│          └── Returns: AgentResult                               │
│                                                                  │
│  5. VALIDATE OUTPUT                                              │
│     └── agent.validate_output(output)                           │
│          └── Returns: (is_valid, error)                         │
│                                                                  │
│  6. AGGREGATE                                                    │
│     └── engine.aggregate_result(result)                         │
│          └── Returns: EngineResult                              │
│                                                                  │
│  7. CLEANUP (on shutdown)                                        │
│     └── agent.cleanup()                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Engine Interface for Agents

```python
class AgentEngine(ABC):
    """Engine interface for agent management."""

    @abstractmethod
    def register_agent(self, agent: SubAgent, contract: AgentContract) -> bool:
        """Register an agent with the engine."""
        ...

    @abstractmethod
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent."""
        ...

    @abstractmethod
    def get_agent(self, agent_name: str) -> Optional[SubAgent]:
        """Get agent by name."""
        ...

    @abstractmethod
    def find_agent(self, task_type: str, payload: Dict[str, Any]) -> Optional[tuple[SubAgent, float]]:
        """Find best agent for task."""
        ...

    @abstractmethod
    def invoke_agent(self, agent_name: str, input: AgentInput) -> AgentResult:
        """Invoke an agent by name."""
        ...

    @abstractmethod
    def invoke_agents_parallel(self, requests: List[tuple[str, AgentInput]]) -> List[AgentResult]:
        """Invoke multiple agents in parallel."""
        ...

    @abstractmethod
    def validate_skill_chain(self, agents: List[str]) -> tuple[bool, List[str]]:
        """Validate skill dependencies across agent chain."""
        ...

    @abstractmethod
    def shutdown_all(self) -> None:
        """Shutdown all registered agents."""
        ...
```

---

## Complete Agent Example

```python
class ArchitectAgent(SubAgent):
    """
    Agent responsible for high-level architecture design.

    Responsibilities:
    - Analyze requirements for architectural implications
    - Design system architecture
    - Define component interfaces
    - Identify cross-cutting concerns
    """

    def __init__(self):
        self._status = AgentStatus.CREATED
        self._context = None
        self._metrics = {"executions": 0, "total_duration_ms": 0}

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="ArchitectAgent",
            responsibility="Design system architecture and component interfaces",
            version="1.0.0",
            description="Analyzes requirements and produces architectural designs",
            capabilities=[
                AgentCapability.PLANNING_DECOMPOSITION,
                AgentCapability.REASONING_VALIDATION
            ],
            input_schema={
                "type": "object",
                "required": ["requirements"],
                "properties": {
                    "requirements": {
                        "type": "array",
                        "description": "Feature requirements"
                    },
                    "constraints": {
                        "type": "array",
                        "description": "Architectural constraints"
                    }
                }
            },
            output_schema={
                "type": "object",
                "required": ["components", "interfaces"],
                "properties": {
                    "components": {"type": "array"},
                    "interfaces": {"type": "object"},
                    "decisions": {"type": "array"}
                }
            },
            required_skills=[
                SkillDependency("intent_parser", required=True),
                SkillDependency("constraint_validator", required=True)
            ],
            error_strategy=ErrorStrategy.ESCALATE,
            supported_task_types=["architecture_design", "component_design"]
        )

    @property
    def status(self) -> AgentStatus:
        return self._status

    def initialize(self, config: AgentConfig, context: Optional[SharedContext] = None) -> bool:
        self._status = AgentStatus.INITIALIZING
        # Validate skill availability
        # Load templates
        # Prepare resources
        self._status = AgentStatus.READY
        return True

    def execute(self, input: AgentInput) -> AgentResult:
        start_time = datetime.utcnow()
        try:
            # Validate input
            is_valid, error = self.validate_input(input)
            if not is_valid:
                return AgentResult(
                    agent_name=self.metadata.name,
                    task_type=input.task_type,
                    status=ResultStatus.FAILURE,
                    input_summary={"task_type": input.task_type},
                    error=error,
                    error_code="E001",
                    error_category="validation",
                    recovery_action="Fix input and retry",
                    duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )

            self.on_start(input)

            # Main execution logic
            # ...

            output = AgentOutput(
                task_type=input.task_type,
                payload={"components": [], "interfaces": {}},
                confidence=0.95
            )

            result = AgentResult(
                agent_name=self.metadata.name,
                task_type=input.task_type,
                status=ResultStatus.SUCCESS,
                input_summary={"task_type": input.task_type},
                output=output,
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                confidence=output.confidence
            )

            self.on_complete(result)
            return result

        except Exception as e:
            self.on_error(e, {"input": input})
            return AgentResult(
                agent_name=self.metadata.name,
                task_type=input.task_type,
                status=ResultStatus.FAILURE,
                input_summary={"task_type": input.task_type},
                error=str(e),
                error_code="E999",
                error_category="execution",
                recovery_action="Check logs",
                duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )

    def validate_input(self, input: AgentInput) -> tuple[bool, str]:
        if "requirements" not in input.payload:
            return False, "Missing required field: requirements"
        return True, "Valid"

    def validate_output(self, output: AgentOutput) -> tuple[bool, str]:
        if "components" not in output.payload:
            return False, "Missing required output: components"
        return True, "Valid"

    def get_capabilities(self) -> List[AgentCapability]:
        return self.metadata.capabilities

    def can_handle(self, task_type: str, payload: Dict[str, Any]) -> float:
        if task_type not in self.metadata.supported_task_types:
            return 0.0
        if "requirements" not in payload:
            return 0.5  # Partial match
        return 1.0  # Full match

    def on_start(self, input: AgentInput) -> None:
        self._status = AgentStatus.RUNNING

    def on_progress(self, progress: float, step: str) -> None:
        pass  # Log or emit event

    def on_complete(self, result: AgentResult) -> None:
        self._status = AgentStatus.READY
        self._metrics["executions"] += 1
        self._metrics["total_duration_ms"] += result.duration_ms

    def on_error(self, error: Exception, context: Dict[str, Any]) -> None:
        self._status = AgentStatus.ERROR
        # Log error

    def cleanup(self) -> None:
        self._status = AgentStatus.SHUTTING_DOWN
        # Release resources
        self._status = AgentStatus.SHUTDOWN

    def set_context(self, context: "SharedContext") -> None:
        self._context = context

    def get_context_updates(self) -> Dict[str, Any]:
        return {"last_agent": "ArchitectAgent", "last_action": "architecture_design"}

    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics

    def reset_metrics(self) -> None:
        self._metrics = {"executions": 0, "total_duration_ms": 0}

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "status": self._status.value,
            "metrics": self._metrics,
            "metadata_version": self.metadata.version
        }
```

---

## Summary

| Interface Element | Description | Key Methods |
|-------------------|-------------|-------------|
| **Identity** | Name, responsibility, version | `metadata` |
| **Input** | Schema, validation, accepted types | `execute(input)`, `validate_input(input)` |
| **Output** | Schema, validation, produced types | `validate_output(output)` |
| **Skills** | Dependencies, injection | `required_skills` in metadata |
| **Error Handling** | Strategy, response, recovery | `ErrorStrategy`, `ErrorHandler` |
| **Lifecycle** | Initialize, execute, cleanup | `initialize`, `execute`, `cleanup` |
| **Context** | Shared state integration | `set_context`, `get_context_updates` |
| **Metrics** | Diagnostics, performance | `get_metrics`, `get_diagnostics` |

**PHR**: `history/prompts/subagent-interface/001-define-subagent-interface.spec.prompt.md`
