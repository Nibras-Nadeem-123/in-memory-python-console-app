# Core Runtime Architecture Specification

**Spec ID:** CORE-RUNTIME-ARCHITECTURE
**Version:** 1.0.0
**Status:** Draft
**Created:** 2025-12-29

## 1. Overview

This specification defines the core runtime architecture for the reusable intelligence framework. It describes how the engine orchestrates agents, manages context, invokes skills, handles errors, and provides introspection throughout the full execution lifecycle.

This runtime architecture integrates with:
- **Intelligence Model** (`specs/core-intelligence-model/spec.md`) — Implements reasoning/execution boundary
- **Cognitive Skills** (`specs/reusable-cognitive-skills/spec.md`) — Invokes stateless skills
- **Reusable Agents** (`specs/reusable-agents/spec.md`) — Routes to specialized agents

## 2. Runtime Architecture Overview

### 2.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RUNTIME ENGINE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   ENGINE CORE   │────▶│ CONTEXT MANAGER │────▶│ AGENT ROUTER    │       │
│  │   (Lifecycle)   │     │   (State)       │     │   (Routing)     │       │
│  └─────────────────┘     └─────────────────┘     └────────┬────────┘       │
│                                                           │                 │
│                                                           ▼                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │   INTROSPECTION │◀────│   SKILL         │◀────│   AGENT         │       │
│  │   (Logs/Metrics)│     │   EXECUTOR      │     │   DISPATCHER    │       │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐                                │
│  │   ERROR         │     │   SKILL         │                                │
│  │   HANDLER       │     │   REGISTRY      │                                │
│  └─────────────────┘     └─────────────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Engine Core** | Lifecycle management, initialization, shutdown, orchestration |
| **Context Manager** | Session state, data isolation, context persistence |
| **Agent Router** | Select appropriate agent based on task type |
| **Agent Dispatcher** | Invoke agent, manage agent lifecycle |
| **Skill Executor** | Execute skills, manage timeouts, collect results |
| **Skill Registry** | Discover and load skills |
| **Error Handler** | Classify errors, determine recovery strategy |
| **Introspection** | Logging, metrics, tracing, audit trails |

---

## 3. Engine Lifecycle

### 3.1 Lifecycle States

```
                    ┌─────────────────────────────────────────┐
                    │            ENGINE LIFECYCLE             │
                    └─────────────────────────────────────────┘

       ┌─────────┐     ┌─────────────┐     ┌─────────────┐
       │ CREATED │────▶│  INITIALIZED│────▶│   RUNNING   │
       │ (new)   │     │ (start())   │     │ (ready)     │
       └─────────┘     └─────────────┘     └──────┬──────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
           ┌─────────────┐               ┌─────────────┐               ┌─────────────┐
           │  IDLE       │               │ EXECUTING   │               │ PAUSED      │
           │ (no active  │               │ (processing │               │ (suspended) │
           │  tasks)     │               │  tasks)     │               │             │
           └──────┬──────┘               └──────┬──────┘               └──────┬──────┘
                  │                             │                             │
                  └─────────────────────────────┼─────────────────────────────┘
                                                │
                                                ▼
                                       ┌─────────────┐
                                       │  SHUTDOWN   │
                                       │ (terminated)│
                                       └─────────────┘
```

### 3.2 Lifecycle Methods

```python
class RuntimeEngine:
    """Core runtime engine managing the intelligence system."""

    async def start(self) -> None:
        """
        Initialize the engine.

        Actions:
        1. Load skill registry
        2. Register all available agents
        3. Initialize context store
        4. Start introspection service
        5. Begin health check loop
        """
        await self._load_skills()
        await self._register_agents()
        await self._init_context_store()
        await self._start_introspection()
        await self._start_health_monitor()
        self._state = EngineState.RUNNING

    async def shutdown(self, grace_period: Duration = 30s) -> None:
        """
        Gracefully shutdown the engine.

        Args:
            grace_period: Maximum time to wait for active tasks

        Actions:
        1. Set state to SHUTDOWN
        2. Reject new submissions
        3. Allow active tasks to complete (up to grace_period)
        4. Force-terminate stuck tasks
        5. Flush all logs
        6. Close all connections
        """
        self._state = EngineState.SHUTDOWN
        await self._drain_active_tasks(grace_period)
        await self._flush_logs()
        await self._close_connections()

    async def submit(
        self,
        request: IntelligenceRequest
    ) -> ExecutionHandle:
        """
        Submit a new intelligence request.

        Returns:
            ExecutionHandle for tracking progress

        Raises:
            EngineNotReadyError: If engine not in RUNNING state
            InvalidRequestError: If request fails validation
        """
```

### 3.3 Health Monitoring

```python
class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthCheck:
    """Health monitoring for runtime components."""

    async def check_all(self) -> HealthReport:
        """Check all components and return health status."""
        return HealthReport(
            engine=self._check_engine(),
            skills=self._check_skill_registry(),
            agents=self._check_agent_availability(),
            context=self._check_context_store(),
            memory=self._check_memory_usage(),
            timestamp=utc_now()
        )
```

---

## 4. Context Management

### 4.1 Context Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CONTEXT HIERARCHY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    GLOBAL CONTEXT (Singleton)                       │    │
│  │  - Engine configuration                                             │    │
│  │  - Registered agents and skills                                     │    │
│  │  - System-wide policies                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐   │
│  │   SESSION CONTEXT   │ │   SESSION CONTEXT   │ │   SESSION CONTEXT   │   │
│  │   (User Session)    │ │   (User Session)    │ │   (User Session)    │   │
│  │  - session_id       │ │  - session_id       │ │  - session_id       │   │
│  │  - user_profile     │ │  - user_profile     │ │  - user_profile     │   │
│  │  - session_history  │ │  - session_history  │ │  - session_history  │   │
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘   │
│            │                   │                   │                        │
│            ▼                   ▼                   ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EXECUTION CONTEXT (Per Request)                   │    │
│  │  - execution_id                                                     │    │
│  │  - original_request                                                 │    │
│  │  - current_task_stage                                               │    │
│  │  - intermediate_outputs                                             │    │
│  │  - execution_trace                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Context Data Structures

```python
@dataclass
class GlobalContext:
    """Engine-wide shared context."""
    config: EngineConfig
    skill_registry: SkillRegistry
    agent_registry: AgentRegistry
    policies: list[Policy]
    introspection: IntrospectionService


@dataclass
class SessionContext:
    """User session context."""
    session_id: str
    user_id: str
    created_at: timestamp
    last_activity: timestamp
    history: list[ExecutionSummary]
    user_profile: UserProfile | None


@dataclass
class ExecutionContext:
    """Per-request execution context."""
    execution_id: str
    session_id: str
    request: IntelligenceRequest
    stage: TaskStage
    state: dict[str, Any]              # Intermediate data
    outputs: dict[str, Any]            # Final outputs
    trace: ExecutionTrace
    errors: list[ExecutionError]
    started_at: timestamp
    metadata: dict[str, Any]


@dataclass
class ExecutionTrace:
    """Complete execution trace for introspection."""
    events: list[TraceEvent]
    agent_invocations: list[AgentInvocation]
    skill_invocations: list[SkillInvocation]
    decisions: list[ReasoningDecision]
```

### 4.3 Context Isolation Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Session Isolation** | One session cannot access another's data |
| **Execution Isolation** | Concurrent executions have isolated state |
| **Clean Lifecycle** | Context deleted after execution completes (or via TTL) |
| **Immutable Inputs** | Original request never modified |

---

## 5. Agent Routing

### 5.1 Routing Algorithm

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AGENT ROUTING LOGIC                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                           │
│  │  Incoming   │                                                           │
│  │  Task       │                                                           │
│  └──────┬──────┘                                                           │
│         │                                                                  │
│         ▼                                                                  │
│  ┌─────────────┐    ┌───────────────────────────────────────────┐          │
│  │   Extract   │───▶│   Match Task Type to Agent Capabilities   │          │
│  │   Metadata  │    │                                           │          │
│  └─────────────┘    │   1. Extract task_requirements            │          │
│                     │   2. Query agent registry                 │          │
│                     │   3. Filter by capability                 │          │
│                     │   4. Score candidates                     │          │
│                     │   5. Select best match                    │          │
│                     └───────────────────────────────────────────┘          │
│                                    │                                       │
│                                    ▼                                       │
│                          ┌─────────────────┐                               │
│                          │  Selected Agent │                               │
│                          │   Dispatch      │                               │
│                          └─────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Routing Rules

```python
class AgentRouter:
    """Routes tasks to appropriate agents."""

    async def route(
        self,
        task: Task,
        context: ExecutionContext,
        available_agents: list[AgentReference]
    ) -> AgentDispatch:
        """
        Route a task to the best available agent.

        Selection Criteria (in priority order):
        1. Capability match (agent declares task type)
        2. Availability (agent not overloaded)
        3. Performance history (success rate, latency)
        4. Session affinity (same agent for related tasks)
        """
        candidates = await self._find_candidates(task, available_agents)
        if not candidates:
            raise NoAgentFoundError(task.type)

        # Score and rank candidates
        scored = [
            (agent, await self._score(agent, task, context))
            for agent in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return AgentDispatch(
            agent=scored[0][0],
            task=task,
            context=context,
            routing_reason=scored[0][1].reason
        )
```

### 5.3 Routing Table

| Task Type | Default Agent | Fallback Agents |
|-----------|---------------|-----------------|
| `intent_parse` | InterpreterAgent | [None] |
| `spec_generate` | ArchitectAgent | [PlannerAgent] |
| `task_decompose` | PlannerAgent | [ArchitectAgent] |
| `constraint_validate` | ReviewerAgent | [PlannerAgent] |
| `plan_generate` | PlannerAgent | [ArchitectAgent] |
| `execute_skills` | ExecutorAgent | [RefinerAgent] |
| `result_evaluate` | ReviewerAgent | [RefinerAgent] |
| `refine_output` | RefinerAgent | [ReviewerAgent] |

---

## 6. Skill Invocation

### 6.1 Invocation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SKILL INVOCATION FLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   Request   │────▶│   Validate  │────▶│   Prepare   │                   │
│  │   Arrives   │     │   Inputs    │     │   Context   │                   │
│  └─────────────┘     └─────────────┘     └──────┬──────┘                   │
│                                                  │                          │
│                                                  ▼                          │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                     EXECUTION SANDBOX                            │      │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐     │      │
│  │  │ Timeout   │  │  Memory   │  │  Import   │  │  Resource │     │      │
│  │  │  Monitor  │  │   Limit   │  │  Filter   │  │   Cap     │     │      │
│  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘     │      │
│  │        │            │            │            │               │      │
│  │        └────────────┴────────────┴────────────┘               │      │
│  │                           │                                     │      │
│  │                           ▼                                     │      │
│  │  ┌─────────────────────────────────────────────────────────┐   │      │
│  │  │                    SKILL EXECUTION                      │   │      │
│  │  │         (Actual skill logic runs here)                  │   │      │
│  │  └─────────────────────────────────────────────────────────┘   │      │
│  │                           │                                     │      │
│  └───────────────────────────┼─────────────────────────────────────┘      │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   Capture   │────▶│   Validate  │────▶│   Return    │                   │
│  │   Output    │     │   Result    │     │   Result    │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Invocation Interface

```python
class SkillExecutor:
    """Executes skills with safety guarantees."""

    async def invoke(
        self,
        skill_id: str,
        input: SkillInput,
        context: ExecutionContext,
        options: InvocationOptions | None = None
    ) -> SkillResult[Output]:
        """
        Invoke a skill with safety guarantees.

        Safety Features:
        - Timeout enforcement
        - Memory limits
        - Import filtering (sandbox)
        - Resource caps
        - Result validation
        """
        options = options or InvocationOptions()

        # 1. Validate inputs
        await self._validate_input(skill_id, input)

        # 2. Prepare sandbox
        sandbox = await self._create_sandbox(options)

        # 3. Set up monitoring
        monitor = ExecutionMonitor(
            timeout=options.timeout or DEFAULT_TIMEOUT,
            memory_limit=options.memory_limit or DEFAULT_MEMORY,
            on_timeout=self._handle_timeout,
            on_memory_exceeded=self._handle_memory
        )

        # 4. Execute with monitoring
        async with monitor:
            result = await self._execute_in_sandbox(
                skill_id, input, context, sandbox
            )

        # 5. Validate output
        await self._validate_output(skill_id, result)

        return result


@dataclass
class InvocationOptions:
    """Options for skill invocation."""
    timeout: Duration | None = None
    memory_limit: Memory | None = None
    retry_policy: RetryPolicy | None = None
    sandbox_config: SandboxConfig | None = None
    priority: int = 0
```

### 6.3 Retry Policy

```python
@dataclass
class RetryPolicy:
    """Retry configuration for skill invocations."""
    max_attempts: int = 3
    initial_delay: Duration = 1s
    max_delay: Duration = 30s
    exponential_base: float = 2.0
    retryable_errors: list[ErrorType] = field(default_factory=list)
    non_retryable_errors: list[ErrorType] = field(default_factory=list)

# Default: retry on transient errors, not on validation errors
DEFAULT_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    retryable_errors=[
        ErrorType.TIMEOUT,
        ErrorType.TRANSIENT_FAILURE,
        ErrorType.RATE_LIMITED
    ],
    non_retryable_errors=[
        ErrorType.INVALID_INPUT,
        ErrorType.PERMISSION_DENIED,
        ErrorType.ASSERTION_FAILURE
    ]
)
```

---

## 7. Error Handling

### 7.1 Error Taxonomy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ERROR TAXONOMY                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         RUNTIME ERROR                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐      │
│  │   FATAL     │           │   RETRYABLE │           │   WARN      │      │
│  │   (Halt)    │           │   (Retry)   │           │   (Log)     │      │
│  └─────────────┘           └─────────────┘           └─────────────┘      │
│         │                          │                          │             │
│         ▼                          ▼                          ▼             │
│  - Invalid input          - Transient failure        - Performance warning │
│  - Permission denied      - Timeout (retry once)     - Non-critical gap    │
│  - Assertion failure      - Resource temporarily     - Style suggestion    │
│  - Assertion failure      unavailable                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Error Classification

```python
class ErrorType(Enum):
    # Fatal errors (no retry)
    INVALID_INPUT = "invalid_input"
    PERMISSION_DENIED = "permission_denied"
    ASSERTION_FAILURE = "assertion_failure"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"

    # Retryable errors
    TIMEOUT = "timeout"
    TRANSIENT_FAILURE = "transient_failure"
    RATE_LIMITED = "rate_limited"
    RESOURCE_UNAVAILABLE = "resource_unavailable"

    # Warnings (non-blocking)
    PERFORMANCE_WARNING = "performance_warning"
    QUALITY_WARNING = "quality_warning"
    STYLE_SUGGESTION = "style_suggestion"


@dataclass
class ExecutionError:
    """Classified execution error."""
    error_id: str
    type: ErrorType
    source: str                      # skill_id or agent_id
    message: str
    details: dict[str, Any]
    timestamp: timestamp
    recovery_action: RecoveryAction | None
    context: dict[str, Any]          # For debugging
```

### 7.3 Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERROR HANDLING FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐                                                           │
│  │   Error     │                                                           │
│  │   Occurs    │                                                           │
│  └──────┬──────┘                                                           │
│         │                                                                  │
│         ▼                                                                  │
│  ┌─────────────┐    ┌───────────────────────────────────────────┐          │
│  │  Classify   │───▶│   Determine Error Type                    │          │
│  │  Error      │    │   (FATAL / RETRYABLE / WARN)              │          │
│  └─────────────┘    └───────────────────────────────────────────┘          │
│                            │                                               │
│         ┌──────────────────┼──────────────────┐                            │
│         ▼                  ▼                  ▼                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   FATAL     │    │  RETRYABLE  │    │    WARN     │                    │
│  │             │    │             │    │             │                    │
│  │ 1. Log error│    │ 1. Check    │    │ 1. Log with │                    │
│  │ 2. Stop     │    │    retry    │    │    level    │                    │
│  │    execution│    │    budget   │    │    WARN     │                    │
│  │ 3. Capture  │    │ 2. Apply    │    │ 2. Continue │                    │
│  │    state    │    │    backoff  │    │    execution│                    │
│  │ 4. Return   │    │ 3. Retry    │    │ 3. Attach   │                    │
│  │    error    │    │ 4. On fail: │    │    to       │                    │
│  │             │    │    escalate │    │    context  │                    │
│  └─────────────┘    └──────┬──────┘    └─────────────┘                    │
│                            │                                               │
│                            ▼                                               │
│                   ┌─────────────────┐                                       │
│                   │   ESCALATION    │                                       │
│                   │   (if needed)   │                                       │
│                   └─────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.4 Recovery Actions

| Error Type | Recovery Action |
|------------|-----------------|
| `INVALID_INPUT` | Request clarification from user |
| `TIMEOUT` | Retry with longer timeout |
| `TRANSIENT_FAILURE` | Retry with backoff |
| `RESOURCE_UNAVAILABLE` | Wait and retry |
| `NOT_FOUND` | Check input, may need human review |
| `PERMISSION_DENIED` | Request elevated permissions |

---

## 8. Logging and Introspection

### 8.1 Event Types

```python
class EventType(Enum):
    # Engine events
    ENGINE_STARTED = "engine_started"
    ENGINE_STOPPED = "engine_stopped"

    # Request events
    REQUEST_RECEIVED = "request_received"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"

    # Context events
    CONTEXT_CREATED = "context_created"
    CONTEXT_UPDATED = "context_updated"
    CONTEXT_CLEANED = "context_cleaned"

    # Routing events
    AGENT_ROUTED = "agent_routed"
    AGENT_SELECTED = "agent_selected"
    ROUTING_FAILED = "routing_failed"

    # Execution events
    SKILL_INVOKED = "skill_invoked"
    SKILL_COMPLETED = "skill_completed"
    SKILL_FAILED = "skill_failed"

    # Error events
    ERROR_OCCURRED = "error_occurred"
    ERROR_RECOVERED = "error_recovered"
    ERROR_ESCALATED = "error_escalated"

    # Refinement events
    REFINE_REQUESTED = "refine_requested"
    REFINE_COMPLETED = "refine_completed"
```

### 8.2 Trace Event Structure

```python
@dataclass
class TraceEvent:
    """Single event in the execution trace."""
    event_id: str
    event_type: EventType
    timestamp: timestamp
    execution_id: str
    agent_id: str | None
    skill_id: str | None
    message: str
    details: dict[str, Any]
    correlation_id: str | None
    span_id: str | None
    trace_id: str | None
```

### 8.3 Introspection Interface

```python
class IntrospectionService:
    """Centralized logging and introspection."""

    async def log_event(self, event: TraceEvent) -> None:
        """Log a trace event."""
        await self._storage.store(event)
        await self._metrics.record(event)

    async def get_execution_trace(
        self,
        execution_id: str
    ) -> ExecutionTrace:
        """Retrieve complete trace for an execution."""
        events = await self._storage.get_events(execution_id)
        return self._reconstruct_trace(events)

    async def get_execution_metrics(
        self,
        execution_id: str
    ) -> ExecutionMetrics:
        """Get metrics for an execution."""
        return await self._metrics.get_for_execution(execution_id)

    async def search_logs(
        self,
        query: LogQuery
    ) -> list[TraceEvent]:
        """Search logs with filters."""
        return await self._storage.search(query)


@dataclass
class ExecutionTrace:
    """Complete execution trace."""
    execution_id: str
    request: IntelligenceRequest
    events: list[TraceEvent]
    start_time: timestamp
    end_time: timestamp | None
    duration_ms: int | None
    final_state: ExecutionState
    total_skills_invoked: int
    total_errors: int
    agent_timeline: list[AgentTimelineEntry]
```

### 8.4 Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed step tracking | "Input validated for skill X" |
| **INFO** | Key events | "Agent Y routed for task Z" |
| **WARNING** | Non-critical issues | "Timeout approaching for step 5" |
| **ERROR** | Recoverable failures | "Skill X failed, retrying" |
| **CRITICAL** | Unrecoverable failures | "Execution halted due to Y" |

---

## 9. Full Runtime Flow

### 9.1 End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FULL RUNTIME EXECUTION FLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PHASE 1: REQUEST RECEIPT                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. User submits IntelligenceRequest                                 │    │
│  │  2. Engine validates request                                         │    │
│  │  3. Create ExecutionContext                                          │    │
│  │  4. Generate execution_id                                            │    │
│  │  5. Log REQUEST_RECEIVED event                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  PHASE 2: REASONING (No Side Effects)                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  6. Route to InterpreterAgent                                        │    │
│  │  7. Intent Parsing Skill → ParsedIntent                              │    │
│  │  8. Route to ArchitectAgent                                          │    │
│  │  9. Specification Generation Skill → Specification                   │    │
│  │  10. Route to PlannerAgent                                           │    │
│  │  11. Task Decomposition Skill → TaskTree                             │    │
│  │  12. Route to ReviewerAgent                                          │    │
│  │  13. Constraint Validation Skill → ValidationResult                  │    │
│  │  14. Route to PlannerAgent                                           │    │
│  │  15. Execution Planning Skill → ActionPlan                           │    │
│  │  16. Route to ReviewerAgent                                          │    │
│  │  17. Result Evaluation Skill → Approval/Rejection                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼ (Plan Approved)                         │
│  PHASE 3: EXECUTION (Side Effects Allowed)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  18. Route to ExecutorAgent                                          │    │
│  │  19. For each step in ActionPlan:                                    │    │
│  │      a. Route to appropriate agent                                   │    │
│  │      b. Invoke required skill                                        │    │
│  │      c. Capture output                                               │    │
│  │      d. Update ExecutionContext                                      │    │
│  │      e. Log SKILL_INVOKED/SKILL_COMPLETED                           │    │
│  │  20. Aggregate results                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  PHASE 4: EVALUATION                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  21. Route to ReviewerAgent                                          │    │
│  │  22. Result Evaluation Skill → EvaluationReport                      │    │
│  │  23. If should_refine:                                               │    │
│  │      a. Route to RefinerAgent                                        │    │
│  │      b. Apply refinements                                            │    │
│  │      c. Go to PHASE 2 (with modified context)                        │    │
│  │  24. Else: Finalize output                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  PHASE 5: COMPLETION                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  25. Log REQUEST_COMPLETED event                                     │    │
│  │  26. Package Outcome (result, trace, metrics)                        │    │
│  │  27. Return Outcome to caller                                        │    │
│  │  28. Archive ExecutionContext (TTL = 24h)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Sequence Diagram

```
User           Engine         Context       Router       Agents        Skills       Introspection
 │               │              │             │              │              │               │
 │──Submit──────▶│              │             │              │              │               │
 │   Request     │              │             │              │              │               │
 │               │──Create─────▶│             │              │              │               │
 │               │   Context    │             │              │              │               │
 │               │──────────────┼─────────────┼──────────────┼──────────────┼──────────────▶│
 │               │   Log: REQUEST_RECEIVED    │              │              │   Event       │
 │               │              │             │              │              │               │
 │               │──────────────┼────────────▶│ Route to     │              │               │
 │               │   Route      │             │ Interpreter  │              │               │
 │               │              │             │──────────────┼──────────────│               │
 │               │              │             │              │──Invoke─────▶│               │
 │               │              │             │              │ Skill        │               │
 │               │              │◀────────────┼──────────────┼──Result──────┤               │
 │               │              │   Update    │              │              │               │
 │               │──────────────┼─────────────┼──────────────┼──────────────┼──────────────▶│
 │               │   Log: SKILL_COMPLETED     │              │              │   Event       │
 │               │              │             │              │              │               │
 │               │ (Repeat reasoning phases with Architect, Planner, Reviewer)              │
 │               │              │             │              │              │               │
 │               │──────────────┼────────────▶│ Route to     │              │               │
 │               │   Route      │             │ Executor     │              │               │
 │               │              │             │──────────────┼──────────────│               │
 │               │              │             │              │──Invoke─────▶│               │
 │               │              │             │              │ Skill        │               │
 │               │              │◀────────────┼──────────────┼──Result──────┤               │
 │               │              │   Update    │              │              │               │
 │               │──────────────┼─────────────┼──────────────┼──────────────┼──────────────▶│
 │               │   Log: SKILL_COMPLETED     │              │              │   Event       │
 │               │              │             │              │              │               │
 │               │ (Execute all plan steps)                                           │               │
 │               │              │             │              │              │               │
 │               │──────────────┼────────────▶│ Route to     │              │               │
 │               │   Route      │             │ Reviewer     │              │               │
 │               │              │             │──────────────┼──────────────│               │
 │               │              │             │              │──Invoke─────▶│               │
 │               │              │             │              │ Skill        │               │
 │               │              │◀────────────┼──────────────┼──Result──────┤               │
 │               │              │   Update    │              │              │               │
 │               │──────────────┼─────────────┼──────────────┼──────────────┼──────────────▶│
 │               │   Log: REQUEST_COMPLETED   │              │              │   Event       │
 │               │              │             │              │              │               │
 │◀─Outcome─────│              │             │              │              │               │
 │               │              │             │              │              │               │
```

---

## 10. Quality Standards

### 10.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Request to first skill | <100ms | P95 latency |
| Agent routing decision | <10ms | P95 latency |
| Skill invocation overhead | <5ms | P95 latency |
| Error detection to halt | <50ms | P95 latency |
| Trace retrieval | <200ms | P95 latency |
| Concurrent executions | 100+ | Without degradation |

### 10.2 Reliability Targets

| Metric | Target |
|--------|--------|
| Successful executions | >99% |
| Context isolation | 100% (no leakage) |
| Error classification accuracy | >95% |
| Log completeness | 100% events captured |

### 10.3 Safety Guarantees

- No skill can block the engine indefinitely (timeout enforcement)
- Memory usage is capped per execution
- Errors in one execution cannot affect others (isolation)
- All side effects are logged and reversible where possible

---

## 11. Out of Scope

- **Specific agent implementations** — Defined in agent specs
- **Skill implementation details** — Defined in skills spec
- **LLM provider integration** — Abstraction layer handles this
- **Persistence implementation** — Abstracted behind Context interface
- **Network/distributed concerns** — Single-node focus for now

---

## 12. References

- **Intelligence Model:** `specs/core-intelligence-model/spec.md`
- **Cognitive Skills:** `specs/reusable-cognitive-skills/spec.md`
- **Reusable Agents:** `specs/reusable-agents/spec.md`
- **Constitution:** `.specify/memory/constitution.md`

---

**Spec Status:** Draft
**Review Required:** Yes
**Approval Authority:** Architect
