# Core Intelligence Runtime Specification

**Feature Branch**: `feat/core-intelligence-runtime`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define the Core Intelligence Runtime..."

## User Scenarios & Testing

### User Story 1 - Agent Coordination (Priority: P1)

As a developer, I want the runtime to coordinate multiple agents working on a single task so that complex workflows execute correctly.

**Why this priority**: Without coordination, agents would work in isolation, producing inconsistent or conflicting results.

**Independent Test**: Can be tested by invoking multiple agents and verifying correct execution order.

**Acceptance Scenarios**:

1. **Given** 3 agents in a workflow, **When** runtime executes, **Then** dependencies are respected and data flows correctly
2. **Given** agents with shared context, **When** one modifies context, **Then** all subsequent agents see the update
3. **Given** parallelizable agents, **When** executed, **Then** they run concurrently where appropriate

---

### User Story 2 - Context Maintenance (Priority: P1)

As a developer, I want the runtime to maintain shared context across agent invocations so that agents don't need to re-establish state.

**Why this priority**: Context sharing prevents redundant work and enables coherent multi-step operations.

**Independent Test**: Can be tested by invoking agents in sequence and verifying context persistence.

**Acceptance Scenarios**:

1. **Given** context with initial values, **When** agent A modifies context, **Then** agent B sees modified values
2. **Given** context size limit, **When** context exceeds limit, **Then** LRU eviction occurs
3. **Given** context isolation requirement, **When** multiple sessions exist, **Then** each session has isolated context

---

### User Story 3 - Task Routing (Priority: P1)

As a developer, I want the runtime to route tasks to appropriate skills/agents so that I don't need to manually select components.

**Why this priority**: Automatic routing enables high-level task submission without component knowledge.

**Independent Test**: Can be tested by submitting tasks and verifying correct component selection.

**Acceptance Scenarios**:

1. **Given** task "analyze code quality", **When** routed, **Then** task goes to ReviewerAgent
2. **Given** task "parse user intent", **When** routed, **Then** task goes to IntentParser skill
3. **Given** ambiguous task, **When** routed, **Then** routing provides alternatives with confidence scores

---

### User Story 4 - Execution State Tracking (Priority: P1)

As a developer, I want the runtime to track execution state so that I can resume, audit, or debug workflows.

**Why this priority**: State tracking enables resumability, debugging, and compliance auditing.

**Independent Test**: Can be tested by interrupting workflows and resuming from state.

**Acceptance Scenarios**:

1. **Given** workflow in progress, **When** state captured, **Then** workflow can resume from that point
2. **Given** completed workflow, **When** state queried, **Then** complete execution trace is available
3. **Given** failed workflow, **When** state examined, **Then** failure point and reason are clear

---

### User Story 5 - Introspection and Debugging (Priority: P2)

As a developer, I want the runtime to provide introspection capabilities so that I can debug issues and understand system behavior.

**Why this priority**: Debugging complex agent systems requires visibility into internal state and execution.

**Independent Test**: Can be tested by querying runtime state and verifying introspection data.

**Acceptance Scenarios**:

1. **Given** running workflow, **When** introspected, **Then** current step, context, and state are visible
2. **Given** completed workflow, **When** debugging, **Then** full execution trace with timing is available
3. **Given** performance issue, **When** profiled, **Then** bottlenecks are identified

---

## Requirements

### Functional Requirements

- **FR-RT-001**: Runtime MUST coordinate sub-agents through a central Engine
- **FR-RT-002**: Runtime MUST maintain shared context accessible to all components
- **FR-RT-003**: Runtime MUST route tasks to appropriate skills/agents based on capability
- **FR-RT-004**: Runtime MUST track execution state with checkpoint/restore capability
- **FR-RT-005**: Runtime MUST support introspection and debugging
- **FR-RT-006**: Runtime MUST handle errors consistently across all components
- **FR-RT-007**: Runtime MUST provide structured I/O contracts for all operations

### Non-Functional Requirements

- **NFR-RT-001**: Runtime initialization MUST complete within 500ms
- **NFR-RT-002**: Task routing MUST complete within 50ms
- **NFR-RT-003**: Context operations MUST complete within 10ms
- **NFR-RT-004**: Runtime MUST support 100+ concurrent sessions
- **NFR-RT-005**: State snapshots MUST be serializable to JSON

### Key Entities

- **Engine**: Central orchestration controller
- **Context**: Shared execution context
- **Dispatcher**: Task routing and execution
- **Registry**: Component discovery and management
- **Result**: Structured execution result

---

## Core Runtime Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Core Intelligence Runtime                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐   │
│  │   Engine    │────►│  Dispatcher │────►│     Registry        │   │
│  │  (Orchestrates)    │  (Routes)        │   (Discovers)        │   │
│  └─────────────┘     └───────┬─────┘     └─────────────────────┘   │
│         │                    │                                      │
│         │                    ▼                                      │
│         │           ┌─────────────┐                                 │
│         │           │   Context   │                                 │
│         │           │  (Shared)   │                                 │
│         │           └──────┬──────┘                                 │
│         │                  │                                         │
│         ▼                  ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Component Layer                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │  Skills  │  │  Agents  │  │Templates │  │Evaluators│    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Engine Component

### Purpose
Central orchestration controller that manages the entire runtime lifecycle.

### Engine Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class EngineState(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Engine configuration."""
    engine_id: str = "core-runtime"
    version: str = "1.0.0"
    max_concurrent_sessions: int = 100
    context_ttl_seconds: int = 3600
    context_max_size_mb: int = 10
    checkpoint_interval_seconds: int = 60
    enable_introspection: bool = True
    enable_debugging: bool = True
    log_level: str = "INFO"
    registry_path: str = "./intelligence"


@dataclass
class Session:
    """Execution session."""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    state: Dict[str, Any] = field(default_factory=dict)
    context: "Context" = None
    status: str = "active"


class Engine(ABC):
    """Core Intelligence Runtime Engine."""

    @property
    @abstractmethod
    def config(self) -> EngineConfig:
        """Engine configuration."""
        ...

    @property
    @abstractmethod
    def state(self) -> EngineState:
        """Current engine state."""
        ...

    @property
    @abstractmethod
    def context(self) -> "Context":
        """Global context manager."""
        ...

    @property
    @abstractmethod
    def dispatcher(self) -> "Dispatcher":
        """Task dispatcher."""
        ...

    @property
    @abstractmethod
    def registry(self) -> "Registry":
        """Component registry."""
        ...

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the engine and all components."""
        ...

    @abstractmethod
    def start(self) -> bool:
        """Start accepting requests."""
        ...

    @abstractmethod
    def pause(self) -> bool:
        """Pause processing (queue requests)."""
        ...

    @abstractmethod
    def shutdown(self, graceful: bool = True) -> bool:
        """Shutdown the engine."""
        ...

    @abstractmethod
    def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create a new execution session."""
        ...

    @abstractmethod
    def execute(self, session_id: str, task: Dict[str, Any]) -> "Result":
        """Execute a task in a session."""
        ...

    @abstractmethod
    def execute_pipeline(
        self,
        session_id: str,
        pipeline: List[Dict[str, Any]]
    ) -> "Result":
        """Execute a pipeline of tasks."""
        ...

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get engine state for introspection."""
        ...

    @abstractmethod
    def introspect(self, session_id: str) -> Dict[str, Any]:
        """Introspect a session."""
        ...
```

### Lifecycle Stages

```
┌─────────┐    ┌─────────────┐    ┌─────────┐    ┌─────────────┐
│ CREATED │───►│INITIALIZING │───►│  IDLE   │───►│  RUNNING    │
└─────────┘    └─────────────┘    └─────────┘    └──────┬──────┘
     │               │                │                  │
     │               │                │                  │
     ▼               ▼                ▼                  ▼
┌─────────┐    ┌─────────────┐    ┌─────────┐    ┌─────────────┐
│ FAILED  │    │ TIMEOUT     │    │ PAUSED  │    │ SHUTTING    │
│ (init   │    │ (init fail) │    │ (pause) │    │  DOWN       │
│ error)  │    │             │    │         │    │             │
└─────────┘    └─────────────┘    └─────────┘    └──────┬──────┘
                                                       │
                                                       ▼
                                                ┌─────────┐
                                                │ SHUTDOWN│
                                                └─────────┘
```

---

## 2. Context Component

### Purpose
Maintains shared execution context accessible to all components.

### Context Interface

```python
@dataclass
class ContextEntry:
    """Individual context entry."""
    key: str
    value: Any
    scope: str = "session"  # "global", "session", "task"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    encrypted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > self.ttl_seconds


class Context:
    """Shared execution context."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        ...

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        scope: str = "session",
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set value in context."""
        ...

    @abstractmethod
    def delete(self, key: str, scope: str = "session") -> bool:
        """Delete value from context."""
        ...

    @abstractmethod
    def exists(self, key: str, scope: str = "session") -> bool:
        """Check if key exists."""
        ...

    @abstractmethod
    def clear(self, scope: str = "session") -> int:
        """Clear context by scope."""
        ...

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]:
        """Create context snapshot."""
        ...

    @abstractmethod
    def restore(self, data: Dict[str, Any]) -> bool:
        """Restore context from snapshot."""
        ...

    @abstractmethod
    def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Get all context entries."""
        ...

    @abstractmethod
    def import_data(self, data: Dict[str, Any], scope: str = "session") -> int:
        """Import external data into context."""
        ...

    @abstractmethod
    def export_data(self, scope: str = "session") -> Dict[str, Any]:
        """Export context data."""
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        ...
```

### Context Scopes

| Scope | Visibility | Lifetime | Use Case |
|-------|-----------|----------|----------|
| **global** | All sessions | Engine lifetime | Configuration, constants |
| **session** | Single session | Session lifetime | Session-specific data |
| **task** | Single task | Task lifetime | Task-specific data |

---

## 3. Dispatcher Component

### Purpose
Routes tasks to appropriate skills/agents based on capability matching.

### Dispatcher Interface

```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    target_name: str
    target_type: str  # "skill", "agent", "template"
    confidence: float  # 0.0 to 1.0
    routing_reason: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    estimated_duration_ms: int = 0
    required_context: List[str] = field(default_factory=list)


@dataclass
class DispatchRequest:
    """Request to dispatch."""
    task_type: str
    payload: Dict[str, Any]
    session_id: str
    priority: int = 0  # Higher = more urgent
    timeout_seconds: int = 30
    allow_fallback: bool = True


class Dispatcher:
    """Task dispatcher."""

    @abstractmethod
    def dispatch(self, request: DispatchRequest) -> "Result":
        """Dispatch a task to appropriate component."""
        ...

    @abstractmethod
    def route(self, task_type: str, payload: Dict[str, Any]) -> RoutingDecision:
        """Route a task to appropriate component."""
        ...

    @abstractmethod
    def can_handle(self, component: str, task_type: str) -> bool:
        """Check if component can handle task type."""
        ...

    @abstractmethod
    def get_capable_components(self, task_type: str) -> List[str]:
        """Get components capable of handling task type."""
        ...

    @abstractmethod
    def execute_parallel(
        self,
        requests: List[DispatchRequest]
    ) -> List["Result"]:
        """Execute multiple requests in parallel."""
        ...

    @abstractmethod
    def execute_sequential(
        self,
        requests: List[DispatchRequest]
    ) -> List["Result"]:
        """Execute multiple requests sequentially."""
        ...
```

### Routing Strategies

```python
class RoutingStrategy(Enum):
    CAPABILITY_MATCH = "capability_match"  # Best capability match
    PRIORITY = "priority"  # Highest priority component
    LOAD_BALANCED = "load_balanced"  # Round-robin across capable
    AFFINITY = "affinity"  # Prefer same component as before
    FALLBACK = "fallback"  # Try primary, then fallback


class CapabilityMatcher:
    """Matches tasks to components based on capabilities."""

    def match(
        self,
        task_type: str,
        payload: Dict[str, Any],
        registry: "Registry"
    ) -> List[tuple[str, float]]:
        """Match task to capable components with confidence scores."""
        # Implementation
        ...
```

---

## 4. Registry Component

### Purpose
Discovers, registers, and manages skills, agents, templates, and evaluators.

### Registry Interface

```python
@dataclass
class ComponentMetadata:
    """Metadata for a registered component."""
    name: str
    type: str  # "skill", "agent", "template", "evaluator"
    version: str
    description: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    author: str = ""
    license: str = ""
    tags: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComponentInstance:
    """Instantiated component."""
    metadata: ComponentMetadata
    instance: Any
    load_time: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    use_count: int = 0
    health_status: str = "healthy"
    load: float = 0.0  # Current load (0.0 to 1.0)


class Registry:
    """Component registry."""

    @abstractmethod
    def register(self, component: Any, metadata: ComponentMetadata) -> bool:
        """Register a component."""
        ...

    @abstractmethod
    def unregister(self, name: str) -> bool:
        """Unregister a component."""
        ...

    @abstractmethod
    def get(self, name: str) -> Optional[ComponentInstance]:
        """Get component by name."""
        ...

    @abstractmethod
    def find_by_type(self, component_type: str) -> List[ComponentMetadata]:
        """Find components by type."""
        ...

    @abstractmethod
    def find_by_capability(self, capability: str) -> List[ComponentMetadata]:
        """Find components by capability."""
        ...

    @abstractmethod
    def find_by_tag(self, tag: str) -> List[ComponentMetadata]:
        """Find components by tag."""
        ...

    @abstractmethod
    def list_all(self) -> List[ComponentMetadata]:
        """List all registered components."""
        ...

    @abstractmethod
    def discover(self, paths: List[str]) -> int:
        """Discover components from paths."""
        ...

    @abstractmethod
    def reload(self, name: str) -> bool:
        """Hot-reload a component."""
        ...

    @abstractmethod
    def health_check(self, name: str) -> Dict[str, Any]:
        """Check component health."""
        ...

    @abstractmethod
    def get_load(self, name: str) -> float:
        """Get component current load."""
        ...
```

---

## 5. Result Component

### Purpose
Encapsulates structured execution results with success/failure information.

### Result Interface

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResultStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ComponentResult:
    """Result from a single component."""
    component_name: str
    component_type: str
    status: ResultStatus
    output: Any = None
    duration_ms: int = 0
    error: Optional[str] = None
    error_code: Optional[str] = None
    artifacts_created: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStep:
    """Individual execution step."""
    step_id: str
    step_type: str
    component_name: str
    status: ResultStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: int = 0
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Result:
    """Complete execution result."""
    result_id: str
    session_id: str
    status: ResultStatus
    overall_score: Optional[float] = None  # 0.0 to 1.0
    components: List[ComponentResult] = field(default_factory=list)
    steps: List[ExecutionStep] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)  # name -> path
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None
    error_code: Optional[str] = None
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS

    def is_failure(self) -> bool:
        return self.status in [ResultStatus.FAILURE, ResultStatus.TIMEOUT, ResultStatus.CANCELLED]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "result_id": self.result_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "overall_score": self.overall_score,
            "components": [
                {
                    "component_name": c.component_name,
                    "status": c.status.value,
                    "duration_ms": c.duration_ms
                }
                for c in self.components
            ],
            "duration_ms": self.duration_ms,
            "error": self.error,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Result":
        """Deserialize from dictionary."""
        ...
```

---

## Input/Output Contracts

### Engine Input Contract

```python
@dataclass
class EngineInput:
    """Input to the engine."""
    session_id: str
    task_type: str
    payload: Dict[str, Any]
    options: Dict[str, Any] = field(default_factory=dict)

    # Options
    routing_strategy: str = "capability_match"
    timeout_seconds: int = 30
    priority: int = 0
    allow_parallel: bool = False
    checkpoint_enabled: bool = True
    introspection_enabled: bool = False

    def validate(self) -> tuple[bool, str]:
        if not self.session_id:
            return False, "session_id is required"
        if not self.task_type:
            return False, "task_type is required"
        if not self.payload:
            return False, "payload is required"
        return True, "Valid"
```

### Engine Output Contract

```python
@dataclass
class EngineOutput:
    """Output from the engine."""
    result: Result
    session_state: Dict[str, Any]
    context_snapshot: Dict[str, Any]
    trace_id: Optional[str] = None
    execution_metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[bool, str]:
        if not self.result:
            return False, "result is required"
        if not self.session_state:
            return False, "session_state is required"
        return True, "Valid"
```

---

## Error Handling Rules

### Error Taxonomy

```python
class ErrorCategory(Enum):
    VALIDATION = "validation"  # Input validation failed
    ROUTING = "routing"  # No capable component found
    EXECUTION = "execution"  # Component execution failed
    TIMEOUT = "timeout"  # Operation timed out
    RESOURCE = "resource"  # Resource constraint
    STATE = "state"  # Invalid state transition
    SYSTEM = "system"  # Internal system error


class ErrorCode:
    """Standard error codes."""
    VALIDATION_INVALID_INPUT = ("E001", "Invalid input", ErrorCategory.VALIDATION)
    ROUTING_NO_CAPABLE_COMPONENT = ("E100", "No capable component", ErrorCategory.ROUTING)
    EXECUTION_COMPONENT_FAILED = ("E200", "Component execution failed", ErrorCategory.EXECUTION)
    TIMEOUT_EXCEEDED = ("E300", "Operation timed out", ErrorCategory.TIMEOUT)
    RESOURCE_EXHAUSTED = ("E400", "Resource exhausted", ErrorCategory.RESOURCE)
    STATE_INVALID_TRANSITION = ("E500", "Invalid state transition", ErrorCategory.STATE)
    SYSTEM_INTERNAL_ERROR = ("E999", "Internal system error", ErrorCategory.SYSTEM)


@dataclass
class RuntimeError:
    """Runtime error."""
    error_code: str
    error_message: str
    category: ErrorCategory
    component: Optional[str]
    recovery_action: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
```

### Error Handling Rules

| Rule | Description |
|------|-------------|
| **Rule 1** | All errors MUST be categorized using ErrorCategory |
| **Rule 2** | All errors MUST include error code and message |
| **Rule 3** | All errors MUST include recovery action suggestion |
| **Rule 4** | Validation errors MUST fail fast before execution |
| **Rule 5** | Component errors MUST be caught and wrapped in Result |
| **Rule 6** | Timeout errors MUST include elapsed time |
| **Rule 7** | System errors MUST be logged with full context |
| **Rule 8** | Recovery action MUST be suggested for all errors |
| **Rule 9** | Errors MUST be serializable for debugging |
| **Rule 10** | Error context MUST not include sensitive data |

### Error Recovery Strategies

```python
class ErrorRecoveryStrategy(Enum):
    RETRY = "retry"  # Retry the operation
    FALLBACK = "fallback"  # Use fallback component
    SKIP = "skip"  # Skip the operation
    ABORT = "abort"  # Abort the entire workflow
    MANUAL = "manual"  # Require manual intervention


class ErrorHandler:
    """Error handler for runtime errors."""

    def handle(self, error: RuntimeError, context: Dict[str, Any]) -> ErrorRecoveryStrategy:
        """Determine recovery strategy for error."""
        # Rule-based recovery
        if error.category == ErrorCategory.VALIDATION:
            return ErrorRecoveryStrategy.ABORT
        elif error.category == ErrorCategory.TIMEOUT:
            return ErrorRecoveryStrategy.RETRY
        elif error.category == ErrorCategory.EXECUTION:
            return ErrorRecoveryStrategy.FALLBACK
        else:
            return ErrorRecoveryStrategy.MANUAL
```

---

## Complete Runtime Implementation

```python
class CoreIntelligenceRuntime(Engine):
    """Complete Core Intelligence Runtime implementation."""

    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self._state = EngineState.CREATED

        # Components
        self._context: Optional[Context] = None
        self._registry: Optional[Registry] = None
        self._dispatcher: Optional[Dispatcher] = None

        # Internal state
        self._sessions: Dict[str, Session] = {}
        self._result_cache: Dict[str, Result] = {}
        self._execution_traces: Dict[str, List[ExecutionStep]] = {}

    @property
    def config(self) -> EngineConfig:
        return self._config

    @property
    def state(self) -> EngineState:
        return self._state

    @property
    def context(self) -> Context:
        if self._context is None:
            raise RuntimeError("Engine not initialized")
        return self._context

    @property
    def dispatcher(self) -> Dispatcher:
        if self._dispatcher is None:
            raise RuntimeError("Engine not initialized")
        return self._dispatcher

    @property
    def registry(self) -> Registry:
        if self._registry is None:
            raise RuntimeError("Engine not initialized")
        return self._registry

    def initialize(self) -> bool:
        """Initialize the engine."""
        try:
            self._state = EngineState.INITIALIZING

            # Initialize context
            self._context = InMemoryContext(self.config)

            # Initialize registry and discover components
            self._registry = ComponentRegistry(self.config)
            discovered = self._registry.discover([self.config.registry_path])

            # Initialize dispatcher
            self._dispatcher = TaskDispatcher(self.config, self._registry)

            # Initialize context with engine metadata
            self.context.set("engine", {
                "id": self.config.engine_id,
                "version": self.config.version,
                "initialized_at": datetime.utcnow().isoformat()
            }, scope="global")

            self._state = EngineState.IDLE
            return True

        except Exception as e:
            self._state = EngineState.ERROR
            raise RuntimeError(f"Initialization failed: {e}")

    def start(self) -> bool:
        """Start accepting requests."""
        if self._state != EngineState.IDLE:
            raise RuntimeError(f"Cannot start from state: {self._state}")
        self._state = EngineState.RUNNING
        return True

    def pause(self) -> bool:
        """Pause processing."""
        if self._state != EngineState.RUNNING:
            raise RuntimeError(f"Cannot pause from state: {self._state}")
        self._state = EngineState.PAUSED
        return True

    def shutdown(self, graceful: bool = True) -> bool:
        """Shutdown the engine."""
        if self._state in [EngineState.SHUTDOWN, EngineState.SHUTTING_DOWN]:
            return True

        self._state = EngineState.SHUTTING_DOWN

        # Finalize all sessions
        for session in self._sessions.values():
            self._finalize_session(session)

        # Shutdown components
        self._context = None
        self._registry = None
        self._dispatcher = None

        self._state = EngineState.SHUTDOWN
        return True

    def create_session(self, user_id: Optional[str] = None) -> Session:
        """Create a new execution session."""
        session = Session(
            session_id=self._generate_session_id(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            context=self.context,
            status="active"
        )
        self._sessions[session.session_id] = session
        return session

    def execute(self, session_id: str, task: Dict[str, Any]) -> Result:
        """Execute a task in a session."""
        if self._state not in [EngineState.IDLE, EngineState.RUNNING]:
            raise RuntimeError(f"Engine not ready: {self._state}")

        session = self._sessions.get(session_id)
        if not session:
            raise RuntimeError(f"Session not found: {session_id}")

        # Validate input
        input_data = EngineInput(
            session_id=session_id,
            task_type=task.get("type", "default"),
            payload=task.get("payload", {}),
            options=task.get("options", {})
        )
        is_valid, error = input_data.validate()
        if not is_valid:
            return Result(
                result_id=self._generate_result_id(),
                session_id=session_id,
                status=ResultStatus.FAILURE,
                error=error,
                error_code="E001"
            )

        # Route task
        routing_decision = self._dispatcher.route(
            input_data.task_type,
            input_data.payload
        )

        # Execute
        start_time = datetime.utcnow()
        try:
            component_result = self._dispatcher.dispatch(DispatchRequest(
                task_type=input_data.task_type,
                payload=input_data.payload,
                session_id=session_id,
                timeout_seconds=input_data.timeout_seconds
            ))

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            return Result(
                result_id=self._generate_result_id(),
                session_id=session_id,
                status=ResultStatus.SUCCESS if component_result.status == ResultStatus.SUCCESS else ResultStatus.PARTIAL,
                components=[component_result],
                duration_ms=int(duration_ms),
                context_snapshot=self.context.snapshot()
            )

        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return Result(
                result_id=self._generate_result_id(),
                session_id=session_id,
                status=ResultStatus.FAILURE,
                error=str(e),
                error_code="E999",
                duration_ms=int(duration_ms)
            )

    def execute_pipeline(
        self,
        session_id: str,
        pipeline: List[Dict[str, Any]]
    ) -> Result:
        """Execute a pipeline of tasks."""
        results = []
        for task in pipeline:
            result = self.execute(session_id, task)
            results.append(result)
            if result.is_failure():
                # Stop on first failure
                break

        return Result(
            result_id=self._generate_result_id(),
            session_id=session_id,
            status=ResultStatus.SUCCESS if all(r.is_success() for r in results) else ResultStatus.PARTIAL,
            components=[r.components[0] for r in results if r.components],
            duration_ms=sum(r.duration_ms for r in results)
        )

    def get_state(self) -> Dict[str, Any]:
        """Get engine state for introspection."""
        return {
            "state": self._state.value,
            "config": {
                "engine_id": self.config.engine_id,
                "version": self.config.version
            },
            "sessions_active": len([s for s in self._sessions.values() if s.status == "active"]),
            "components_registered": len(self.registry.list_all()),
            "context_size": self.context.get_stats()["entry_count"],
            "timestamp": datetime.utcnow().isoformat()
        }

    def introspect(self, session_id: str) -> Dict[str, Any]:
        """Introspect a session."""
        session = self._sessions.get(session_id)
        if not session:
            raise RuntimeError(f"Session not found: {session_id}")

        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "status": session.status,
            "context": self.context.get_all(scope="session"),
            "state": session.state,
            "components": [c.metadata.name for c in self.registry.list_all()],
            "engine_state": self.get_state()
        }

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"session-{uuid.uuid4().hex[:12]}"

    def _generate_result_id(self) -> str:
        """Generate unique result ID."""
        import uuid
        return f"result-{uuid.uuid4().hex[:12]}"

    def _finalize_session(self, session: Session) -> None:
        """Finalize a session."""
        session.status = "finalized"
        # Snapshot context
        self.context.set(f"session_{session.session_id}_final", {
            "context": self.context.snapshot(),
            "state": session.state,
            "finalized_at": datetime.utcnow().isoformat()
        }, scope="global")
```

---

## Summary

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **Engine** | Central orchestration | initialize, execute, execute_pipeline, introspect |
| **Context** | Shared state | get, set, snapshot, restore |
| **Dispatcher** | Task routing | dispatch, route, execute_parallel |
| **Registry** | Component management | register, discover, health_check |
| **Result** | Execution outcome | is_success, to_dict, from_dict |

**PHR**: `history/prompts/core-intelligence-runtime/001-define-core-intelligence-runtime.spec.prompt.md`
