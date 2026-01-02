---
id: 'execution-pipeline'
title: 'Execution Pipeline'
version: '1.0.0'
date: '2025-12-28'
status: 'Draft'
feature: 'execution-pipeline'
branch: 'main'
---

## Overview

The Execution Pipeline orchestrates the flow from user intent to final result through a series of well-defined stages. It handles intent normalization, agent selection, skill execution, context updates, and result delivery with comprehensive error recovery and logging.

## Purpose

- **Structured Flow**: Predictable 6-stage pipeline from intent to result
- **Error Recovery**: Graceful handling and recovery from failures at each stage
- **Retry Logic**: Configurable retry with exponential backoff and circuit breaker
- **Observability**: Logging hooks at every stage for debugging and auditing

## User Scenarios & Testing

### User Story 1 - Successful Execution

As a user, I want my intent to be processed through the pipeline and return a result so that I can accomplish my goal.

**Priority**: P1

**Independent Test**: Submit valid intent, verify result returned through all stages.

**Acceptance Scenarios**:

1. **Given** valid user intent, **When** submitted to pipeline, **Then** all 6 stages complete successfully
2. **Given** completed pipeline, **When** result returned, **Then** result matches expected output schema
3. **Given** pipeline execution, **When** complete, **Then** context updated with all artifacts

### User Story 2 - Error Recovery

As a developer, I want the pipeline to recover from errors gracefully so that users get helpful feedback.

**Priority**: P1

**Independent Test**: Inject errors at various stages, verify recovery behavior.

**Acceptance Scenarios**:

1. **Given** normalization error, **When** intent invalid, **Then** helpful error returned without execution
2. **Given** agent selection fails, **When** no suitable agent, **Then** escalation with alternatives suggested
3. **Given** skill execution fails, **When** retryable error, **Then** retry with backoff before failure
4. **Given** context update fails, **When** storage error, **Then** pipeline continues with warning logged

### User Story 3 - Retry Strategy

As a system, I want to retry transient failures with appropriate backoff so that transient errors don't cause permanent failures.

**Priority**: P1

**Independent Test**: Trigger transient failures, verify retry behavior.

**Acceptance Scenarios**:

1. **Given** transient error (network, rate limit), **When** first attempt fails, **Then** retry after 1s base delay
2. **Given** repeated failures, **When** retrying, **Then** delay doubles each retry (exponential backoff)
3. **Given** max retries exceeded, **When** still failing, **Then** circuit breaker opens
4. **Given** circuit breaker open, **When** new request, **Then** immediately rejected without execution

### User Story 4 - Logging and Auditing

As an operator, I want comprehensive logging at every stage so that I can debug issues and audit usage.

**Priority**: P2

**Independent Test**: Execute pipeline, verify logs at each stage.

**Acceptance Scenarios**:

1. **Given** pipeline execution, **When** stage starts, **Then** entry logged with timestamp and context
2. **Given** pipeline execution, **When** stage completes, **Then** exit logged with duration and outcome
3. **Given** pipeline execution, **When** error occurs, **Then** error logged with stack trace and recovery action
4. **Given** completed pipeline, **When** querying audit trail, **Then** complete sequence of events available

---

## Requirements

### Functional Requirements

- **FR-PIPE-001**: Pipeline MUST process intents through 6 stages: Receive → Normalize → Select → Execute → Update → Return
- **FR-PIPE-002**: Pipeline MUST support parallel execution of independent stages
- **FR-PIPE-003**: Pipeline MUST validate inputs at each stage boundary
- **FR-PIPE-004**: Pipeline MUST update context after each stage completion
- **FR-PIPE-005**: Pipeline MUST support error recovery with fallback paths
- **FR-PIPE-006**: Pipeline MUST implement retry with exponential backoff
- **FR-PIPE-007**: Pipeline MUST emit logging events at stage boundaries
- **FR-PIPE-008**: Pipeline MUST support cancellation at any point

### Non-Functional Requirements

- **NFR-PIPE-001**: Pipeline MUST complete simple requests within 500ms
- **NFR-PIPE-002**: Pipeline MUST handle 100+ concurrent requests
- **NFR-PIPE-003**: Pipeline MUST have <1ms overhead per stage
- **NFR-PIPE-004**: Pipeline MUST be recoverable from mid-execution state
- **NFR-PIPE-005**: Pipeline MUST support custom logging sinks

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Execution Pipeline                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │ Receive │───►│Normalize│───►│  Select │───►│ Execute │───►│ Update  │   │
│  │ Intent  │    │ Intent  │    │  Agent  │    │  Agent  │    │ Context │   │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘   │
│       │              │              │              │              │        │
│       ▼              ▼              ▼              ▼              ▼        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │ Validation│  │ Intent  │  │  Agent  │  │  Skill  │  │ Context │   │
│  │  & Type  │  │ Parsing │  │ Matching│  │ Execution│  │ Storage │   │
│  │  Check   │  │         │  │         │  │         │  │         │   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘   │
│                                                                              │
│       │              │              │              │              │        │
│       └──────────────┴──────────────┴──────────────┴──────────────┘        │
│                                      │                                      │
│                                      ▼                                      │
│                          ┌─────────────────────┐                            │
│                          │      Return         │                            │
│                          │      Result         │                            │
│                          └─────────────────────┘                            │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Cross-Cutting Concerns                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │   │
│  │  │   Error     │  │    Retry    │  │         Logging             │  │   │
│  │  │   Handler   │  │   Strategy  │  │         Hooks               │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Receive Intent

```python
@dataclass
class IntentReceipt:
    """Input to the pipeline."""
    raw_text: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    context_hints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReceiptResult:
    """Output from receipt stage."""
    receipt_id: str
    intent: IntentReceipt
    validated: bool
    validation_errors: List[str] = field(default_factory=list)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)


class ReceiveStage:
    """Stage 1: Receive and validate user intent."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = PipelineLogger("receive_stage")

    def execute(self, receipt: IntentReceipt) -> ReceiptResult:
        """Process incoming intent."""
        receipt_id = self._generate_receipt_id()

        self.logger.info(f"Received intent: {receipt_id}", {
            "receipt_id": receipt_id,
            "user_id": receipt.user_id,
            "has_attachments": len(receipt.attachments) > 0
        })

        # Validate receipt structure
        is_valid, errors = self._validate_receipt(receipt)

        # Create context for pipeline
        context_snapshot = {
            "receipt_id": receipt_id,
            "user_id": receipt.user_id,
            "session_id": receipt.session_id,
            "timestamp": receipt.timestamp.isoformat(),
            "raw_intent": receipt.raw_text
        }

        return ReceiptResult(
            receipt_id=receipt_id,
            intent=receipt,
            validated=is_valid,
            validation_errors=errors,
            context_snapshot=context_snapshot
        )

    def _validate_receipt(self, receipt: IntentReceipt) -> tuple[bool, List[str]]:
        """Validate receipt has required fields."""
        errors = []
        if not receipt.raw_text or not receipt.raw_text.strip():
            errors.append("raw_text is required and must not be empty")
        if len(receipt.raw_text) > self.config.max_intent_length:
            errors.append(f"raw_text exceeds max length of {self.config.max_intent_length}")
        return len(errors) == 0, errors

    def _generate_receipt_id(self) -> str:
        """Generate unique receipt ID."""
        import uuid
        return f"receipt-{uuid.uuid4().hex[:12]}"
```

### Stage 2: Normalize Intent

```python
@dataclass
class NormalizedIntent:
    """Normalized intent output."""
    receipt_id: str
    canonical_form: str
    intent_type: str
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    ambiguity_detected: bool = False
    suggested_clarifications: List[str] = field(default_factory=list)
    normalized_at: datetime = field(default_factory=datetime.utcnow)


class NormalizeStage:
    """Stage 2: Normalize and parse intent."""

    def __init__(self, config: PipelineConfig, intent_parser: "Skill"):
        self.config = config
        self.intent_parser = intent_parser
        self.logger = PipelineLogger("normalize_stage")

    def execute(self, receipt_result: ReceiptResult) -> NormalizedIntent:
        """Normalize the intent."""
        self.logger.info(f"Normalizing intent: {receipt_result.receipt_id}")

        # Parse intent using skill
        skill_context = SkillContext(
            inputs={"text": receipt_result.intent.raw_text},
            shared_context=receipt_result.context_snapshot,
            metrics=self._create_metrics_collector()
        )

        try:
            parse_result = self.intent_parser.execute(skill_context)

            normalized = NormalizedIntent(
                receipt_id=receipt_result.receipt_id,
                canonical_form=parse_result.get("canonical_form", receipt_result.intent.raw_text),
                intent_type=parse_result.get("intent_type", "general"),
                entities=parse_result.get("entities", {}),
                confidence=parse_result.get("confidence", 0.9),
                ambiguity_detected=parse_result.get("ambiguity_detected", False),
                suggested_clarifications=parse_result.get("clarifications", [])
            )

            self.logger.info(f"Intent normalized: {normalized.intent_type}", {
                "receipt_id": normalized.receipt_id,
                "intent_type": normalized.intent_type,
                "confidence": normalized.confidence
            })

            return normalized

        except Exception as e:
            self.logger.error(f"Normalization failed: {e}")
            # Fallback: use raw text as canonical form
            return NormalizedIntent(
                receipt_id=receipt_result.receipt_id,
                canonical_form=receipt_result.intent.raw_text,
                intent_type="general",
                confidence=0.5,
                ambiguity_detected=True,
                suggested_clarifications=["Could not parse intent, please rephrase"]
            )
```

### Stage 3: Select Agent

```python
@dataclass
class AgentSelection:
    """Agent selection result."""
    receipt_id: str
    selected_agent: str
    confidence: float
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    selection_reason: str = ""
    agent_config: Dict[str, Any] = field(default_factory=dict)


class SelectStage:
    """Stage 3: Select appropriate agent for intent."""

    def __init__(self, config: PipelineConfig, agent_registry: AgentRegistry):
        self.config = config
        self.registry = agent_registry
        self.logger = PipelineLogger("select_stage")

    def execute(self, normalized: NormalizedIntent) -> AgentSelection:
        """Select best agent for intent."""
        self.logger.info(f"Selecting agent for: {normalized.intent_type}")

        # Find capable agents
        candidates = self.registry.find_by_capability(normalized.intent_type)

        if not candidates:
            # Fallback: search by general capability
            candidates = self.registry.find_by_capability("general_purpose")

        if not candidates:
            return AgentSelection(
                receipt_id=normalized.receipt_id,
                selected_agent="",
                confidence=0.0,
                selection_reason="No suitable agent found"
            )

        # Score and rank candidates
        scored = []
        for agent_name in candidates:
            agent = self.registry.get(agent_name)
            if agent:
                confidence = agent.can_handle(normalized.intent_type, normalized.entities)
                scored.append({
                    "name": agent_name,
                    "confidence": confidence,
                    "metadata": agent.metadata
                })

        # Sort by confidence
        scored.sort(key=lambda x: x["confidence"], reverse=True)

        best = scored[0]
        alternatives = [
            {"name": s["name"], "confidence": s["confidence"]}
            for s in scored[1:4]  # Top 3 alternatives
        ]

        self.logger.info(f"Agent selected: {best['name']}", {
            "agent": best["name"],
            "confidence": best["confidence"],
            "alternatives": len(alternatives)
        })

        return AgentSelection(
            receipt_id=normalized.receipt_id,
            selected_agent=best["name"],
            confidence=best["confidence"],
            alternatives=alternatives,
            selection_reason=f"Best match for intent type '{normalized.intent_type}'"
        )
```

### Stage 4: Execute Agent

```python
@dataclass
class ExecutionResult:
    """Result from agent execution."""
    receipt_id: str
    agent_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    artifacts: List[str] = field(default_factory=list)
    duration_ms: int = 0
    steps: List[ExecutionStep] = field(default_factory=list)
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_category: Optional[str] = None
    recovery_action: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class ExecuteStage:
    """Stage 4: Execute selected agent."""

    def __init__(self, config: PipelineConfig, agent_engine: AgentEngine,
                 retry_strategy: RetryStrategy, error_handler: ErrorHandler):
        self.config = config
        self.agent_engine = agent_engine
        self.retry_strategy = retry_strategy
        self.error_handler = error_handler
        self.logger = PipelineLogger("execute_stage")

    def execute(self, selection: AgentSelection,
                normalized: NormalizedIntent) -> ExecutionResult:
        """Execute the selected agent."""
        self.logger.info(f"Executing agent: {selection.selected_agent}")

        start_time = datetime.utcnow()

        # Build agent input
        agent_input = AgentInput(
            task_type=normalized.intent_type,
            payload={
                "intent": normalized.canonical_form,
                "entities": normalized.entities
            },
            session_id=normalized.receipt_id,
            options=selection.agent_config
        )

        # Execute with retry
        result = self._execute_with_retry(selection, agent_input)

        # Record metrics
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return ExecutionResult(
            receipt_id=normalized.receipt_id,
            agent_name=selection.selected_agent,
            success=result.is_success(),
            output=result.output.payload if result.output else None,
            artifacts=result.artifacts_created,
            duration_ms=int(duration_ms),
            steps=result.steps_executed,
            error=result.error,
            error_code=result.error_code,
            error_category=result.error_category,
            recovery_action=result.recovery_action,
            metrics=result.metadata
        )

    def _execute_with_retry(self, selection: AgentSelection,
                            input: AgentInput) -> AgentResult:
        """Execute with retry strategy."""
        for attempt in range(self.retry_strategy.max_retries + 1):
            try:
                result = self.agent_engine.invoke_agent(
                    selection.selected_agent,
                    input
                )

                if result.is_success():
                    return result

                # Handle non-retryable errors
                if not self._is_retryable(result.error_category):
                    return result

                # Log retry attempt
                self.logger.warning(f"Attempt {attempt + 1} failed: {result.error}")

            except Exception as e:
                if not self._is_retryable_exception(e):
                    raise
                self.logger.warning(f"Attempt {attempt + 1} exception: {str(e)}")

            # Wait before retry
            if attempt < self.retry_strategy.max_retries:
                delay = self.retry_strategy.calculate_delay(attempt)
                self._sleep(delay)

        # Max retries exceeded
        return AgentResult(
            agent_name=selection.selected_agent,
            task_type=input.task_type,
            status=ResultStatus.FAILURE,
            error="Max retries exceeded",
            error_code="E300",
            error_category="timeout"
        )

    def _is_retryable(self, error_category: Optional[str]) -> bool:
        """Check if error is retryable."""
        return error_category in ["timeout", "execution", "resource"]

    def _is_retryable_exception(self, e: Exception) -> bool:
        """Check if exception is retryable."""
        return isinstance(e, (NetworkError, RateLimitError, TimeoutError))

    def _sleep(self, ms: int) -> None:
        """Sleep for specified milliseconds."""
        import time
        time.sleep(ms / 1000)
```

### Stage 5: Update Context

```python
@dataclass
class ContextUpdate:
    """Result of context update."""
    receipt_id: str
    success: bool
    updated_keys: List[str] = field(default_factory=list)
    error: Optional[str] = None
    snapshot: Dict[str, Any] = field(default_factory=dict)


class UpdateStage:
    """Stage 5: Update shared context with results."""

    def __init__(self, config: PipelineConfig, context: SharedContext):
        self.config = config
        self.context = context
        self.logger = PipelineLogger("update_stage")

    def execute(self, execution: ExecutionResult,
                normalized: NormalizedIntent) -> ContextUpdate:
        """Update context with execution results."""
        self.logger.info(f"Updating context: {execution.receipt_id}")

        try:
            # Record execution step
            step = ExecutionStep(
                step_type="agent_execution",
                agent=execution.agent_name,
                action=execution.receipt_id,
                status="success" if execution.success else "failure",
                duration_ms=execution.duration_ms
            )
            self.context.record_execution_step(step)

            # Update goals if applicable
            if execution.success:
                self._update_goals(execution, normalized)

            # Store artifacts
            for artifact_id in execution.artifacts:
                self._link_artifact(artifact_id, execution)

            # Update conversation state
            self._update_conversation(execution, normalized)

            # Get snapshot for return
            snapshot = self.context.snapshot()

            return ContextUpdate(
                receipt_id=execution.receipt_id,
                success=True,
                updated_keys=["execution_history", "goals", "artifacts", "conversation"],
                snapshot=snapshot
            )

        except Exception as e:
            self.logger.error(f"Context update failed: {e}")
            return ContextUpdate(
                receipt_id=execution.receipt_id,
                success=False,
                error=str(e)
            )

    def _update_goals(self, execution: ExecutionResult,
                      normalized: NormalizedIntent) -> None:
        """Update goal status based on execution."""
        active_goals = self.context.get_active_goals()
        for goal in active_goals:
            if goal.metadata.get("receipt_id") == execution.receipt_id:
                goal.update_status(GoalStatus.COMPLETED)

    def _link_artifact(self, artifact_id: str,
                       execution: ExecutionResult) -> None:
        """Link artifact to execution."""
        # Store artifact reference in context
        self.context.set(
            f"artifact_{artifact_id}",
            {
                "created_by": execution.agent_name,
                "created_at": datetime.utcnow().isoformat(),
                "receipt_id": execution.receipt_id
            }
        )

    def _update_conversation(self, execution: ExecutionResult,
                             normalized: NormalizedIntent) -> None:
        """Update conversation state."""
        turn = ConversationTurn(
            role="agent",
            message=str(execution.output),
            intent=normalized.intent_type,
            entities=normalized.entities
        )
        self.context.add_turn(turn)
```

### Stage 6: Return Result

```python
@dataclass
class PipelineResult:
    """Final result from pipeline."""
    receipt_id: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    recovery_suggestion: Optional[str] = None
    duration_ms: int = 0
    stages_completed: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReturnStage:
    """Stage 6: Return final result to user."""

    def __init__(self, config: PipelineConfig, result_formatter: ResultFormatter):
        self.config = config
        self.formatter = result_formatter
        self.logger = PipelineLogger("return_stage")

    def execute(self, execution: ExecutionResult,
                context_update: ContextUpdate,
                normalized: NormalizedIntent) -> PipelineResult:
        """Return final result."""
        self.logger.info(f"Returning result: {execution.receipt_id}")

        # Format output
        if execution.success:
            output = self.formatter.format_success(execution, normalized)
        else:
            output = self.formatter.format_error(execution)

        return PipelineResult(
            receipt_id=execution.receipt_id,
            success=execution.success,
            output=output,
            error=execution.error,
            error_code=execution.error_code,
            recovery_suggestion=execution.recovery_action,
            duration_ms=execution.duration_ms,
            stages_completed=["receive", "normalize", "select", "execute", "update"],
            artifacts=execution.artifacts,
            context_snapshot=context_update.snapshot,
            metadata={
                "agent": execution.agent_name,
                "intent_type": normalized.intent_type,
                "confidence": normalized.confidence
            }
        )
```

---

## Error Recovery

```python
class ErrorRecoveryStrategy(Enum):
    """Strategies for error recovery."""
    RETRY = "retry"
    FALLBACK_AGENT = "fallback_agent"
    FALLBACK_OUTPUT = "fallback_output"
    SKIP_STAGE = "skip_stage"
    ESCALATE = "escalate"
    ABORT = "abort"


class ErrorRecoveryConfig:
    """Configuration for error recovery."""
    default_strategy: ErrorRecoveryStrategy = ErrorRecoveryStrategy.RETRY
    max_recovery_attempts: int = 3
    fallback_agents: Dict[str, List[str]] = field(default_factory=dict)  # agent -> alternatives
    fallback_outputs: Dict[str, Any] = field(default_factory=dict)  # intent_type -> output
    stage_skip_order: List[str] = field(default_factory=list)


class ErrorRecovery:
    """Handles error recovery across pipeline stages."""

    def __init__(self, config: ErrorRecoveryConfig, registry: SkillRegistry):
        self.config = config
        self.registry = registry
        self.circuit_breaker = CircuitBreaker()

    def handle_error(self, stage: str, error: Exception,
                     context: Dict[str, Any]) -> RecoveryAction:
        """Handle an error and determine recovery action."""
        # Check circuit breaker
        if self.circuit_breaker.is_open(stage):
            return RecoveryAction(
                strategy=ErrorRecoveryStrategy.ESCALATE,
                reason="Circuit breaker open",
                fallback_output={"error": "Service temporarily unavailable"}
            )

        # Determine error category
        category = self._categorize_error(error)

        # Apply recovery strategy based on category
        if category in ["validation", "routing"]:
            return RecoveryAction(
                strategy=ErrorRecoveryStrategy.ABORT,
                reason=f"Non-recoverable error in {stage}",
                error_message=str(error)
            )

        if category == "timeout":
            return RecoveryAction(
                strategy=ErrorRecoveryStrategy.RETRY,
                reason="Retryable timeout",
                retry_after_ms=1000
            )

        if category == "execution":
            return self._handle_execution_error(stage, error, context)

        return RecoveryAction(
            strategy=ErrorRecoveryStrategy.RETRY,
            reason="Default retry"
        )

    def _handle_execution_error(self, stage: str, error: Exception,
                                 context: Dict[str, Any]) -> RecoveryAction:
        """Handle execution errors with fallback."""
        agent_name = context.get("agent_name")

        # Try fallback agent
        if agent_name and agent_name in self.config.fallback_agents:
            alternatives = self.config.fallback_agents[agent_name]
            return RecoveryAction(
                strategy=ErrorRecoveryStrategy.FALLBACK_AGENT,
                reason=f"Fallback to {alternatives[0]}",
                fallback_agent=alternatives[0]
            )

        # Try fallback output
        intent_type = context.get("intent_type")
        if intent_type and intent_type in self.config.fallback_outputs:
            return RecoveryAction(
                strategy=ErrorRecoveryStrategy.FALLBACK_OUTPUT,
                reason="Using fallback output",
                fallback_output=self.config.fallback_outputs[intent_type]
            )

        return RecoveryAction(
            strategy=ErrorRecoveryStrategy.RETRY,
            reason="No fallback available, retrying"
        )
```

---

## Retry Strategy

```python
@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    exponential_base: int = 2
    jitter: bool = True
    jitter_factor: float = 0.1
    retryable_categories: List[str] = field(default_factory=lambda: [
        "timeout", "execution", "resource", "rate_limit"
    ])


class RetryStrategy:
    """Implements retry with exponential backoff and jitter."""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempt_counts: Dict[str, int] = {}

    def should_retry(self, stage: str, error: Exception) -> bool:
        """Determine if retry should be attempted."""
        attempts = self.attempt_counts.get(stage, 0)
        if attempts >= self.config.max_attempts:
            return False

        category = self._get_error_category(error)
        return category in self.config.retryable_categories

    def calculate_delay(self, attempt: int) -> int:
        """Calculate delay before next retry."""
        delay = self.config.base_delay_ms * (self.config.exponential_base ** attempt)

        # Cap at max delay
        delay = min(delay, self.config.max_delay_ms)

        # Add jitter
        if self.config.jitter:
            jitter_range = delay * self.config.jitter_factor
            delay = delay + (hash(str(attempt)) % int(jitter_range * 2)) - jitter_range

        return int(delay)

    def record_attempt(self, stage: str) -> None:
        """Record retry attempt."""
        self.attempt_counts[stage] = self.attempt_counts.get(stage, 0) + 1

    def reset_attempts(self, stage: str) -> None:
        """Reset attempt count for stage."""
        self.attempt_counts.pop(stage, None)

    def _get_error_category(self, error: Exception) -> str:
        """Get error category for retry decision."""
        error_str = str(error).lower()
        if "timeout" in error_str:
            return "timeout"
        if "rate limit" in error_str:
            return "rate_limit"
        if "resource" in error_str:
            return "resource"
        return "execution"


class CircuitBreaker:
    """Circuit breaker for preventing cascade failures."""

    def __init__(self, failure_threshold: int = 5,
                 recovery_timeout_ms: int = 30000):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_ms = recovery_timeout_ms
        self.state: Dict[str, Dict[str, Any]] = {}  # stage -> state

    def record_failure(self, stage: str) -> None:
        """Record a failure for the stage."""
        if stage not in self.state:
            self.state[stage] = {
                "failures": 0,
                "last_failure": None,
                "state": "closed"
            }

        self.state[stage]["failures"] += 1
        self.state[stage]["last_failure"] = datetime.utcnow()

        if self.state[stage]["failures"] >= self.failure_threshold:
            self.state[stage]["state"] = "open"

    def record_success(self, stage: str) -> None:
        """Record a success, potentially closing the circuit."""
        if stage in self.state:
            self.state[stage]["failures"] = 0
            self.state[stage]["state"] = "closed"

    def is_open(self, stage: str) -> bool:
        """Check if circuit breaker is open."""
        if stage not in self.state:
            return False

        state = self.state[stage]
        if state["state"] == "closed":
            return False

        # Check if recovery timeout has elapsed
        elapsed = (datetime.utcnow() - state["last_failure"]).total_seconds() * 1000
        if elapsed > self.recovery_timeout_ms:
            state["state"] = "half-open"
            return False

        return True
```

---

## Logging Hooks

```python
class PipelineLogger:
    """Structured logger for pipeline events."""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.event_log: List[Dict[str, Any]] = []

    def debug(self, message: str, context: Dict[str, Any] = {}) -> None:
        """Log debug event."""
        self._log("DEBUG", message, context)

    def info(self, message: str, context: Dict[str, Any] = {}) -> None:
        """Log info event."""
        self._log("INFO", message, context)

    def warning(self, message: str, context: Dict[str, Any] = {}) -> None:
        """Log warning event."""
        self._log("WARNING", message, context)

    def error(self, message: str, context: Dict[str, Any] = {}) -> None:
        """Log error event."""
        self._log("ERROR", message, context)

    def _log(self, level: str, message: str, context: Dict[str, Any]) -> None:
        """Emit log event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "stage": self.stage_name,
            "message": message,
            "context": context
        }
        self.event_log.append(event)
        # Emit to logging system
        self._emit(event)

    def _emit(self, event: Dict[str, Any]) -> None:
        """Emit event to logging infrastructure."""
        # In production, emit to configured sinks
        pass

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all logged events."""
        return self.event_log

    def clear(self) -> None:
        """Clear event log."""
        self.event_log.clear()


class LoggingHooks:
    """Logging hooks at each pipeline stage boundary."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.hooks: Dict[str, List[callable]] = {
            "on_stage_start": [],
            "on_stage_complete": [],
            "on_stage_error": [],
            "on_pipeline_start": [],
            "on_pipeline_complete": [],
            "on_pipeline_error": []
        }

    def register_hook(self, event: str, hook: callable) -> None:
        """Register a logging hook."""
        if event in self.hooks:
            self.hooks[event].append(hook)

    def emit(self, event: str, data: Dict[str, Any]) -> None:
        """Emit event to all registered hooks."""
        for hook in self.hooks.get(event, []):
            try:
                hook(data)
            except Exception:
                pass  # Hooks must not fail


# Example logging hook implementations

def structured_log_hook(data: Dict[str, Any]) -> None:
    """Emit structured logs to logging system."""
    print(f"[{data['timestamp']}] {data['level']}: {data['message']}")


def metrics_hook(data: Dict[str, Any]) -> None:
    """Record metrics for monitoring."""
    if data["level"] == "ERROR":
        increment_counter("pipeline.errors", {"stage": data["stage"]})
    elif data["level"] == "INFO" and "complete" in data["message"]:
        increment_counter("pipeline.completions", {"stage": data["stage"]})


def audit_hook(data: Dict[str, Any]) -> None:
    """Record audit trail for compliance."""
    if data["level"] in ["ERROR", "WARNING"]:
        append_to_audit_trail({
            "timestamp": data["timestamp"],
            "event": data["message"],
            "stage": data["stage"],
            "context": data["context"]
        })
```

---

## Complete Pipeline Orchestration

```python
@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    max_intent_length: int = 10000
    enable_metrics: bool = True
    enable_tracing: bool = True
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    error_recovery_config: ErrorRecoveryConfig = field(default_factory=ErrorRecoveryConfig)
    logging_hooks: LoggingHooks = field(default_factory=LoggingHooks)


class ExecutionPipeline:
    """
    Complete execution pipeline orchestrator.

    Coordinates all 6 stages with error recovery, retry, and logging.
    """

    def __init__(self, config: PipelineConfig,
                 stages: Dict[str, Any],  # Stage implementations
                 registry: SkillRegistry,
                 context: SharedContext):
        self.config = config
        self.stages = stages
        self.registry = registry
        self.context = context
        self.logger = PipelineLogger("pipeline")

        # Initialize error handling
        self.retry_strategy = RetryStrategy(config.retry_config)
        self.error_recovery = ErrorRecovery(config.error_recovery_config, registry)
        self.error_handler = ErrorHandler(ErrorStrategy.ERROR)

    def execute(self, receipt: IntentReceipt) -> PipelineResult:
        """
        Execute the complete pipeline.

        Args:
            receipt: User intent to process

        Returns:
            PipelineResult with output or error
        """
        pipeline_id = self._generate_pipeline_id()
        start_time = datetime.utcnow()

        self.logger.info("Pipeline started", {"pipeline_id": pipeline_id})
        self.config.logging_hooks.emit("on_pipeline_start", {
            "pipeline_id": pipeline_id,
            "receipt": receipt
        })

        # Track stages
        stages_completed = []
        last_error = None

        try:
            # Stage 1: Receive
            receipt_result = self._execute_stage(
                "receive", self.stages["receive"], receipt
            )
            stages_completed.append("receive")

            # Stage 2: Normalize
            normalized = self._execute_stage(
                "normalize", self.stages["normalize"], receipt_result
            )
            stages_completed.append("normalize")

            # Stage 3: Select
            selection = self._execute_stage(
                "select", self.stages["select"], normalized
            )
            stages_completed.append("select")

            # Stage 4: Execute
            execution = self._execute_stage(
                "execute", self.stages["execute"], selection, normalized
            )
            stages_completed.append("execute")

            # Stage 5: Update
            context_update = self._execute_stage(
                "update", self.stages["update"], execution, normalized
            )
            stages_completed.append("update")

            # Stage 6: Return
            result = self._execute_stage(
                "return", self.stages["return"], execution, context_update, normalized
            )
            stages_completed.append("return")

            # Success
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            self.logger.info("Pipeline completed", {
                "pipeline_id": pipeline_id,
                "duration_ms": duration_ms
            })
            self.config.logging_hooks.emit("on_pipeline_complete", {
                "pipeline_id": pipeline_id,
                "result": result,
                "duration_ms": duration_ms
            })

            return result

        except Exception as e:
            last_error = e
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            self.logger.error(f"Pipeline failed: {e}", {"pipeline_id": pipeline_id})
            self.config.logging_hooks.emit("on_pipeline_error", {
                "pipeline_id": pipeline_id,
                "error": str(e),
                "stages_completed": stages_completed
            })

            return self._create_error_result(receipt, e, stages_completed, duration_ms)

    def _execute_stage(self, stage_name: str, stage: Any,
                       *args) -> Any:
        """Execute a single stage with error handling."""
        self.logger.info(f"Stage '{stage_name}' started")

        try:
            result = stage.execute(*args)

            self.logger.info(f"Stage '{stage_name}' completed", {
                "stage": stage_name,
                "success": True
            })

            return result

        except Exception as e:
            self.logger.error(f"Stage '{stage_name}' failed: {e}")

            # Try error recovery
            recovery = self.error_recovery.handle_error(
                stage_name, e, {"args": str(args)}
            )

            if recovery.strategy == ErrorRecoveryStrategy.ABORT:
                raise

            elif recovery.strategy == ErrorRecoveryStrategy.RETRY:
                self.retry_strategy.record_attempt(stage_name)
                delay = self.retry_strategy.calculate_delay(
                    self.retry_strategy.attempt_counts.get(stage_name, 0)
                )
                self._sleep(delay)
                return self._execute_stage(stage_name, stage, *args)

            elif recovery.strategy == ErrorRecoveryStrategy.FALLBACK_AGENT:
                # Modify args for fallback agent and retry
                return self._execute_stage(stage_name, stage, *args)

            elif recovery.strategy == ErrorRecoveryStrategy.FALLBACK_OUTPUT:
                return recovery.fallback_output

            else:
                raise

    def _create_error_result(self, receipt: IntentReceipt, error: Exception,
                             stages_completed: List[str], duration_ms: int) -> PipelineResult:
        """Create error result."""
        return PipelineResult(
            receipt_id=receipt.raw_text[:20] if receipt.raw_text else "unknown",
            success=False,
            error=str(error),
            duration_ms=duration_ms,
            stages_completed=stages_completed,
            recovery_suggestion="Please rephrase your request or try again later"
        )

    def _generate_pipeline_id(self) -> str:
        """Generate unique pipeline ID."""
        import uuid
        return f"pipeline-{uuid.uuid4().hex[:12]}"

    def _sleep(self, ms: int) -> None:
        """Sleep for milliseconds."""
        import time
        time.sleep(ms / 1000)
```

---

## Summary

| Stage | Purpose | Key Methods |
|-------|---------|-------------|
| **1. Receive** | Validate and receipt intent | `execute(receipt)`, `_validate_receipt()` |
| **2. Normalize** | Parse and canonicalize intent | `execute(receipt_result)`, intent parsing skill |
| **3. Select** | Choose best agent | `execute(normalized)`, agent registry lookup |
| **4. Execute** | Run agent with skills | `execute(selection)`, retry with backoff |
| **5. Update** | Store results in context | `execute(execution)`, record step, update goals |
| **6. Return** | Format and deliver result | `execute(execution, update)`, format output |

**Error Recovery**: RETRY → FALLBACK_AGENT → FALLBACK_OUTPUT → SKIP → ESCALATE → ABORT

**Retry Strategy**: Exponential backoff with jitter, max 3 attempts, circuit breaker

**Logging Hooks**: on_stage_start, on_stage_complete, on_stage_error, on_pipeline_start, on_pipeline_complete, on_pipeline_error

**PHR**: `history/prompts/execution-pipeline/001-define-execution-pipeline.spec.prompt.md`
