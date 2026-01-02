"""
Context and Memory System for the Intelligence Framework.

This module provides the core data structures for managing execution state,
history, and memory across the intelligence system. It follows the spec
defined in specs/001-context-memory-system/spec.md.

Key Components:
- HistoryEvent: Immutable record of a single execution event
- ExecutionContext: Container for all execution state, goals, and history
- State snapshots for rollback support
- JSON serialization for persistence
"""
from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# =============================================================================
# Exceptions
# =============================================================================

class ContextError(Exception):
    """Base exception for context-related errors."""
    pass


class SerializationError(ContextError):
    """Raised when context serialization fails."""
    pass


class PersistenceError(ContextError):
    """Raised when context persistence (save/load) fails."""
    pass


class InvalidRollbackStateError(ContextError):
    """Raised when attempting to rollback to an invalid state."""
    pass


class ImmutabilityError(ContextError):
    """Raised when attempting to modify immutable fields."""
    pass


# =============================================================================
# Data Structures
# =============================================================================

@dataclass(frozen=True)
class HistoryEvent:
    """
    A single, immutable event in the execution history.

    Attributes:
        event_id: Unique identifier for this event
        timestamp: ISO 8601 timestamp of when the event occurred
        type: Event type (e.g., 'skill_start', 'skill_success', 'state_change')
        details: Event-specific payload data
    """
    event_id: str
    timestamp: str
    type: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "type": self.type,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HistoryEvent:
        """Create HistoryEvent from dictionary."""
        return cls(
            event_id=data["event_id"],
            timestamp=data["timestamp"],
            type=data["type"],
            details=data.get("details", {}),
        )


@dataclass
class StateSnapshot:
    """
    A snapshot of the execution state at a specific point in time.
    Used for rollback functionality.
    """
    event_id: str
    state: Dict[str, Any]
    status: str


class ExecutionContext:
    """
    Container for all information related to a single, end-to-end execution.

    This object tracks state, goals, and history, and supports inspection
    and rollback. It is the central nervous system of any execution.

    Attributes:
        execution_id: Unique identifier for this execution (immutable)
        status: Current status (pending, in_progress, success, failed, rolled_back)
        goal: Original, immutable goal and structured intent
        state: Mutable working memory for skill outputs and intermediate data
        history: Append-only log of all events

    Thread Safety:
        This context is designed for single-threaded access within a given
        execution. Concurrent modification is undefined behavior.
    """

    # Valid status transitions
    VALID_STATUSES = {"pending", "in_progress", "success", "failed", "rolled_back"}

    def __init__(
        self,
        execution_id: str,
        status: str = "pending",
        goal: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None,
        history: Optional[List[HistoryEvent]] = None,
    ) -> None:
        """
        Initialize an ExecutionContext.

        Args:
            execution_id: Unique identifier for this execution
            status: Initial status (default: "pending")
            goal: The original goal/intent (immutable after creation)
            state: Initial state dictionary
            history: Initial history events
        """
        # Immutable fields (set via object's __dict__ to bypass property setter)
        object.__setattr__(self, "_execution_id", execution_id)
        object.__setattr__(self, "_goal", goal if goal is not None else {})
        object.__setattr__(self, "_goal_frozen", False)

        # Mutable fields
        self._status = status
        self._state: Dict[str, Any] = state if state is not None else {}
        self._history: List[HistoryEvent] = history if history is not None else []
        self._snapshots: Dict[str, StateSnapshot] = {}

        # Take initial snapshot
        self._take_snapshot("initial")

    # -------------------------------------------------------------------------
    # Immutable Properties
    # -------------------------------------------------------------------------

    @property
    def execution_id(self) -> str:
        """Unique identifier for this execution (immutable)."""
        return self._execution_id

    @property
    def goal(self) -> Dict[str, Any]:
        """Original goal/intent (immutable after first access in execution)."""
        object.__setattr__(self, "_goal_frozen", True)
        return self._goal

    # -------------------------------------------------------------------------
    # Mutable Properties
    # -------------------------------------------------------------------------

    @property
    def status(self) -> str:
        """Current execution status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Set execution status with validation."""
        if value not in self.VALID_STATUSES:
            raise ContextError(f"Invalid status: {value}. Must be one of {self.VALID_STATUSES}")
        self._status = value

    @property
    def state(self) -> Dict[str, Any]:
        """Mutable working memory for the execution."""
        return self._state

    @property
    def history(self) -> List[HistoryEvent]:
        """Append-only history log (returns copy to prevent external modification)."""
        return list(self._history)

    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from state.

        Args:
            key: State key to retrieve
            default: Default value if key not found

        Returns:
            The value or default
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in state.

        Args:
            key: State key to set
            value: Value to store (must be JSON-serializable)
        """
        self._state[key] = value

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple state values at once.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        self._state.update(updates)

    # -------------------------------------------------------------------------
    # History Management
    # -------------------------------------------------------------------------

    def append_event(self, event_type: str, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Append a new event to the execution history.

        This is the only way to add events - the history is append-only.

        Args:
            event_type: Type of event (e.g., 'skill_start', 'state_change')
            details: Event-specific information

        Returns:
            The generated event_id
        """
        event_id = f"evt_{len(self._history) + 1:04d}"
        event = HistoryEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            type=event_type,
            details=details if details is not None else {},
        )
        self._history.append(event)

        # Take snapshot after state-changing events
        if event_type in ("skill_success", "state_change", "action_success"):
            self._take_snapshot(event_id)

        return event_id

    # Alias for backwards compatibility
    def add_event(self, event_type: str, details: Optional[Dict[str, Any]] = None) -> str:
        """Alias for append_event (backwards compatibility)."""
        return self.append_event(event_type, details)

    # -------------------------------------------------------------------------
    # Snapshot & Rollback
    # -------------------------------------------------------------------------

    def _take_snapshot(self, event_id: str) -> None:
        """Take a deep copy snapshot of current state."""
        self._snapshots[event_id] = StateSnapshot(
            event_id=event_id,
            state=copy.deepcopy(self._state),
            status=self._status,
        )

    def rollback_to_event(self, event_id: str) -> None:
        """
        Roll back the context's state to after a specific event.

        This restores the state snapshot taken after the target event
        and marks the context as rolled back.

        Args:
            event_id: The event ID to roll back to

        Raises:
            InvalidRollbackStateError: If event_id is not found or has no snapshot
        """
        self.append_event("rollback_attempt", {"target_event_id": event_id})

        # Find the event to verify it exists
        event_exists = any(e.event_id == event_id for e in self._history)
        if not event_exists and event_id != "initial":
            self.append_event("rollback_failure", {"error": f"Event ID '{event_id}' not found"})
            raise InvalidRollbackStateError(f"Event ID '{event_id}' not found in history.")

        # Check for snapshot
        if event_id not in self._snapshots:
            self.append_event("rollback_failure", {"error": f"No snapshot for event '{event_id}'"})
            raise InvalidRollbackStateError(
                f"No state snapshot available for event '{event_id}'. "
                "Snapshots are only taken after state-changing events."
            )

        # Restore state from snapshot
        snapshot = self._snapshots[event_id]
        self._state = copy.deepcopy(snapshot.state)
        self._status = "rolled_back"

        self.append_event("rollback_success", {
            "restored_to_event": event_id,
            "restored_state_keys": list(self._state.keys()),
        })

    # Alias for backwards compatibility
    def rollback(self, event_id: str) -> None:
        """Alias for rollback_to_event (backwards compatibility)."""
        return self.rollback_to_event(event_id)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary for serialization.

        Returns:
            Dictionary representation of the context
        """
        return {
            "execution_id": self._execution_id,
            "status": self._status,
            "goal": self._goal,
            "state": self._state,
            "history": [e.to_dict() for e in self._history],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutionContext:
        """
        Create an ExecutionContext from a dictionary.

        Args:
            data: Dictionary containing context data

        Returns:
            New ExecutionContext instance
        """
        history = [HistoryEvent.from_dict(e) for e in data.get("history", [])]
        return cls(
            execution_id=data["execution_id"],
            status=data.get("status", "pending"),
            goal=data.get("goal", {}),
            state=data.get("state", {}),
            history=history,
        )

    def save(self, file_path: str) -> None:
        """
        Serialize and persist the context to a JSON file.

        Args:
            file_path: Path to save the context

        Raises:
            SerializationError: If the context cannot be serialized
            PersistenceError: If the file cannot be written
        """
        self.append_event("context_save_start", {"path": file_path})

        try:
            data = self.to_dict()
            # Validate serializability
            json_str = json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError) as e:
            self.append_event("context_save_failure", {"error": str(e)})
            raise SerializationError(f"Failed to serialize context: {e}") from e

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            self.append_event("context_save_success", {"path": file_path})
        except OSError as e:
            self.append_event("context_save_failure", {"error": str(e)})
            raise PersistenceError(f"Failed to write to file: {e}") from e

    @classmethod
    def load(cls, file_path: str) -> ExecutionContext:
        """
        Load and deserialize a context from a JSON file.

        Args:
            file_path: Path to load the context from

        Returns:
            Loaded ExecutionContext instance

        Raises:
            PersistenceError: If the file cannot be read or parsed
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise PersistenceError(f"Failed to load context file: {e}") from e

        context = cls.from_dict(data)
        context.append_event("context_load_success", {"path": file_path})
        return context

    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        goal: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None,
    ) -> ExecutionContext:
        """
        Factory method to create a new ExecutionContext with auto-generated ID.

        Args:
            goal: The goal/intent for this execution
            execution_id: Optional custom ID (auto-generated if not provided)

        Returns:
            New ExecutionContext instance
        """
        if execution_id is None:
            execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        return cls(
            execution_id=execution_id,
            goal=goal if goal is not None else {},
        )

    # -------------------------------------------------------------------------
    # Introspection
    # -------------------------------------------------------------------------

    def get_history_by_type(self, event_type: str) -> List[HistoryEvent]:
        """Get all history events of a specific type."""
        return [e for e in self._history if e.type == event_type]

    def get_last_event(self) -> Optional[HistoryEvent]:
        """Get the most recent history event."""
        return self._history[-1] if self._history else None

    def __repr__(self) -> str:
        return (
            f"ExecutionContext(id={self._execution_id!r}, "
            f"status={self._status!r}, "
            f"events={len(self._history)})"
        )
