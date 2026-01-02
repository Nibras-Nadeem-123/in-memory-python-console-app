# Core Intelligence Engine Specification

**Feature Branch**: `feat/core-intelligence-engine`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Define the Core Intelligence Engine..."

## User Scenarios & Testing

### User Story 1 - Intent Routing (Priority: P1)

As a user, I want to submit my intent to a single entry point so that the system automatically routes it to the appropriate agents and skills.

**Why this priority**: The Core Engine is the single point of entry. Without proper routing, users would need to manually invoke specific components.

**Independent Test**: Can be tested by submitting various intents and verifying correct component routing.

**Acceptance Scenarios**:

1. **Given** intent "create a new feature for user authentication", **When** processed by Core Engine, **Then** intent is routed to Architect Agent for design
2. **Given** intent "show me the current architecture", **When** processed, **Then** intent is routed to Reflector Agent for analysis
3. **Given** intent that requires multiple components, **When** processed, **Then** components are invoked in correct dependency order

---

### User Story 2 - Shared Context Maintenance (Priority: P1)

As a user, I want the system to maintain context across interactions so that subsequent requests understand prior state.

**Why this priority**: Without shared context, each request is treated as independent, losing valuable state and requiring repetitive information.

**Independent Test**: Can be tested by submitting related intents and verifying context preservation.

**Acceptance Scenarios**:

1. **Given** previous intent established project context, **When** new intent is submitted, **Then** context includes project information
2. **Given** multiple intents in a session, **When** context is maintained, **Then** all components see consistent context
3. **Given** context exceeds size limits, **When** new items added, **Then** least-recently-used items are evicted

---

### User Story 3 - Constraint Enforcement (Priority: P1)

As a user, I want the system to enforce execution constraints so that I can rely on predictable, safe behavior.

**Why this priority**: Constraints ensure safety, resource limits, and ordering requirements are respected.

**Independent Test**: Can be tested by submitting intents that violate constraints and verifying enforcement.

**Acceptance Scenarios**:

1. **Given** constraint "max execution time 30s", **When** operation exceeds limit, **Then** operation is terminated with timeout
2. **Given** constraint "step A before step B", **When** step B is invoked before A, **Then** step A is executed first
3. **Given** constraint "single agent per type", **When** multiple requests target same agent, **Then** requests are serialized

---

### User Story 4 - Deterministic Execution (Priority: P1)

As a user, I want the system to produce consistent, reproducible results so that I can rely on deterministic behavior.

**Why this priority**: Determinism enables testing, debugging, and user trust. Non-deterministic systems are unpredictable.

**Independent Test**: Can be tested by submitting identical intents multiple times and verifying identical outputs.

**Acceptance Scenarios**:

1. **Given** identical intent submitted twice, **When** processed, **Then** outputs are byte-for-byte identical
2. **Given** system state changes between requests, **When** intent is re-submitted, **Then** output reflects only intent, not system state
3. **Given** random inputs are required, **When** seeded identically, **Then** outputs are identical

---

### User Story 5 - Execution Inspection (Priority: P2)

As a developer, I want to inspect the execution trace so that I can debug issues and understand system behavior.

**Why this priority**: Inspection enables debugging, optimization, and user understanding of system decisions.

**Independent Test**: Can be tested by submitting intent and verifying complete execution trace.

**Acceptance Scenarios**:

1. **Given** intent processing completed, **When** inspection requested, **Then** trace shows all components invoked
2. **Given** execution failed, **When** inspected, **Then** trace shows failure point and reason
3. **Given** complex workflow, **When** visualized, **Then** component interactions are clear

---

### Edge Cases

- What happens when no component can handle an intent?
- How are circular dependencies in routing detected?
- What happens when memory is exhausted?
- How are conflicting constraints resolved?
- What happens during graceful and forced shutdown?

## Requirements

### Functional Requirements

- **FR-ENG-001**: Core Engine MUST provide single entry point for all user intents
- **FR-ENG-002**: Core Engine MUST route intents to appropriate skills/agents based on capability matching
- **FR-ENG-003**: Core Engine MUST maintain shared context accessible to all components
- **FR-ENG-004**: Core Engine MUST provide persistent memory across sessions
- **FR-ENG-005**: Core Engine MUST enforce execution constraints (time, order, resources)
- **FR-ENG-006**: Core Engine MUST produce deterministic outputs for identical inputs
- **FR-ENG-007**: Core Engine MUST provide complete execution trace for inspection
- **FR-ENG-008**: Core Engine MUST be reusable across all projects without modification
- **FR-ENG-009**: Core Engine MUST support hot-reload of components without restart
- **FR-ENG-010**: Core Engine MUST support graceful and forced shutdown

### Non-Functional Requirements

- **NFR-ENG-001**: Core Engine MUST initialize within 1 second
- **NFR-ENG-002**: Intent routing MUST complete within 50ms
- **NFR-ENG-003**: Context operations MUST complete within 10ms
- **NFR-ENG-004**: Engine MUST support at least 100 concurrent sessions
- **NFR-ENG-005**: Memory footprint MUST stay under 100MB for idle state
- **NFR-ENG-006**: All operations MUST be logged for audit purposes

### Key Entities

- **CoreEngine**: Central orchestration controller
- **IntentRouter**: Routes intents to appropriate components
- **ContextManager**: Maintains shared execution context
- **MemoryStore**: Persistent storage for learned information
- **ConstraintEnforcer**: Validates and enforces execution constraints
- **ExecutionTrace**: Complete record of execution for inspection
- **ComponentRegistry**: Discovers and manages skills, agents, templates

## Success Criteria

- **SC-ENG-001**: Core Engine can process any intent without domain-specific code
- **SC-ENG-002**: Routing correctly identifies capable components 99%+ of the time
- **SC-ENG-003**: Identical intents produce identical outputs
- **SC-ENG-004**: Execution trace provides complete visibility into all operations
- **SC-ENG-005**: Components can be added/removed without engine restart

---

## Core Engine Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Core Intelligence Engine                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │   Intent      │  │   Context     │  │   Memory          │   │
│  │   Router      │  │   Manager     │  │   Store           │   │
│  └───────┬───────┘  └───────┬───────┘  └─────────┬─────────┘   │
│          │                  │                    │              │
│          ▼                  ▼                    ▼              │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              Component Registry                        │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │     │
│  │  │ Skills  │ │ Agents  │ │Templates│ │ Evaluators│    │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │     │
│  └───────────────────────────────────────────────────────┘     │
│          │                  │                    │              │
│          ▼                  ▼                    ▼              │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              Constraint Enforcer                       │     │
│  └───────────────────────────────────────────────────────┘     │
│          │                                                     │
│          ▼                                                     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              Execution Trace                           │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Engine Interface

### Engine Configuration

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Configuration for the Core Intelligence Engine."""
    # Core settings
    engine_id: str = "core-engine"
    version: str = "1.0.0"
    log_level: LogLevel = LogLevel.INFO

    # Routing configuration
    default_agent: str = "architect_agent"
    routing_strategy: str = "capability-match"  # "capability-match", "round-robin", "priority"

    # Context configuration
    context_max_size_mb: int = 10
    context_ttl_seconds: int = 3600

    # Memory configuration
    memory_backend: str = "in-memory"  # "in-memory", "disk", "distributed"
    memory_persistence_path: Optional[str] = None
    memory_max_entries: int = 10000

    # Constraint configuration
    max_execution_time_seconds: int = 300
    max_concurrent_operations: int = 10
    constraint_strict_mode: bool = True

    # Inspection configuration
    trace_enabled: bool = True
    trace_depth: str = "full"  # "minimal", "standard", "full"
    trace_storage: str = "memory"  # "memory", "disk", "external"

    # Component configuration
    component_scan_paths: List[str] = field(default_factory=lambda: ["skills", "agents", "templates"])
    hot_reload_enabled: bool = True
    component_timeout_seconds: int = 30
```

### Intent Input

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class UserIntent:
    """User input to the Core Engine."""
    raw_text: str
    session_id: str
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0  # 0=normal, higher=more urgent
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.raw_text:
            raise ValueError("raw_text cannot be empty")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")


@dataclass
class EngineInput:
    """Complete input to the Core Engine."""
    intent: UserIntent
    context_overrides: Dict[str, Any] = field(default_factory=dict)
    constraints: List["Constraint"] = field(default_factory=list)
    callbacks: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[bool, str]:
        """Validate input."""
        if not self.intent.raw_text.strip():
            return False, "Intent text cannot be empty"
        if not self.intent.session_id:
            return False, "Session ID is required"
        return True, "Valid"
```

### Structured Output

```python
@dataclass
class ComponentResult:
    """Result from a single component execution."""
    component_name: str
    component_type: str  # "skill", "agent", "template"
    status: str  # "success", "partial", "failed", "skipped"
    output: Any
    duration_ms: int
    error: Optional[str] = None
    artifacts_created: List[str] = field(default_factory=list)


@dataclass
class ExecutionSummary:
    """Summary of engine execution."""
    total_duration_ms: int
    components_invoked: List[str]
    success_count: int
    failure_count: int
    skip_count: int
    memory_delta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineOutput:
    """Complete output from the Core Engine."""
    status: str  # "success", "partial", "failed"
    primary_output: Any
    results: List[ComponentResult] = field(default_factory=list)
    summary: ExecutionSummary = None
    trace_id: str = ""
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.summary is None:
            self.summary = ExecutionSummary(
                total_duration_ms=0,
                components_invoked=[],
                success_count=0,
                failure_count=0,
                skip_count=0
            )
```

### Core Engine Interface

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator


class CoreEngine(ABC):
    """Core Intelligence Engine - central orchestration controller."""

    @property
    @abstractmethod
    def config(self) -> EngineConfig:
        """Engine configuration."""
        ...

    @property
    @abstractmethod
    def context_manager(self) -> "ContextManager":
        """Access to context management."""
        ...

    @property
    @abstractmethod
    def memory_store(self) -> "MemoryStore":
        """Access to persistent memory."""
        ...

    @property
    @abstractmethod
    def component_registry(self) -> "ComponentRegistry":
        """Access to component registry."""
        ...

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the engine and all components."""
        ...

    @abstractmethod
    def shutdown(self, graceful: bool = True) -> None:
        """Shutdown the engine."""
        ...

    @abstractmethod
    def process(self, input: EngineInput) -> EngineOutput:
        """Process a single intent synchronously."""
        ...

    @abstractmethod
    def process_stream(self, input: EngineInput) -> AsyncIterator[ComponentResult]:
        """Process intent with streaming results."""
        ...

    @abstractmethod
    def get_trace(self, trace_id: str) -> "ExecutionTrace":
        """Retrieve execution trace for inspection."""
        ...

    @abstractmethod
    def add_constraint(self, constraint: "Constraint") -> bool:
        """Add an execution constraint."""
        ...

    @abstractmethod
    def remove_constraint(self, constraint_id: str) -> bool:
        """Remove an execution constraint."""
        ...
```

---

## Component Registry

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type


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


@dataclass
class ComponentInstance:
    """Instantiated component with metadata."""
    metadata: ComponentMetadata
    instance: Any
    load_time: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    use_count: int = 0
    health_status: str = "healthy"


class ComponentRegistry(ABC):
    """Discovers, registers, and manages components."""

    @abstractmethod
    def register(self, component: Any, metadata: ComponentMetadata) -> bool:
        """Register a component."""
        ...

    @abstractmethod
    def unregister(self, name: str) -> bool:
        """Unregister a component."""
        ...

    @abstractmethod
    def get(self, name: str) -> ComponentInstance:
        """Get component by name."""
        ...

    @abstractmethod
    def find_by_capability(self, capability: str) -> List[ComponentMetadata]:
        """Find components with specific capability."""
        ...

    @abstractmethod
    def find_by_type(self, type: str) -> List[ComponentMetadata]:
        """Find components by type."""
        ...

    @abstractmethod
    def list_all(self) -> List[ComponentMetadata]:
        """List all registered components."""
        ...

    @abstractmethod
    def discover(self, paths: List[str]) -> int:
        """Discover components from file paths."""
        ...

    @abstractmethod
    def reload(self, name: str) -> bool:
        """Hot-reload a component."""
        ...

    @abstractmethod
    def validate_dependencies(self) -> tuple[bool, List[str]]:
        """Validate all component dependencies."""
        ...
```

---

## Intent Router

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RoutingDecision:
    """Result of intent routing."""
    target_component: str
    confidence: float  # 0.0 to 1.0
    routing_reason: str
    alternative_targets: List[str] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)
    estimated_duration_ms: int = 0


class IntentRouter(ABC):
    """Routes intents to appropriate components."""

    @abstractmethod
    def route(self, intent: UserIntent, context: Dict[str, Any]) -> RoutingDecision:
        """Determine which component should handle the intent."""
        ...

    @abstractmethod
    def can_handle(self, intent: UserIntent, component: str) -> bool:
        """Check if a component can handle a specific intent."""
        ...

    @abstractmethod
    def get_capability_match(self, intent: UserIntent) -> List[tuple[str, float]]:
        """Get capability matches for an intent."""
        ...

    @abstractmethod
    def train(self, training_data: List[tuple[UserIntent, str]]) -> None:
        """Train router on historical routing decisions."""
        ...
```

### Default Routing Strategies

```python
class CapabilityMatchRouter(IntentRouter):
    """Routes based on capability matching."""

    def route(self, intent: UserIntent, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on capability matching."""
        matches = self.get_capability_match(intent)
        if not matches:
            return RoutingDecision(
                target_component=self.default_fallback,
                confidence=0.0,
                routing_reason="No capable component found"
            )

        best_match, confidence = matches[0]
        alternatives = [m[0] for m in matches[1:4]]  # Top 3 alternatives

        return RoutingDecision(
            target_component=best_match,
            confidence=confidence,
            routing_reason=f"Best capability match ({confidence:.2%})",
            alternative_targets=alternatives,
            required_context=self._get_required_context(best_match)
        )


class PriorityRouter(IntentRouter):
    """Routes based on component priority."""

    def route(self, intent: UserIntent, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on configured priority."""
        ...


class AdaptiveRouter(IntentRouter):
    """Routes based on historical performance."""

    def route(self, intent: UserIntent, context: Dict[str, Any]) -> RoutingDecision:
        """Route based on success rates and timing."""
        ...
```

---

## Context Manager

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


@dataclass
class ContextEntry:
    """Individual entry in the context."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    scope: str = "session"  # "session", "user", "global"
    encrypted: bool = False

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass
class ContextSnapshot:
    """Snapshot of context at a point in time."""
    snapshot_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    entries: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    user_id: Optional[str] = None


class ContextManager(ABC):
    """Manages shared execution context."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, scope: str = "session", ttl_seconds: Optional[int] = None) -> bool:
        """Set value in context."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from context."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in context."""
        ...

    @abstractmethod
    def clear(self, scope: str = "session") -> int:
        """Clear context entries by scope."""
        ...

    @abstractmethod
    def snapshot(self) -> ContextSnapshot:
        """Create a snapshot of current context."""
        ...

    @abstractmethod
    def restore(self, snapshot: ContextSnapshot) -> int:
        """Restore context from snapshot."""
        ...

    @abstractmethod
    def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Get all context entries."""
        ...

    @abstractmethod
    def import_context(self, context_data: Dict[str, Any], scope: str = "session") -> int:
        """Import external context data."""
        ...

    @abstractmethod
    def export_context(self, scope: str = "session") -> Dict[str, Any]:
        """Export context data."""
        ...
```

---

## Memory Store

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """Individual memory entry."""
    memory_id: str
    key: str
    value: Any
    category: str  # "pattern", "learned_fact", "preference", "history"
    confidence: float = 1.0
    source: str = ""  # Which component created this
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if memory entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class MemoryQuery:
    """Query for memory retrieval."""
    key: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    limit: int = 100
    include_expired: bool = False


class MemoryStore(ABC):
    """Persistent storage for learned information."""

    @abstractmethod
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        ...

    @abstractmethod
    def retrieve(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memory entries matching query."""
        ...

    @abstractmethod
    def retrieve_by_key(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve memory by exact key."""
        ...

    @abstractmethod
    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory entry."""
        ...

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        ...

    @abstractmethod
    def forget_by_category(self, category: str) -> int:
        """Delete all entries in a category."""
        ...

    @abstractmethod
    def forget_expired(self) -> int:
        """Delete all expired entries."""
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        ...

    @abstractmethod
    def backup(self, path: str) -> bool:
        """Backup memory store to file."""
        ...

    @abstractmethod
    def restore(self, path: str) -> int:
        """Restore memory store from file."""
        ...
```

---

## Constraint Enforcer

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ConstraintType(Enum):
    TIME_LIMIT = "time_limit"
    ORDER_CONSTRAINT = "order_constraint"
    RESOURCE_LIMIT = "resource_limit"
    MUTEX = "mutex"  # Mutual exclusion
    DEPENDENCY = "dependency"
    CAPACITY = "capacity"
    CUSTOM = "custom"


class ConstraintPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Constraint:
    """Execution constraint."""
    constraint_id: str
    type: ConstraintType
    priority: ConstraintPriority = ConstraintPriority.NORMAL
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def evaluate(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """Evaluate if constraint is satisfied."""
        ...


@dataclass
class ConstraintViolation:
    """Violation of a constraint."""
    constraint_id: str
    constraint_type: ConstraintType
    message: str
    suggested_action: str = ""
    severity: str = "error"  # "error", "warning", "info"


class ConstraintEnforcer(ABC):
    """Validates and enforces execution constraints."""

    @abstractmethod
    def add_constraint(self, constraint: Constraint) -> bool:
        """Add a new constraint."""
        ...

    @abstractmethod
    def remove_constraint(self, constraint_id: str) -> bool:
        """Remove a constraint."""
        ...

    @abstractmethod
    def get_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Get constraint by ID."""
        ...

    @abstractmethod
    def list_constraints(self, type: Optional[ConstraintType] = None) -> List[Constraint]:
        """List all constraints."""
        ...

    @abstractmethod
    def validate_pre_execution(self, plan: List[str], context: Dict[str, Any]) -> List[ConstraintViolation]:
        """Validate constraints before execution."""
        ...

    @abstractmethod
    def validate_during_execution(self, current_step: str, context: Dict[str, Any]) -> List[ConstraintViolation]:
        """Validate constraints during execution."""
        ...

    @abstractmethod
    def acquire_resources(self, resource_id: str, owner: str, timeout_seconds: int = 30) -> bool:
        """Acquire a resource (for mutex constraints)."""
        ...

    @abstractmethod
    def release_resources(self, resource_id: str, owner: str) -> bool:
        """Release a resource."""
        ...
```

### Built-in Constraints

```python
class TimeLimitConstraint(Constraint):
    """Constraint: max execution time."""

    def __init__(self, max_seconds: int):
        super().__init__(
            constraint_id=f"time-limit-{uuid.uuid4().hex[:8]}",
            type=ConstraintType.TIME_LIMIT,
            params={"max_seconds": max_seconds},
            description=f"Maximum execution time: {max_seconds}s"
        )

    def evaluate(self, context: Dict[str, Any]) -> tuple[bool, str]:
        elapsed = context.get("elapsed_ms", 0) / 1000
        if elapsed > self.params["max_seconds"]:
            return False, f"Time limit exceeded: {elapsed:.2f}s > {self.params['max_seconds']}s"
        return True, "Time limit satisfied"


class OrderConstraint(Constraint):
    """Constraint: step A before step B."""

    def __init__(self, before: str, after: str):
        super().__init__(
            constraint_id=f"order-{before}-{after}",
            type=ConstraintType.ORDER_CONSTRAINT,
            params={"before": before, "after": after},
            description=f"{before} must execute before {after}"
        )

    def evaluate(self, context: Dict[str, Any]) -> tuple[bool, str]:
        completed = context.get("completed_steps", [])
        if self.params["after"] in completed and self.params["before"] not in completed:
            return False, f"{self.params['before']} must complete before {self.params['after']}"
        return True, "Order constraint satisfied"


class MutexConstraint(Constraint):
    """Constraint: mutual exclusion."""

    def __init__(self, resource_id: str):
        super().__init__(
            constraint_id=f"mutex-{resource_id}",
            type=ConstraintType.MUTEX,
            params={"resource_id": resource_id},
            description=f"Exclusive access to {resource_id}"
        )
```

---

## Execution Trace

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


class TraceEventType(Enum):
    COMPONENT_STARTED = "component_started"
    COMPONENT_COMPLETED = "component_completed"
    COMPONENT_FAILED = "component_failed"
    CONTEXT_UPDATED = "context_updated"
    MEMORY_STORED = "memory_stored"
    CONSTRAINT_CHECKED = "constraint_checked"
    CONSTRAINT_VIOLATED = "constraint_violated"
    ROUTING_DECISION = "routing_decision"
    RESOURCE_ACQUIRED = "resource_acquired"
    RESOURCE_RELEASED = "resource_released"


@dataclass
class TraceEvent:
    """Individual event in execution trace."""
    event_id: str
    event_type: TraceEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    component_name: Optional[str] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    parent_event_id: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class ExecutionTrace:
    """Complete execution trace."""
    trace_id: str
    intent_text: str
    session_id: str
    engine_version: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    events: List[TraceEvent] = field(default_factory=list)
    final_status: str = "pending"
    total_duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.end_time is None:
            self.end_time = self.start_time

    def add_event(self, event: TraceEvent) -> None:
        """Add event to trace."""
        self.events.append(event)

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological timeline of events."""
        return sorted(self.events, key=lambda e: e.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trace to dictionary."""
        return {
            "trace_id": self.trace_id,
            "intent_text": self.intent_text,
            "session_id": self.session_id,
            "engine_version": self.engine_version,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_ms": self.total_duration_ms,
            "final_status": self.final_status,
            "event_count": len(self.events),
            "events": [e.__dict__ for e in self.events],
            "metadata": self.metadata
        }


class ExecutionTraceStore(ABC):
    """Stores and retrieves execution traces."""

    @abstractmethod
    def store(self, trace: ExecutionTrace) -> bool:
        """Store an execution trace."""
        ...

    @abstractmethod
    def retrieve(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Retrieve trace by ID."""
        ...

    @abstractmethod
    def search(self, query: Dict[str, Any]) -> List[ExecutionTrace]:
        """Search traces by criteria."""
        ...

    @abstractmethod
    def get_recent(self, limit: int = 100) -> List[ExecutionTrace]:
        """Get recent traces."""
        ...

    @abstractmethod
    def prune(self, older_than: datetime) -> int:
        """Delete old traces."""
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get trace store statistics."""
        ...
```

---

## Engine Lifecycle

### Lifecycle States

```
┌─────────┐
│ CREATED │ ←── initialize()
└────┬────┘
     │
     ▼
┌─────────┐     ┌─────────┐
│ IDLE    │────►│ RUNNING │
└─────────┘     └────┬────┘
     │               │
     │    ┌──────────┴──────────┐
     │    │                       │
     │    ▼                       ▼
     │ ┌─────────┐           ┌─────────┐
     │ │ BUSY    │           │ PAUSED  │
     │ └────┬────┘           └────┬────┘
     │      │                      │
     │      └──────────┬───────────┘
     │                 │
     ▼                 ▼
┌─────────┐◄───────────────┐
│ SHUTDOWN│               │
└─────────┘               │
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
              ┌──────────┐  ┌──────────┐
              │ GRACEFUL │  │ FORCED   │
              └──────────┘  └──────────┘
```

### Lifecycle Interface

```python
from enum import Enum


class EngineState(Enum):
    CREATED = "created"
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    PAUSED = "paused"
    SHUTDOWN = "shutdown"


class LifecycleManager(ABC):
    """Manages engine lifecycle."""

    @abstractmethod
    def get_state(self) -> EngineState:
        """Get current engine state."""
        ...

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize engine and all components."""
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
    def resume(self) -> bool:
        """Resume processing."""
        ...

    @abstractmethod
    def shutdown(self, graceful: bool = True, timeout_seconds: int = 60) -> bool:
        """Shutdown the engine."""
        ...

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if engine is healthy."""
        ...

    @abstractmethod
    def get_health_details(self) -> Dict[str, Any]:
        """Get detailed health status."""
        ...
```

---

## Determinism Guarantees

```python
class DeterminismGuarantor:
    """Ensures deterministic engine behavior."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self._rng = random.Random(seed)

    def get_seed(self) -> Optional[int]:
        """Get current seed."""
        return self.seed

    def set_seed(self, seed: int) -> None:
        """Set seed for deterministic behavior."""
        self.seed = seed
        self._rng = random.Random(seed)

    def shuffle_deterministic(self, sequence: List[Any]) -> List[Any]:
        """Shuffle with deterministic RNG."""
        result = sequence.copy()
        self._rng.shuffle(result)
        return result

    def sample_deterministic(self, population: List[Any], k: int) -> List[Any]:
        """Sample deterministically."""
        return self._rng.sample(population, k)

    def generate_id(self, prefix: str = "") -> str:
        """Generate deterministic ID."""
        random_part = self._rng.randint(0, 99999999)
        return f"{prefix}{random_part:08d}"
```

---

## Complete Engine Implementation

```python
class CoreIntelligenceEngine(CoreEngine):
    """Complete implementation of Core Intelligence Engine."""

    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self.state = EngineState.CREATED

        # Core components
        self._context_manager: Optional[ContextManager] = None
        self._memory_store: Optional[MemoryStore] = None
        self._component_registry: Optional[ComponentRegistry] = None
        self._router: Optional[IntentRouter] = None
        self._constraint_enforcer: Optional[ConstraintEnforcer] = None
        self._trace_store: Optional[ExecutionTraceStore] = None
        self._determinism = DeterminismGuarantor()

        # Internal state
        self._trace_id_counter = 0
        self._active_traces: Dict[str, ExecutionTrace] = {}

    @property
    def config(self) -> EngineConfig:
        return self._config

    @property
    def context_manager(self) -> ContextManager:
        if self._context_manager is None:
            raise RuntimeError("Engine not initialized")
        return self._context_manager

    @property
    def memory_store(self) -> MemoryStore:
        if self._memory_store is None:
            raise RuntimeError("Engine not initialized")
        return self._memory_store

    @property
    def component_registry(self) -> ComponentRegistry:
        if self._component_registry is None:
            raise RuntimeError("Engine not initialized")
        return self._component_registry

    def initialize(self) -> None:
        """Initialize all engine components."""
        if self.state != EngineState.CREATED:
            raise RuntimeError(f"Cannot initialize from state: {self.state}")

        # Initialize core components
        self._context_manager = InMemoryContextManager(self.config)
        self._memory_store = create_memory_store(self.config)
        self._component_registry = ComponentRegistryImpl(self.config)
        self._router = CapabilityMatchRouter(self._component_registry)
        self._constraint_enforcer = ConstraintEnforcerImpl(self.config)
        self._trace_store = InMemoryTraceStore(self.config)

        # Discover and register components
        discovered = self._component_registry.discover(self.config.component_scan_paths)

        # Initialize context with engine metadata
        self.context_manager.set("engine", {
            "id": self.config.engine_id,
            "version": self.config.version,
            "initialized_at": datetime.utcnow().isoformat()
        })

        self.state = EngineState.IDLE

    def shutdown(self, graceful: bool = True) -> None:
        """Shutdown the engine."""
        if self.state == EngineState.SHUTDOWN:
            return

        # Persist memory if graceful
        if graceful:
            # Store context snapshots
            self.memory_store.store(MemoryEntry(
                memory_id=f"context-snapshot-{datetime.utcnow().isoformat()}",
                key="final_context",
                value=self.context_manager.get_all(),
                category="history"
            ))

        # Shutdown components
        if self._memory_store:
            self._memory_store = None
        if self._context_manager:
            self._context_manager.clear()
            self._context_manager = None

        self.state = EngineState.SHUTDOWN

    def process(self, input: EngineInput) -> EngineOutput:
        """Process a single intent."""
        if self.state not in (EngineState.IDLE, EngineState.RUNNING, EngineState.BUSY):
            raise RuntimeError(f"Engine not ready: {self.state}")

        # Validate input
        is_valid, error = input.validate()
        if not is_valid:
            return EngineOutput(
                status="failed",
                primary_output=None,
                errors=[error]
            )

        # Create execution trace
        trace = ExecutionTrace(
            trace_id=self._generate_trace_id(),
            intent_text=input.intent.raw_text,
            session_id=input.intent.session_id,
            engine_version=self.config.version
        )

        try:
            self.state = EngineState.BUSY

            # Apply context overrides
            for key, value in input.context_overrides.items():
                self.context_manager.set(key, value, scope="session")

            # Route intent
            routing_decision = self._router.route(
                input.intent,
                self.context_manager.get_all()
            )

            trace.add_event(TraceEvent(
                event_id=f"evt-{uuid.uuid4().hex[:8]}",
                event_type=TraceEventType.ROUTING_DECISION,
                component_name="router",
                event_data={
                    "target": routing_decision.target_component,
                    "confidence": routing_decision.confidence,
                    "reason": routing_decision.routing_reason
                }
            ))

            # Validate constraints
            violations = self._constraint_enforcer.validate_pre_execution(
                [routing_decision.target_component],
                self.context_manager.get_all()
            )

            if violations:
                trace.add_event(TraceEvent(
                    event_id=f"evt-{uuid.uuid4().hex[:8]}",
                    event_type=TraceEventType.CONSTRAINT_VIOLATED,
                    event_data={"violations": [v.__dict__ for v in violations]}
                ))

            # Execute component
            component = self._component_registry.get(routing_decision.target_component)
            component.instance.last_used = datetime.utcnow()
            component.use_count += 1

            start_time = datetime.utcnow()
            component_result = self._execute_component(
                component,
                input,
                trace
            )
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Build output
            output = EngineOutput(
                status="success" if component_result.status == "success" else "partial",
                primary_output=component_result.output,
                results=[component_result],
                trace_id=trace.trace_id,
                metadata={"routing": routing_decision.__dict__}
            )

            trace.final_status = output.status
            trace.end_time = datetime.utcnow()
            trace.total_duration_ms = duration_ms

            # Store trace
            self._trace_store.store(trace)

            return output

        except Exception as e:
            trace.final_status = "failed"
            trace.end_time = datetime.utcnow()
            trace.add_event(TraceEvent(
                event_id=f"evt-{uuid.uuid4().hex[:8]}",
                event_type=TraceEventType.COMPONENT_FAILED,
                event_data={"error": str(e)}
            ))
            self._trace_store.store(trace)

            return EngineOutput(
                status="failed",
                primary_output=None,
                errors=[f"Execution failed: {str(e)}"]
            )

        finally:
            self.state = EngineState.IDLE

    def _generate_trace_id(self) -> str:
        """Generate deterministic trace ID."""
        self._trace_id_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"trace-{timestamp}-{self._trace_id_counter:06d}"

    def _execute_component(
        self,
        component: ComponentInstance,
        input: EngineInput,
        trace: ExecutionTrace
    ) -> ComponentResult:
        """Execute a single component."""
        # Start event
        trace.add_event(TraceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:8]}",
            event_type=TraceEventType.COMPONENT_STARTED,
            component_name=component.metadata.name
        ))

        try:
            # Execute
            if hasattr(component.instance, 'execute'):
                result = component.instance.execute(input)
            else:
                result = component.instance(input)

            # Completion event
            trace.add_event(TraceEvent(
                event_id=f"evt-{uuid.uuid4().hex[:8]}",
                event_type=TraceEventType.COMPONENT_COMPLETED,
                component_name=component.metadata.name,
                event_data={"status": "success"}
            ))

            return ComponentResult(
                component_name=component.metadata.name,
                component_type=component.metadata.type,
                status="success",
                output=result,
                duration_ms=0  # TODO: measure
            )

        except Exception as e:
            trace.add_event(TraceEvent(
                event_id=f"evt-{uuid.uuid4().hex[:8]}",
                event_type=TraceEventType.COMPONENT_FAILED,
                component_name=component.metadata.name,
                event_data={"error": str(e)}
            ))

            return ComponentResult(
                component_name=component.metadata.name,
                component_type=component.metadata.type,
                status="failed",
                output=None,
                duration_ms=0,
                error=str(e)
            )
```

---

## Error Handling

```python
class EngineError(Exception):
    """Base exception for engine errors."""
    pass


class EngineNotInitializedError(EngineError):
    """Engine has not been initialized."""
    pass


class EngineShutdownError(EngineError):
    """Engine has been shutdown."""
    pass


class ComponentNotFoundError(EngineError):
    """Requested component not found."""
    pass


class ConstraintViolationError(EngineError):
    """Constraint was violated."""
    pass


class RoutingError(EngineError):
    """Failed to route intent."""
    pass
```

---

## Configuration Example

```python
# Default configuration
config = EngineConfig(
    engine_id="core-intelligence-engine",
    version="1.0.0",
    log_level=LogLevel.INFO,
    default_agent="architect_agent",
    routing_strategy="capability-match",
    context_max_size_mb=10,
    context_ttl_seconds=3600,
    memory_backend="in-memory",
    memory_max_entries=10000,
    max_execution_time_seconds=300,
    max_concurrent_operations=10,
    constraint_strict_mode=True,
    trace_enabled=True,
    trace_depth="full",
    component_scan_paths=["skills", "agents", "templates"],
    hot_reload_enabled=True,
    component_timeout_seconds=30
)
```
