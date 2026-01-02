---
id: 'shared-context-model'
title: 'Shared Context Model'
version: '1.0.0'
date: '2025-12-28'
status: 'Draft'
feature: 'shared-context-model'
branch: 'main'
---

## Overview

The Shared Context Model provides a unified, structured container for all runtime state in the intelligence layer. It serves as the single source of truth for conversation state, goals, constraints, artifacts, and execution history.

## Purpose

- **Conversation State**: Track the current state of interactions with users and agents
- **Goals & Constraints**: Maintain active goals and their associated constraints
- **Intermediate Artifacts**: Store generated outputs from reasoning and execution steps
- **Execution History**: Record the sequence of operations for debugging and resume
- **Serialization**: Enable persistence, transfer, and recovery of context state

## User Scenarios & Testing

### User Story 1 - Multi-Agent State Sharing

As a developer, I want multiple agents to share state through a common context so that they can collaborate on complex tasks.

**Priority**: P1

**Independent Test**: Two agents read/write to context and verify state consistency.

**Acceptance Scenarios**:

1. **Given** context with conversation state, **When** Agent A writes to `conversation.turn_count`, **Then** Agent B reads updated value
2. **Given** context with active goals, **When** Agent A adds a new goal, **Then** Agent B sees the goal in `goals.active`
3. **Given** empty context, **When** multiple agents read simultaneously, **Then** no race conditions occur

### User Story 2 - Goal Tracking

As a developer, I want the context to track goals and their constraints so that agents can work toward explicit objectives.

**Priority**: P1

**Independent Test**: Add/update goals and verify constraints are enforced.

**Acceptance Scenarios**:

1. **Given** context with no goals, **When** Agent adds goal "implement feature X", **Then** goal appears in `goals.active` with PENDING status
2. **Given** goal with constraints, **When** agent action violates constraint, **Then** constraint violation is detected
3. **Given** completed goal, **When** goal marked complete, **Then** goal moves from `active` to `completed`

### User Story 3 - Artifact Storage

As a developer, I want to store intermediate artifacts in context so that they can be retrieved by downstream agents.

**Priority**: P1

**Independent Test**: Store artifact, verify retrieval by name and version.

**Acceptance Scenarios**:

1. **Given** context with no artifacts, **When** Agent stores `spec_v1.json`, **Then** artifact appears in `artifacts.generated`
2. **Given** artifact with name "spec", **When** Agent retrieves "spec", **Then** latest version is returned
3. **Given** artifact version history, **When** specific version requested, **Then** exact version returned

### User Story 4 - Execution History

As a developer, I want execution history recorded in context so that I can debug and resume workflows.

**Priority**: P1

**Independent Test**: Execute steps, verify history recording.

**Acceptance Scenarios**:

1. **Given** empty history, **When** Agent executes action, **Then** entry appears in `execution.history`
2. **Given** history with entries, **When** querying recent actions, **Then** entries returned in order with timestamps
3. **Given** failed execution, **When** recording failure, **Then** error details stored with stack trace

### User Story 5 - Serialization

As a developer, I want context to be serializable so that I can save and restore state.

**Priority**: P1

**Independent Test**: Serialize context, delete, restore from snapshot.

**Acceptance Scenarios**:

1. **Given** context with data, **When** serialized to JSON, **Then** all fields preserved
2. **Given** serialized context, **When** restored, **Then** all data matches original
3. **Given** context at point T1, **When** modified, **Then** snapshot at T1 remains unchanged

---

## Requirements

### Functional Requirements

- **FR-CTX-001**: Context MUST store conversation state with turn tracking and intent history
- **FR-CTX-002**: Context MUST track goals with status, priority, and dependencies
- **FR-CTX-003**: Context MUST enforce constraints associated with goals
- **FR-CTX-004**: Context MUST store intermediate artifacts with versioning
- **FR-CTX-005**: Context MUST record execution history with timestamps and outcomes
- **FR-CTX-006**: Context MUST be serializable to/from JSON
- **FR-CTX-007**: Context MUST support incremental updates without full serialization
- **FR-CTX-008**: Context MUST provide atomic read-modify-write operations

### Non-Functional Requirements

- **NFR-CTX-001**: Context operations MUST complete within 5ms for reads, 10ms for writes
- **NFR-CTX-002**: Context MUST support 1000+ concurrent reads
- **NFR-CTX-003**: Context snapshot MUST be at most 10MB
- **NFR-CTX-004**: Context MUST be immutable to consumers (copy-on-write semantics)
- **NFR-CTX-005**: Context MUST support TTL-based expiration for session data

---

## Context Schema

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json
import uuid


class ContextScope(Enum):
    """Context visibility scopes."""
    GLOBAL = "global"        # Visible to all sessions, engine lifetime
    SESSION = "session"      # Visible within single session
    TASK = "task"            # Visible within single task/operation


class ContextAccess(Enum):
    """Access permission levels."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class GoalStatus(Enum):
    """Goal completion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ConstraintType(Enum):
    """Types of constraints that can be enforced."""
    MAX_TOKENS = "max_tokens"
    MAX_TIME = "max_time"
    REQUIRED_FIELDS = "required_fields"
    PATTERN_MATCH = "pattern_match"
    VALUE_RANGE = "value_range"
    MUTEX = "mutex"          # Mutually exclusive with another goal


@dataclass
class Constraint:
    """A constraint on goal execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: ConstraintType
    value: Any
    description: str = ""
    enforced: bool = True
    violation_action: str = "fail"  # "fail", "warn", "skip"

    def validate(self, input_value: Any) -> tuple[bool, str]:
        """Validate input against constraint."""
        if self.type == ConstraintType.MAX_TOKENS:
            if isinstance(input_value, dict) and "tokens" in input_value:
                return input_value["tokens"] <= self.value, f"Token count exceeds {self.value}"
        elif self.type == ConstraintType.MAX_TIME:
            if isinstance(input_value, dict) and "duration_ms" in input_value:
                return input_value["duration_ms"] <= self.value, f"Duration exceeds {self.value}ms"
        elif self.type == ConstraintType.REQUIRED_FIELDS:
            if isinstance(input_value, dict):
                missing = [f for f in self.value if f not in input_value]
                return len(missing) == 0, f"Missing required fields: {missing}"
        elif self.type == ConstraintType.PATTERN_MATCH:
            import re
            if isinstance(input_value, str):
                return bool(re.match(self.value, input_value)), f"Pattern {self.value} not matched"
        elif self.type == ConstraintType.VALUE_RANGE:
            if isinstance(input_value, (int, float)):
                min_val, max_val = self.value
                return min_val <= input_value <= max_val, f"Value {input_value} outside range"
        return True, "Valid"


@dataclass
class Goal:
    """A goal to be achieved by agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str = ""
    status: GoalStatus = GoalStatus.PENDING
    priority: int = 0  # Higher = more urgent
    parent_id: Optional[str] = None  # Sub-goal hierarchy
    dependencies: List[str] = field(default_factory=list)  # Goal IDs that must complete first
    constraints: List[Constraint] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    assignee: Optional[str] = None  # Agent or role responsible
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_constraint(self, constraint: Constraint) -> bool:
        """Add constraint to goal."""
        self.constraints.append(constraint)
        self.updated_at = datetime.utcnow()
        return True

    def update_status(self, new_status: GoalStatus) -> bool:
        """Update goal status."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        if new_status == GoalStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
        return True


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str  # "user", "agent", "system"
    message: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Artifact:
    """An intermediate artifact generated during execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    version: int = 1
    content_type: str = "application/json"
    data: Any = None
    schema: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    parent_id: Optional[str] = None  # For derived artifacts
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def new_version(self, data: Any) -> "Artifact":
        """Create a new version of this artifact."""
        return Artifact(
            name=self.name,
            version=self.version + 1,
            content_type=self.content_type,
            data=data,
            schema=self.schema,
            created_by=self.created_by,
            parent_id=self.id,
            tags=self.tags,
            metadata=self.metadata
        )


@dataclass
class ExecutionStep:
    """A single step in execution history."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    step_type: str  # "reasoning", "planning", "execution", "evaluation"
    agent: Optional[str] = None
    action: str
    input_summary: Dict[str, Any] = field(default_factory=dict)
    output_summary: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # "success", "failure", "partial"
    error: Optional[str] = None
    error_code: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextState:
    """Complete state of the context."""
    version: str = "1.0.0"
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Conversation state
    conversation: Dict[str, Any] = field(default_factory=dict)

    # Goals and constraints
    goals: Dict[str, Any] = field(default_factory=dict)

    # Artifacts
    artifacts: Dict[str, Any] = field(default_factory=dict)

    # Execution history
    execution: Dict[str, Any] = field(default_factory=dict)

    # Custom context data
    custom: Dict[str, Any] = field(default_factory=dict)


class SharedContext(ABC):
    """
    Abstract base class for the shared context model.

    The SharedContext provides:
    - Structured storage for all runtime state
    - Atomic read-modify-write operations
    - Scope-based visibility and TTL
    - Serialization for persistence
    """

    @property
    @abstractmethod
    def state(self) -> ContextState:
        """Get current context state (read-only view)."""
        ...

    @abstractmethod
    def initialize(self, session_id: Optional[str] = None) -> bool:
        """Initialize context for a session."""
        ...

    # ==================== Conversation State ====================

    @abstractmethod
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get complete conversation state."""
        ...

    @abstractmethod
    def set_conversation_state(self, state: Dict[str, Any]) -> bool:
        """Set conversation state (replaces existing)."""
        ...

    @abstractmethod
    def add_turn(self, turn: ConversationTurn) -> bool:
        """Add a conversation turn."""
        ...

    @abstractmethod
    def get_turn_count(self) -> int:
        """Get current turn count."""
        ...

    @abstractmethod
    def get_intent_history(self) -> List[Dict[str, Any]]:
        """Get history of detected intents."""
        ...

    @abstractmethod
    def record_intent(self, intent: str, confidence: float) -> bool:
        """Record a detected intent."""
        ...

    # ==================== Goals & Constraints ====================

    @abstractmethod
    def add_goal(self, goal: Goal) -> bool:
        """Add a new goal."""
        ...

    @abstractmethod
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get goal by ID."""
        ...

    @abstractmethod
    def get_active_goals(self) -> List[Goal]:
        """Get all active (pending/in_progress) goals."""
        ...

    @abstractmethod
    def update_goal(self, goal_id: str, updates: Dict[str, Any]) -> bool:
        """Update goal fields."""
        ...

    @abstractmethod
    def complete_goal(self, goal_id: str) -> bool:
        """Mark goal as completed."""
        ...

    @abstractmethod
    def fail_goal(self, goal_id: str, reason: str) -> bool:
        """Mark goal as failed."""
        ...

    @abstractmethod
    def add_goal_constraint(self, goal_id: str, constraint: Constraint) -> bool:
        """Add constraint to goal."""
        ...

    @abstractmethod
    def validate_goal_constraints(self, goal_id: str, input_value: Any) -> tuple[bool, List[str]]:
        """Validate input against goal constraints."""
        ...

    @abstractmethod
    def get_blocked_goals(self) -> List[Goal]:
        """Get goals blocked by unmet dependencies."""
        ...

    # ==================== Artifacts ====================

    @abstractmethod
    def store_artifact(self, artifact: Artifact) -> bool:
        """Store an artifact."""
        ...

    @abstractmethod
    def get_artifact(self, name: str, version: Optional[int] = None) -> Optional[Artifact]:
        """Get artifact by name (latest version if not specified)."""
        ...

    @abstractmethod
    def get_artifact_versions(self, name: str) -> List[int]:
        """Get all versions of an artifact."""
        ...

    @abstractmethod
    def update_artifact(self, name: str, data: Any) -> Artifact:
        """Update artifact with new version."""
        ...

    @abstractmethod
    def delete_artifact(self, name: str, version: Optional[int] = None) -> bool:
        """Delete artifact (specific version or all if not specified)."""
        ...

    @abstractmethod
    def find_artifacts_by_tag(self, tag: str) -> List[Artifact]:
        """Find all artifacts with a given tag."""
        ...

    @abstractmethod
    def get_all_artifacts(self) -> Dict[str, Artifact]:
        """Get all stored artifacts."""
        ...

    # ==================== Execution History ====================

    @abstractmethod
    def record_execution_step(self, step: ExecutionStep) -> bool:
        """Record an execution step."""
        ...

    @abstractmethod
    def get_execution_history(
        self,
        limit: Optional[int] = None,
        agent: Optional[str] = None,
        step_type: Optional[str] = None
    ) -> List[ExecutionStep]:
        """Get execution history with filters."""
        ...

    @abstractmethod
    def get_execution_step(self, step_id: str) -> Optional[ExecutionStep]:
        """Get specific execution step by ID."""
        ...

    @abstractmethod
    def get_recent_errors(self, limit: int = 10) -> List[ExecutionStep]:
        """Get recent failed steps."""
        ...

    @abstractmethod
    def clear_execution_history(self, before: Optional[datetime] = None) -> int:
        """Clear execution history (before timestamp or all)."""
        ...

    # ==================== Generic Access ====================

    @abstractmethod
    def get(self, key: str, scope: ContextScope = ContextScope.SESSION,
            default: Any = None) -> Any:
        """Get value from context by key."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, scope: ContextScope = ContextScope.SESSION) -> bool:
        """Set value in context by key."""
        ...

    @abstractmethod
    def delete(self, key: str, scope: ContextScope = ContextScope.SESSION) -> bool:
        """Delete value from context by key."""
        ...

    @abstractmethod
    def exists(self, key: str, scope: ContextScope = ContextScope.SESSION) -> bool:
        """Check if key exists in context."""
        ...

    @abstractmethod
    def get_all(self, scope: ContextScope = ContextScope.SESSION) -> Dict[str, Any]:
        """Get all values in a scope."""
        ...

    @abstractmethod
    def clear_scope(self, scope: ContextScope) -> int:
        """Clear all values in a scope."""
        ...

    # ==================== Serialization ====================

    @abstractmethod
    def serialize(self) -> str:
        """Serialize context to JSON string."""
        ...

    @abstractmethod
    def deserialize(self, data: str) -> bool:
        """Deserialize context from JSON string."""
        ...

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current state."""
        ...

    @abstractmethod
    def restore(self, snapshot: Dict[str, Any]) -> bool:
        """Restore state from snapshot."""
        ...

    # ==================== Access Control ====================

    @abstractmethod
    def check_access(self, key: str, access: ContextAccess,
                     agent_id: str) -> bool:
        """Check if agent has required access to key."""
        ...

    @abstractmethod
    def grant_access(self, key: str, agent_id: str,
                     access: ContextAccess) -> bool:
        """Grant access to an agent for a key."""
        ...

    @abstractmethod
    def revoke_access(self, key: str, agent_id: str,
                      access: ContextAccess) -> bool:
        """Revoke access from an agent for a key."""
        ...
```

---

## Read/Write Rules

### Read Rules

| Data Category | Who Can Read | Conditions |
|---------------|--------------|------------|
| **Conversation State** | All agents | None |
| **Goals (active)** | All agents | None |
| **Goals (completed)** | All agents | None |
| **Goals (assigned)** | Assigned agent | Owner match or ADMIN |
| **Artifacts (public)** | All agents | Tagged "public" |
| **Artifacts (private)** | Creator only | Creator match or ADMIN |
| **Execution History** | All agents | None |
| **Custom Context** | Owner only | Owner match or ADMIN |

### Write Rules

| Data Category | Who Can Write | Conditions |
|---------------|---------------|------------|
| **Conversation State** | All agents | None |
| **Goals (create)** | All agents | None |
| **Goals (update assigned)** | Assigned agent | Owner match |
| **Goals (update others)** | ADMIN only | - |
| **Artifacts (create)** | All agents | None |
| **Artifacts (update)** | Creator only | Owner match |
| **Execution History** | All agents | Append-only |
| **Custom Context** | Owner only | Owner match |

### Access Control Matrix

```
                    | Read | Write | Delete | Admin
-------------------|------|-------|--------|------
Conversation State |  ✓   |   ✓   |   -    |   -
Goals (active)     |  ✓   |   ✓   |   -    |   -
Goals (assigned)   |  ✓   |   ✓*  |   -    |   -
Goals (others)     |  ✓   |   -   |   -    |   ✓
Artifacts (public) |  ✓   |   -   |   -    |   -
Artifacts (own)    |  ✓   |   ✓   |   ✓    |   -
Artifacts (others) |  ✓   |   -   |   -    |   ✓
Execution History  |  ✓   |   ✓^  |   -    |   -
Custom (own)       |  ✓   |   ✓   |   ✓    |   -
Custom (others)    |  ✓   |   -   |   -    |   ✓

* Only assigned agent can update
^ Only append (new entries)
```

---

## Mutability Rules

### Immutable Data (After Commit)

- **Execution History**: Once recorded, entries cannot be modified or deleted
- **Artifact Versions**: Past versions are immutable; new versions created for updates
- **Goal History**: Status transitions are recorded; goal definition immutable after creation
- **Conversation Turns**: Individual turns are immutable once added

### Mutable Data

| Data | Mutable Fields | Mutability Rules |
|------|----------------|------------------|
| **Goal** | status, priority, assignee, constraints, metadata | Only by owner or ADMIN |
| **Artifact** | data (creates new version), tags, metadata | Creator or ADMIN |
| **Conversation State** | All fields | All agents, atomic replace |
| **Custom Context** | Value itself | Owner or ADMIN |

### Atomic Operations

```python
class AtomicOperation(ABC):
    """Base for atomic context operations."""

    @abstractmethod
    def execute(self, context: SharedContext) -> tuple[bool, Any]:
        """Execute atomically; returns (success, result)."""
        ...


@dataclass
class CompareAndSwap(AtomicOperation):
    """Compare-and-swap operation for atomic updates."""
    key: str
    expected_value: Any
    new_value: Any
    scope: ContextScope = ContextScope.SESSION

    def execute(self, context: SharedContext) -> tuple[bool, bool]:
        current = context.get(self.key, self.scope)
        if current == self.expected_value:
            return context.set(self.key, self.new_value, self.scope), True
        return False, False


@dataclass
class IncrementCounter(AtomicOperation):
    """Atomic increment operation."""
    key: str
    scope: ContextScope = ContextScope.SESSION
    delta: int = 1

    def execute(self, context: SharedContext) -> tuple[bool, int]:
        current = context.get(self.key, self.scope, 0)
        new_value = current + self.delta
        return context.set(self.key, new_value, self.scope), new_value
```

### Conflict Resolution

- **Last-Writer-Wins**: For non-critical data without conflict detection
- **Compare-And-Swap**: For critical updates requiring consistency
- **Merge Required**: For concurrent goal/artifact updates (manual intervention)

---

## Access Patterns for Agents

### Standard Access Pattern

```python
class AgentAccessPattern:
    """Recommended pattern for agent context access."""

    @staticmethod
    def read_context(agent_id: str, context: SharedContext, keys: List[str]) -> Dict[str, Any]:
        """Read multiple context values atomically."""
        results = {}
        for key in keys:
            if context.check_access(key, ContextAccess.READ, agent_id):
                results[key] = context.get(key)
            else:
                raise AccessDeniedError(f"Agent {agent_id} cannot read {key}")
        return results

    @staticmethod
    def write_result(agent_id: str, context: SharedContext,
                     artifact_name: str, data: Any) -> Artifact:
        """Write execution result as artifact."""
        artifact = Artifact(
            name=artifact_name,
            data=data,
            created_by=agent_id
        )
        context.store_artifact(artifact)
        return artifact

    @staticmethod
    def record_step(agent_id: str, context: SharedContext,
                    step_type: str, action: str,
                    input_summary: Dict[str, Any],
                    output_summary: Dict[str, Any],
                    status: str = "success") -> ExecutionStep:
        """Record execution step."""
        step = ExecutionStep(
            step_type=step_type,
            agent=agent_id,
            action=action,
            input_summary=input_summary,
            output_summary=output_summary,
            status=status,
            completed_at=datetime.utcnow()
        )
        context.record_execution_step(step)
        return step
```

### Goal-Oriented Pattern

```python
class GoalAccessPattern:
    """Access pattern for goal-oriented agents."""

    @staticmethod
    def claim_and_work_on_goal(agent_id: str, context: SharedContext,
                               goal_id: str) -> Optional[Goal]:
        """Claim a pending goal and mark as in_progress."""
        goal = context.get_goal(goal_id)
        if goal and goal.status == GoalStatus.PENDING:
            goal.assignee = agent_id
            goal.status = GoalStatus.IN_PROGRESS
            goal.updated_at = datetime.utcnow()
            context.update_goal(goal_id, {
                "status": GoalStatus.IN_PROGRESS,
                "assignee": agent_id
            })
            return goal
        return None

    @staticmethod
    def validate_before_action(agent_id: str, context: SharedContext,
                               goal_id: str, action_data: Any) -> tuple[bool, str]:
        """Validate action against goal constraints."""
        return context.validate_goal_constraints(goal_id, action_data)

    @staticmethod
    def complete_goal(agent_id: str, context: SharedContext,
                      goal_id: str, result: Any) -> bool:
        """Complete goal with result."""
        goal = context.get_goal(goal_id)
        if goal and goal.assignee == agent_id:
            # Store result as artifact
            artifact = Artifact(
                name=f"goal_{goal_id}_result",
                data=result,
                created_by=agent_id
            )
            context.store_artifact(artifact)
            # Mark goal complete
            return context.complete_goal(goal_id)
        return False
```

### Conversation Context Pattern

```python
class ConversationAccessPattern:
    """Access pattern for conversational agents."""

    @staticmethod
    def get_conversation_summary(context: SharedContext) -> Dict[str, Any]:
        """Get conversation summary for context."""
        state = context.get_conversation_state()
        turn_count = context.get_turn_count()
        intent_history = context.get_intent_history()
        return {
            "turn_count": turn_count,
            "intents": intent_history,
            "state": state
        }

    @staticmethod
    def extend_conversation(agent_id: str, context: SharedContext,
                            message: str, intent: Optional[str] = None) -> ConversationTurn:
        """Add agent response to conversation."""
        turn = ConversationTurn(
            role="agent",
            message=message,
            intent=intent,
            created_by=agent_id
        )
        context.add_turn(turn)
        if intent:
            context.record_intent(intent, 1.0)
        return turn
```

### Recommended Agent Workflow

```
1. Initialize
   └── context.initialize(session_id)

2. Read Context
   ├── context.get_conversation_state()
   ├── context.get_active_goals()
   └── context.get_all_artifacts()

3. Validate Constraints
   └── context.validate_goal_constraints(goal_id, plan)

4. Execute
   ├── Record step: context.record_execution_step(step)
   ├── Store artifacts: context.store_artifact(artifact)
   └── Update goals: context.update_goal(goal_id, updates)

5. Finalize
   └── context.snapshot() for persistence
```

---

## Serialization Format

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": { "type": "string" },
    "session_id": { "type": ["string", "null"] },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "conversation": {
      "type": "object",
      "properties": {
        "turns": {
          "type": "array",
          "items": { "$ref": "#/$defs/ConversationTurn" }
        },
        "state": { "type": "object" },
        "intent_history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "intent": { "type": "string" },
              "confidence": { "type": "number" },
              "timestamp": { "type": "string" }
            }
          }
        }
      }
    },
    "goals": {
      "type": "object",
      "properties": {
        "active": {
          "type": "array",
          "items": { "$ref": "#/$defs/Goal" }
        },
        "completed": {
          "type": "array",
          "items": { "$ref": "#/$defs/Goal" }
        }
      }
    },
    "artifacts": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": { "$ref": "#/$defs/Artifact" }
      }
    },
    "execution": {
      "type": "object",
      "properties": {
        "history": {
          "type": "array",
          "items": { "$ref": "#/$defs/ExecutionStep" }
        }
      }
    },
    "custom": { "type": "object" }
  },
  "$defs": {
    "ConversationTurn": {
      "type": "object",
      "properties": {
        "turn_id": { "type": "string" },
        "role": { "type": "string" },
        "message": { "type": "string" },
        "intent": { "type": ["string", "null"] },
        "entities": { "type": "object" },
        "timestamp": { "type": "string" }
      }
    },
    "Goal": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "title": { "type": "string" },
        "status": { "type": "string" },
        "priority": { "type": "integer" },
        "constraints": {
          "type": "array",
          "items": { "$ref": "#/$defs/Constraint" }
        }
      }
    },
    "Artifact": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "version": { "type": "integer" },
        "data": {},
        "created_by": { "type": ["string", "null"] }
      }
    },
    "ExecutionStep": {
      "type": "object",
      "properties": {
        "step_id": { "type": "string" },
        "step_type": { "type": "string" },
        "agent": { "type": ["string", "null"] },
        "action": { "type": "string" },
        "status": { "type": "string" }
      }
    },
    "Constraint": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "type": { "type": "string" },
        "value": {},
        "description": { "type": "string" }
      }
    }
  }
}
```

### Example Context State

```json
{
  "version": "1.0.0",
  "session_id": "session-abc123",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:30:00Z",
  "conversation": {
    "turns": [
      {
        "turn_id": "turn-001",
        "role": "user",
        "message": "Build a todo app",
        "intent": "create_todo_app",
        "timestamp": "2025-12-28T10:00:00Z"
      }
    ],
    "state": {
      "current_phase": "planning",
      "confirmed_requirements": ["add", "list", "delete"]
    },
    "intent_history": [
      {"intent": "create_todo_app", "confidence": 0.95, "timestamp": "2025-12-28T10:00:00Z"}
    ]
  },
  "goals": {
    "active": [
      {
        "id": "goal-001",
        "title": "Design todo app architecture",
        "status": "in_progress",
        "priority": 1,
        "assignee": "ArchitectAgent",
        "constraints": [
          {"type": "max_time", "value": 300000, "description": "Complete within 5 minutes"}
        ]
      }
    ],
    "completed": []
  },
  "artifacts": {
    "spec": [
      {
        "id": "art-001",
        "name": "spec",
        "version": 1,
        "data": {"features": ["add", "list", "delete"]},
        "created_by": "SpecBuilder",
        "tags": ["public"]
      }
    ]
  },
  "execution": {
    "history": [
      {
        "step_id": "step-001",
        "step_type": "reasoning",
        "agent": "IntentParser",
        "action": "parse_intent",
        "status": "success"
      }
    ]
  }
}
```

---

## Summary

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **ContextState** | Root data container | conversation, goals, artifacts, execution |
| **Goal** | Goal tracking | add_constraint, update_status |
| **Constraint** | Constraint enforcement | validate |
| **Artifact** | Artifact versioning | new_version |
| **ExecutionStep** | History recording | record_execution_step |
| **SharedContext** | Main interface | get, set, serialize, snapshot |

**PHR**: `history/prompts/shared-context-model/001-define-shared-context-model.spec.prompt.md`
