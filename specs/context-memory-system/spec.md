# Context and Memory System Specification

**Spec ID:** CONTEXT-MEMORY-SYSTEM
**Version:** 1.0.0
**Status:** Draft
**Created:** 2025-12-29

## 1. Overview

This specification defines the context and memory system for the reusable intelligence framework. The system:

- Tracks execution state, goals, and history
- Is fully serializable for persistence and debugging
- Supports inspection and rollback capabilities
- Enforces isolation between concurrent executions

This system integrates with:
- **Runtime Architecture** (`specs/core-runtime-architecture/spec.md`) — Provides execution context
- **Cognitive Skills** (`specs/reusable-cognitive-skills/spec.md`) — Skills read/write state
- **Reusable Agents** (`specs/reusable-agents/spec.md`) — Agents access context

## 2. Context Hierarchy

### 2.1 Three-Level Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CONTEXT HIERARCHY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LEVEL 1: GLOBAL CONTEXT (Singleton)                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Scope: Engine-wide, shared across all sessions                     │    │
│  │  Lifetime: Engine start to shutdown                                  │    │
│  │                                                                        │    │
│  │  Contains:                                                           │    │
│  │  - Engine configuration                                              │    │
│  │  - Registered skill registry                                         │    │
│  │  - Registered agent registry                                         │    │
│  │  - System policies                                                   │    │
│  │  - Global event bus                                                  │    │
│  │  - Version information                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    │ (parent for all sessions)               │
│                                    ▼                                         │
│  LEVEL 2: SESSION CONTEXT (Per User Session)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Scope: Single user conversation/workspace                           │    │
│  │  Lifetime: User session creation to termination                      │    │
│  │                                                                        │    │
│  │  Contains:                                                           │    │
│  │  - session_id, user_id                                               │    │
│  │  - User profile and preferences                                      │    │
│  │  - Session history (execution summaries)                             │    │
│  │  - Working directory state                                           │    │
│  │  - Authentication tokens (if applicable)                             │    │
│  │  - Custom session variables                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    │ (parent for executions)                 │
│                                    ▼                                         │
│  LEVEL 3: EXECUTION CONTEXT (Per Request)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Scope: Single intelligence request                                  │    │
│  │  Lifetime: Request receipt to completion/timeout                     │    │
│  │                                                                        │    │
│  │  Contains:                                                           │    │
│  │  - execution_id, request_id                                          │    │
│  │  - Original intent/goal                                              │    │
│  │  - Current task stage                                                │    │
│  │  - Mutable state (key-value store)                                   │    │
│  │  - Execution history (event log)                                     │    │
│  │  - Intermediate outputs                                              │    │
│  │  - Error log                                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Context Access Rules

| Context Level | Accessible By | Read/Write |
|---------------|---------------|------------|
| **Global** | Engine, Agents | Read-only (engine manages) |
| **Session** | All executions in session | Read/Write (isolated) |
| **Execution** | Current execution only | Full Read/Write |

---

## 3. Data Structures

### 3.1 Global Context

```python
@dataclass
class GlobalContext:
    """
    Engine-wide shared context.
    Immutable after engine start.
    """
    execution_id: str
    config: EngineConfig
    skill_registry: SkillRegistry
    agent_registry: AgentRegistry
    policies: list[Policy]
    introspection: IntrospectionService
    started_at: timestamp
    version: str


@dataclass
class EngineConfig:
    """Engine configuration."""
    max_concurrent_executions: int = 100
    default_timeout: Duration = 300s
    session_ttl: Duration = 24h
    execution_ttl: Duration = 1h
    persistence_path: Path | None = None
    log_level: LogLevel = LogLevel.INFO
    sandbox_enabled: bool = True
```

### 3.2 Session Context

```python
@dataclass
class SessionContext:
    """
    Per-user session context.
    Shared across multiple executions in a session.
    """
    session_id: str
    user_id: str
    created_at: timestamp
    last_activity: timestamp
    user_profile: UserProfile | None
    working_directory: Path
    history: list[ExecutionSummary]
    session_variables: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class UserProfile:
    """User preferences and profile."""
    user_id: str
    display_name: str | None
    preferred_language: str = "en"
    coding_standards: dict | None = None
    custom_policies: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)


@dataclass
class ExecutionSummary:
    """Summary of a completed execution for history."""
    execution_id: str
    goal: str
    status: ExecutionStatus
    started_at: timestamp
    completed_at: timestamp | None
    outcome: OutcomeType
    summary: str
```

### 3.3 Execution Context (Core)

```python
@dataclass
class ExecutionContext:
    """
    Per-request execution context.
    Central data structure for intelligence execution.
    """
    # Identity
    execution_id: str
    session_id: str
    request_id: str

    # Lifecycle
    status: ExecutionStatus
    current_stage: TaskStage
    started_at: timestamp
    completed_at: timestamp | None

    # Core data
    goal: Goal
    intent: ParsedIntent | None
    specification: Specification | None
    task_tree: TaskTree | None
    action_plan: ActionPlan | None

    # State management
    state: MutableState
    checkpoints: dict[str, Checkpoint]

    # History and tracing
    history: HistoryLog
    trace: ExecutionTrace
    errors: list[ExecutionError]

    # Outputs
    outputs: dict[str, Any]
    outcome: ExecutionOutcome | None

    # Metadata
    metadata: dict[str, Any]
    parent_execution_id: str | None  # For refinement loops
```


### 3.4 Mutable State

```python
@dataclass
class MutableState:
    """
    Key-value store for intermediate data.
    Skills read from and write to this structure.
    """
    data: dict[str, Any]
    version: int  # Incremented on each mutation

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in state."""
        self.data[key] = value
        self.version += 1

    def delete(self, key: str) -> None:
        """Delete a key from state."""
        if key in self.data:
            del self.data[key]
            self.version += 1

    def keys(self) -> list[str]:
        """List all keys in state."""
        return list(self.data.keys())

    def snapshot(self) -> dict[str, Any]:
        """Create a snapshot for rollback."""
        return copy.deepcopy(self.data)
```

### 3.5 History Log

```python
@dataclass
class HistoryLog:
    """
    Append-only event log.
    Records all significant events during execution.
    """
    events: list[HistoryEvent]
    current_event_id: int

    def append(self, event: HistoryEvent) -> None:
        """Append an event to the log."""
        self.events.append(event)
        self.current_event_id += 1

    def get_events_since(self, event_id: int) -> list[HistoryEvent]:
        """Get events after a specific event."""
        return [e for e in self.events if e.event_id > event_id]

    def get_last_event(self) -> HistoryEvent | None:
        """Get the most recent event."""
        return self.events[-1] if self.events else None


@dataclass
class HistoryEvent:
    """
    Single event in the history log.
    Immutable once recorded.
    """
    event_id: int
    timestamp: timestamp
    event_type: EventType
    source: str  # agent_id or skill_id
    action: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    duration_ms: int | None
    error: ExecutionError | None
    metadata: dict[str, Any]


@dataclass
class Checkpoint:
    """Snapshot of state at a point in time."""
    checkpoint_id: str
    event_id: int
    timestamp: timestamp
    state_snapshot: dict[str, Any]
    stage: TaskStage
    description: str
```

### 3.6 Goal and Intent

```python
@dataclass
class Goal:
    """
    The original goal for an execution.
    Immutable after creation.
    """
    goal_id: str
    raw_text: str
    structured_goal: StructuredGoal
    constraints: list[Constraint]
    success_criteria: list[str]
    created_at: timestamp


@dataclass
class StructuredGoal:
    """Structured representation of a goal."""
    objective: str
    entities: list[Entity]
    parameters: dict[str, Any]
    expected_outcome: str | None
```

---

## 4. Read/Write Rules

### 4.1 Immutability Guarantees

| Field | Mutability | Rule |
|-------|------------|------|
| `execution_id` | Immutable | Set at creation, never changes |
| `session_id` | Immutable | Set at creation, never changes |
| `goal` | Immutable | Set at creation, never changes |
| `intent` | Immutable | Set during interpretation |
| `history.events` | Append-only | New events added, existing never modified |
| `state` | Mutable | Skills can read/write |
| `checkpoints` | Mutable | New checkpoints added |
| `outputs` | Mutable | Final output stored here |
| `metadata` | Mutable | Runtime metadata |

### 4.2 State Access Rules

```python
class StateAccessPolicy:
    """Policies for state access."""

    @staticmethod
    def can_read(context: ExecutionContext, key: str) -> bool:
        """Check if a key can be read."""
        return key in context.state.data

    @staticmethod
    def can_write(context: ExecutionContext, key: str) -> bool:
        """Check if a key can be written."""
        # System keys cannot be overwritten
        SYSTEM_KEYS = {"_execution_id", "_session_id", "_goal"}
        return key not in SYSTEM_KEYS

    @staticmethod
    def can_delete(context: ExecutionContext, key: str) -> bool:
        """Check if a key can be deleted."""
        # System keys cannot be deleted
        SYSTEM_KEYS = {"_execution_id", "_session_id", "_goal"}
        return key not in SYSTEM_KEYS


class ContextError(Exception):
    """Base exception for context errors."""
    pass


class ImmutableFieldError(ContextError):
    """Raised when attempting to modify an immutable field."""
    pass


class InvalidStateKeyError(ContextError):
    """Raised when using an invalid state key."""
    pass


class RollbackError(ContextError):
    """Raised when rollback fails."""
    pass
```

### 4.3 Isolation Rules

```python
class ContextIsolation:
    """Enforces context isolation."""

    @staticmethod
    def check_isolation(
        context: ExecutionContext,
        requesting_agent: str
    ) -> None:
        """
        Verify that an agent can only access its own context.

        Rules:
        1. Agents can only access execution context for their current execution
        2. Skills receive a copy of relevant state, never direct access
        3. Cross-context access is only allowed via explicit APIs
        4. Shared context requires explicit configuration
        """
        # Rule 1: Execution-bound access
        if context.execution_id != RequestContext.current_execution():
            raise ContextIsolationError(
                "Agent cannot access context from different execution"
            )

    @staticmethod
    def sanitize_for_skill(
        context: ExecutionContext,
        skill_id: str,
        required_keys: list[str]
    ) -> dict[str, Any]:
        """
        Create a sanitized view of state for a skill.
        Only includes keys the skill is allowed to access.
        """
        allowed = {}
        for key in required_keys:
            if key in context.state.data:
                allowed[key] = context.state.data[key]
        return allowed
```

### 4.4 Write Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STATE WRITE FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐                                                              │
│  │   Skill  │                                                              │
│  │  Wants   │                                                              │
│  │  to Write│                                                              │
│  └────┬─────┘                                                              │
│       │                                                                    │
│       ▼                                                                    │
│  ┌──────────┐    ┌───────────────────────────────────────────┐             │
│  │  Validate│───▶│   Check:                                 │             │
│  │  Request │    │   - Key is valid (not system key)        │             │
│  └────┬─────┘    │   - Value is serializable                │             │
│       │          │   - Context is not frozen                │             │
│       │          └───────────────────────────────────────────┘             │
│       │                              │                                      │
│       │                              ▼                                      │
│       │          ┌───────────────────────────────────────────┐             │
│       │          │   If valid:                               │             │
│       │          │   1. Write to state.data                  │             │
│       │          │   2. Increment state.version              │             │
│       │          │   3. Record HISTORY_EVENT                 │             │
│       │          │   4. (Optional) Create checkpoint         │             │
│       │          └───────────────────────────────────────────┘             │
│       │                              │                                      │
│       │                              ▼                                      │
│       │          ┌───────────────────────────────────────────┐             │
│       │          │   If invalid:                             │             │
│       │          │   1. Raise ContextError                   │             │
│       │          │   2. Record error in history              │             │
│       │          │   3. Halt execution (if critical)         │             │
│       │          └───────────────────────────────────────────┘             │
│       │                                                                    │
│       ▼                                                                    │
│  ┌──────────┐                                                              │
│  │  Return  │                                                              │
│  │  Result  │                                                              │
│  └──────────┘                                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Serialization

### 5.1 Serialization Requirements

```python
class ContextSerializer:
    """Handles context serialization."""

    SUPPORTED_FORMATS = ["json", "msgpack", "yaml"]

    def serialize(
        self,
        context: ExecutionContext,
        format: str = "json"
    ) -> str | bytes:
        """
        Serialize a context to a string/bytes.

        Rules:
        1. Must include all fields (no optional omission)
        2. Must handle circular references
        3. Must preserve type information for complex objects
        4. Must be human-readable (for JSON/YAML)
        """
        if format not in self.SUPPORTED_FORMATS:
            raise SerializationError(f"Unsupported format: {format}")

        data = self._to_serializable_dict(context)
        if format == "json":
            return json.dumps(data, indent=2, default=self._json_serializer)
        elif format == "yaml":
            return yaml.dump(data)
        elif format == "msgpack":
            return msgpack.packb(data)

    def deserialize(
        self,
        data: str | bytes,
        format: str = "json"
    ) -> ExecutionContext:
        """Deserialize a context from string/bytes."""
        if format == "json":
            raw = json.loads(data)
        elif format == "yaml":
            raw = yaml.safe_load(data)
        elif format == "msgpack":
            raw = msgpack.unpackb(data)

        return self._from_serializable_dict(raw)
```

### 5.2 Serialization Rules

| Field | Serialization | Notes |
|-------|---------------|-------|
| `execution_id` | As-is | String |
| `state.data` | Deep copy | All values must be JSON-serializable |
| `history.events` | Full serialization | Includes nested objects |
| `checkpoints` | Full serialization | State snapshots included |
| `goal` | Full serialization | Nested structures preserved |
| `intent` | Full serialization | May be None |
| `errors` | Full serialization | Error details preserved |

### 5.3 Non-Serializable Values

The following types are NOT allowed in state:

```python
NON_SERIALIZABLE_TYPES = (
    file_handle,           # File handles
    network_connection,    # Socket/connection objects
    function,              # Callable functions
    class_type,            # Class objects
    module,                # Module objects
    thread,                # Thread objects
    process,               # Process objects
    lock,                  # Synchronization primitives
    database_connection,   # DB connections
)

def validate_serializable(value: Any) -> None:
    """Validate that a value can be serialized."""
    for non_serializable_type in NON_SERIALIZABLE_TYPES:
        if isinstance(value, non_serializable_type):
            raise SerializationError(
                f"Value of type {type(value).__name__} is not serializable"
            )

    if isinstance(value, dict):
        for k, v in value.items():
            validate_serializable(v)
    elif isinstance(value, (list, tuple)):
        for item in value:
            validate_serializable(item)
```

---

## 6. Inspection

### 6.1 Inspection Interface

```python
class ContextInspector:
    """Provides introspection capabilities for contexts."""

    def __init__(self, context: ExecutionContext):
        self.context = context

    def get_full_state(self) -> dict[str, Any]:
        """Get complete state dump."""
        return {
            "execution_id": self.context.execution_id,
            "status": self.context.status.value,
            "current_stage": self.context.current_stage.value,
            "state": self.context.state.data,
            "history": self._format_history(),
            "outputs": self.context.outputs,
            "errors": [self._format_error(e) for e in self.context.errors],
            "duration_ms": self._calculate_duration(),
        }

    def get_history_summary(self) -> list[dict[str, Any]]:
        """Get condensed history for display."""
        return [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "type": e.event_type.value,
                "source": e.source,
                "action": e.action,
                "duration_ms": e.duration_ms,
            }
            for e in self.context.history.events
        ]

    def get_state_diff(
        self,
        from_event_id: int,
        to_event_id: int | None = None
    ) -> StateDiff:
        """Get state changes between two events."""
        if to_event_id is None:
            to_event_id = self.context.history.current_event_id

        events = self.context.history.get_events_since(from_event_id)
        return self._compute_diff(events)

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Retrieve a specific checkpoint."""
        return self.context.checkpoints.get(checkpoint_id)

    def search_history(
        self,
        query: HistoryQuery
    ) -> list[HistoryEvent]:
        """Search history with filters."""
        events = self.context.history.events

        if query.event_type:
            events = [e for e in events if e.event_type == query.event_type]
        if query.source:
            events = [e for e in events if e.source == query.source]
        if query.start_time:
            events = [e for e in events if e.timestamp >= query.start_time]
        if query.end_time:
            events = [e for e in events if e.timestamp <= query.end_time]

        return events


@dataclass
class StateDiff:
    """Represents changes in state between two points."""
    added_keys: dict[str, Any]
    modified_keys: dict[str, tuple[Any, Any]]  # (old, new)
    deleted_keys: list[str]
    from_event_id: int
    to_event_id: int
```

### 6.2 Debug View

```python
@dataclass
class DebugView:
    """Human-readable debug view of context."""
    execution_id: str
    status: str
    current_stage: str
    goal: str
    state_keys: list[str]
    recent_events: list[dict]
    last_error: str | None
    duration: str
    memory_usage: str

    @classmethod
    def from_context(cls, context: ExecutionContext) -> "DebugView":
        """Create debug view from context."""
        last_error = context.errors[-1] if context.errors else None
        return cls(
            execution_id=context.execution_id,
            status=context.status.value,
            current_stage=context.current_stage.value,
            goal=context.goal.raw_text,
            state_keys=list(context.state.keys()),
            recent_events=cls._format_recent(context.history.events, 10),
            last_error=last_error.message if last_error else None,
            duration=cls._format_duration(context),
            memory_usage=cls._estimate_memory(context),
        )
```

---

## 7. Rollback

### 7.1 Rollback Mechanism

```python
class RollbackManager:
    """Manages state rollback for contexts."""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self._rollback_stack: list[RollbackRecord] = []

    def create_checkpoint(
        self,
        checkpoint_id: str,
        description: str = ""
    ) -> Checkpoint:
        """
        Create a checkpoint at current state.

        Checkpoints are stored and can be restored later.
        """
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            event_id=self.context.history.current_event_id,
            timestamp=utc_now(),
            state_snapshot=self.context.state.snapshot(),
            stage=self.context.current_stage,
            description=description,
        )
        self.context.checkpoints[checkpoint_id] = checkpoint
        return checkpoint

    def rollback(
        self,
        target_event_id: int | None = None,
        checkpoint_id: str | None = None
    ) -> RollbackResult:
        """
        Rollback context to a previous state.

        Args:
            target_event_id: Rollback to state after this event
            checkpoint_id: Rollback to this checkpoint

        Returns:
            RollbackResult with details of the rollback
        """
        # Determine target state
        if checkpoint_id:
            target_state = self.context.checkpoints.get(checkpoint_id)
            if not target_state:
                raise RollbackError(f"Checkpoint not found: {checkpoint_id}")
        elif target_event_id is not None:
            target_state = self._state_at_event(target_event_id)
        else:
            # Rollback to previous event
            last_event = self.context.history.get_last_event()
            if last_event:
                target_state = self._state_at_event(last_event.event_id - 1)
            else:
                raise RollbackError("No events to rollback to")

        # Create rollback record
        record = RollbackRecord(
            from_event_id=self.context.history.current_event_id,
            to_event_id=target_event_id or checkpoint_id,
            timestamp=utc_now(),
            previous_state_snapshot=self.context.state.snapshot(),
        )
        self._rollback_stack.append(record)

        # Perform rollback
        self.context.state.data = target_state
        self.context.state.version += 1

        # Add rollback event to history
        self.context.history.append(HistoryEvent(
            event_id=self.context.history.current_event_id + 1,
            timestamp=utc_now(),
            event_type=EventType.ROLLBACK,
            source="RollbackManager",
            action="rollback",
            input_data={"target": target_event_id or checkpoint_id},
            output_data={"success": True},
            duration_ms=None,
            error=None,
            metadata={},
        ))

        return RollbackResult(
            success=True,
            from_event_id=record.from_event_id,
            to_event_id=target_event_id or checkpoint_id,
            state_restored=True,
        )

    def get_rollback_history(self) -> list[RollbackRecord]:
        """Get history of all rollbacks."""
        return copy.deepcopy(self._rollback_stack)


@dataclass
class RollbackRecord:
    """Record of a rollback operation."""
    from_event_id: int
    to_event_id: int | str
    timestamp: timestamp
    previous_state_snapshot: dict[str, Any]


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    success: bool
    from_event_id: int
    to_event_id: int | str
    state_restored: bool
    error_message: str | None = None
```

### 7.2 Rollback Constraints

| Constraint | Description |
|------------|-------------|
| **No forward recovery** | Rollback only restores previous state, not forward changes |
| **Checkpoint required for state snapshot** | Without checkpoint, only event history available |
| **Rollback adds history event** | Each rollback is recorded in history |
| **Atomic rollback** | Either full rollback succeeds or no changes made |
| **Max rollback depth** | Configurable limit on rollback stack size |

---

## 8. Persistence Boundaries

### 8.1 Persistence Levels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PERSISTENCE BOUNDARIES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LEVEL 0: EPHEMERAL (In-Memory)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Default for active executions                                       │    │
│  │  - Execution context lives in memory                                 │    │
│  │  - Lost on process termination                                       │    │
│  │  - Fastest access                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼ (Explicit save)                         │
│  LEVEL 1: SHORT-TERM (Session)                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Persists for session duration                                       │    │
│  │  - Session context saved to disk/memory                              │    │
│  │  - Survives engine restart (within session)                          │    │
│  │  - Used for: context inspection, debugging                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼ (Explicit archive)                      │
│  LEVEL 2: LONG-TERM (Archive)                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Persists indefinitely                                               │    │
│  │  - Execution contexts serialized to storage                          │    │
│  │  - Used for: audit trail, compliance, analysis                       │    │
│  │  - Configurable retention policy                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Persistence Interface

```python
class ContextPersistence:
    """Handles context persistence."""

    async def save(
        self,
        context: ExecutionContext,
        level: PersistenceLevel = PersistenceLevel.SHORT_TERM
    ) -> PersistenceResult:
        """
        Save a context at the specified level.

        Args:
            context: Context to save
            level: Persistence level

        Returns:
            PersistenceResult with location and metadata
        """
        serialized = self._serializer.serialize(context)

        if level == PersistenceLevel.SHORT_TERM:
            path = self._get_session_path(context.session_id)
        elif level == PersistenceLevel.LONG_TERM:
            path = self._get_archive_path(context.execution_id)

        await self._storage.write(path, serialized)

        return PersistenceResult(
            context_id=context.execution_id,
            level=level,
            path=path,
            size_bytes=len(serialized),
            timestamp=utc_now(),
        )

    async def load(
        self,
        context_id: str,
        level: PersistenceLevel = PersistenceLevel.SHORT_TERM
    ) -> ExecutionContext:
        """Load a context from persistence."""
        path = self._get_path(context_id, level)
        data = await self._storage.read(path)
        return self._serializer.deserialize(data)

    async def archive(
        self,
        context: ExecutionContext,
        retention_days: int = 90
    ) -> None:
        """
        Archive a completed execution context.

        Args:
            context: Context to archive
            retention_days: Days to retain before deletion
        """
        # Compress history (keep full, but summarize)
        archived = self._create_archive_view(context)
        path = self._get_archive_path(context.execution_id)

        await self._storage.write(path, archived)

        # Schedule cleanup
        await self._scheduler.schedule_deletion(
            path,
            delay=timedelta(days=retention_days)
        )


@dataclass
class PersistenceResult:
    """Result of a persistence operation."""
    context_id: str
    level: PersistenceLevel
    path: Path
    size_bytes: int
    timestamp: timestamp


class PersistenceLevel(Enum):
    EPHEMERAL = "ephemeral"       # In-memory only
    SHORT_TERM = "short_term"     # Session duration
    LONG_TERM = "long_term"       # Archive
```

### 8.3 What Gets Persisted

| Data | Ephemeral | Short-Term | Long-Term |
|------|-----------|------------|-----------|
| `execution_id` | ✓ | ✓ | ✓ |
| `state.data` | ✓ | ✓ | ✓ (compressed) |
| `history.events` | ✓ | ✓ | ✓ (full) |
| `checkpoints` | ✓ | ✓ | ✓ |
| `goal` | ✓ | ✓ | ✓ |
| `outputs` | ✓ | ✓ | ✓ |
| `errors` | ✓ | ✓ | ✓ |
| `trace` | ✓ | ✓ | summary only |
| `metadata` | ✓ | ✓ | selected |

---

## 9. Quality Standards

### 9.1 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| State read | <1ms | O(1) dictionary access |
| State write | <1ms | Including version increment |
| Event append | <1ms | Append to list |
| Checkpoint create | <5ms | Deep copy state |
| Rollback | <10ms | Restore from snapshot |
| Serialize (typical) | <50ms | JSON, 100 events |
| Deserialize (typical) | <50ms | JSON, 100 events |

### 9.2 Memory Targets

| Context Size | Memory Limit |
|--------------|--------------|
| Single execution | 50MB (state) |
| Session (10 executions) | 200MB |
| Checkpoint overhead | 2x state size |
| History overhead | ~1KB per event |

### 9.3 Reliability Targets

| Metric | Target |
|--------|--------|
| Serialization success rate | 100% |
| Deserialization integrity | 100% (no data loss) |
| Isolation guarantee | 100% (no cross-context access) |
| Rollback accuracy | 100% (exact state restoration) |

---

## 10. Out of Scope

- **Distributed context sharing** — Single-node focus
- **Real-time context synchronization** — Future enhancement
- **Context encryption** — Future security enhancement
- **Query language for context** — Future enhancement

---

## 11. References

- **Runtime Architecture:** `specs/core-runtime-architecture/spec.md`
- **Cognitive Skills:** `specs/reusable-cognitive-skills/spec.md`
- **Reusable Agents:** `specs/reusable-agents/spec.md`
- **Constitution:** `.specify/memory/constitution.md`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
