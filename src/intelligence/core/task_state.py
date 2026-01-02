"""
Task State Enumeration for the Intelligence Framework.

This module defines the TaskState enum representing the 12 possible states
of an execution throughout its lifecycle, from PENDING to REFINING.

TaskState differs from TaskStage:
- TaskStage: Represents the current processing stage in the pipeline
- TaskState: Represents the overall status of the execution

An execution has one TaskState but progresses through multiple TaskStages.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.intelligence.core.task_stage import TaskStage


class TaskState(Enum):
    """
    Represents the overall state/status of an execution.

    The state captures the high-level status of an execution, indicating
    whether it's waiting to start, in progress, completed successfully,
    failed, or needs refinement.

    States:
        PENDING: Created but not yet started
        INTERPRETED: Intent has been parsed
        TRANSFORMED: Meaning has been structured
        PLANNED: Action plan has been created
        VALIDATED: Plan has been validated
        APPROVED: Plan has been approved
        EXECUTING: Skills are being dispatched
        EVALUATING: Outcome is being assessed
        COMPLETED: Successfully completed
        FAILED: Terminal failure
        CANCELLED: User or system cancelled
        REFINING: Iterating for improvement

    Example:
        >>> state = TaskState.PENDING
        >>> state.value
        'pending'
    """

    #: Initial state - execution created but not started
    #: Context created, waiting to begin processing
    PENDING = auto()

    #: Intent has been parsed from raw input
    #: INTERPRET stage completed successfully
    INTERPRETED = auto()

    #: Intent has been transformed to structured meaning
    #: TRANSFORM stage completed successfully
    TRANSFORMED = auto()

    #: Action plan has been generated
    #: PLAN stage completed successfully
    PLANNED = auto()

    #: Plan has been validated
    #: VALIDATE stage completed successfully
    VALIDATED = auto()

    #: Plan has been approved for execution
    #: APPROVE stage completed successfully
    APPROVED = auto()

    #: Skills are currently being dispatched and executed
    #: EXECUTING stage is in progress
    EXECUTING = auto()

    #: Outcome is being assessed against intent
    #: EVALUATING stage is in progress
    EVALUATING = auto()

    #: Execution completed successfully
    #: Terminal state - all stages completed
    COMPLETED = auto()

    #: Execution failed with an error
    #: Terminal state - unrecoverable failure
    FAILED = auto()

    #: Execution was cancelled (user or system request)
    #: Terminal state - graceful termination
    CANCELLED = auto()

    #: Execution is being refined for improvement
    #: Non-terminal - may return to earlier stages
    REFINING = auto()

    @classmethod
    def from_string(cls, state_name: str) -> "TaskState":
        """
        Create a TaskState from a string value.

        Args:
            state_name: String representation of the state (case-insensitive)

        Returns:
            Corresponding TaskState enum value

        Raises:
            ValueError: If state_name is not a valid TaskState

        Example:
            >>> TaskState.from_string("pending")
            <TaskState.PENDING>
            >>> TaskState.from_string("COMPLETED")
            <TaskState.COMPLETED>
        """
        normalized = state_name.strip().upper()
        for member in cls:
            if member.name == normalized:
                return member
        raise ValueError(f"Invalid state name: {state_name}")

    def is_terminal(self) -> bool:
        """
        Check if this is a terminal state.

        Terminal states are COMPLETED, FAILED, and CANCELLED.
        Once in a terminal state, the execution cannot transition
        to any other state.

        Returns:
            True if this is a terminal state, False otherwise

        Example:
            >>> TaskState.COMPLETED.is_terminal()
            True
            >>> TaskState.EXECUTING.is_terminal()
            False
        """
        return self in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED)

    def is_active(self) -> bool:
        """
        Check if this is an active (non-terminal) state.

        Active states are those where the execution is still in progress
        and may transition to other states.

        Returns:
            True if this is an active state, False if terminal

        Example:
            >>> TaskState.EXECUTING.is_active()
            True
            >>> TaskState.COMPLETED.is_active()
            False
        """
        return not self.is_terminal()

    def can_transition_to(self, next_state: "TaskState") -> bool:
        """
        Check if transition to another state is valid.

        Defines valid state transitions for the execution lifecycle.
        Most states follow a linear progression, with REFINING being
        able to loop back to earlier states.

        Args:
            next_state: The state to transition to

        Returns:
            True if the transition is valid, False otherwise

        Example:
            >>> TaskState.PENDING.can_transition_to(TaskState.INTERPRETED)
            True
            >>> TaskState.COMPLETED.can_transition_to(TaskState.EXECUTING)
            False
        """
        # Terminal states cannot transition to any state
        if self.is_terminal():
            return False

        # Define valid transitions from each non-terminal state
        valid_transitions: dict[TaskState, list[TaskState]] = {
            TaskState.PENDING: [TaskState.INTERPRETED],
            TaskState.INTERPRETED: [TaskState.TRANSFORMED],
            TaskState.TRANSFORMED: [TaskState.PLANNED],
            TaskState.PLANNED: [TaskState.VALIDATED],
            TaskState.VALIDATED: [TaskState.APPROVED],
            TaskState.APPROVED: [TaskState.EXECUTING],
            TaskState.EXECUTING: [TaskState.EVALUATING],
            TaskState.EVALUATING: [TaskState.REFINING, TaskState.COMPLETED, TaskState.FAILED],
            TaskState.REFINING: [TaskState.PLANNED, TaskState.COMPLETED, TaskState.FAILED],
        }
        return next_state in valid_transitions.get(self, [])

    def get_description(self) -> str:
        """
        Get a human-readable description of this state.

        Returns:
            Description of what this state means

        Example:
            >>> TaskState.PENDING.get_description()
            'Execution created but not yet started'
        """
        descriptions: dict[TaskState, str] = {
            TaskState.PENDING: "Execution created but not yet started",
            TaskState.INTERPRETED: "Intent has been parsed from raw input",
            TaskState.TRANSFORMED: "Intent transformed to structured meaning",
            TaskState.PLANNED: "Action plan has been generated",
            TaskState.VALIDATED: "Plan has been validated",
            TaskState.APPROVED: "Plan has been approved for execution",
            TaskState.EXECUTING: "Skills are being dispatched and executed",
            TaskState.EVALUATING: "Outcome is being assessed",
            TaskState.COMPLETED: "Execution completed successfully",
            TaskState.FAILED: "Execution failed with an error",
            TaskState.CANCELLED: "Execution was cancelled",
            TaskState.REFINING: "Execution is being refined for improvement",
        }
        return descriptions.get(self, "Unknown state")

    def get_stage_mapping(self) -> "TaskStage":
        """
        Get the typical TaskStage associated with this state.

        Note: This is a typical mapping; an execution may have
        different stage/state combinations depending on its progress.

        Returns:
            Associated TaskStage

        Example:
            >>> TaskState.EXECUTING.get_stage_mapping()
            <TaskStage.EXECUTING>
        """
        # Runtime import to avoid circular dependency
        from src.intelligence.core.task_stage import TaskStage

        stage_mapping: dict[TaskState, TaskStage] = {
            TaskState.PENDING: TaskStage.INPUT,
            TaskState.INTERPRETED: TaskStage.INTERPRET,
            TaskState.TRANSFORMED: TaskStage.TRANSFORM,
            TaskState.PLANNED: TaskStage.PLAN,
            TaskState.VALIDATED: TaskStage.VALIDATE,
            TaskState.APPROVED: TaskStage.APPROVE,
            TaskState.EXECUTING: TaskStage.EXECUTING,
            TaskState.EVALUATING: TaskStage.EVALUATING,
            TaskState.COMPLETED: TaskStage.TERMINATE,
            TaskState.FAILED: TaskStage.TERMINATE,
            TaskState.CANCELLED: TaskStage.TERMINATE,
            TaskState.REFINING: TaskStage.REFINING,
        }
        return stage_mapping.get(self, TaskStage.INPUT)

    def get_category(self) -> str:
        """
        Get the category of this state.

        Categories group related states for reporting and analysis.

        Returns:
            Category name: "pending", "processing", "terminal", "refinement"

        Example:
            >>> TaskState.EXECUTING.get_category()
            'processing'
        """
        categories: dict[TaskState, str] = {
            TaskState.PENDING: "pending",
            TaskState.INTERPRETED: "processing",
            TaskState.TRANSFORMED: "processing",
            TaskState.PLANNED: "processing",
            TaskState.VALIDATED: "processing",
            TaskState.APPROVED: "processing",
            TaskState.EXECUTING: "processing",
            TaskState.EVALUATING: "processing",
            TaskState.COMPLETED: "terminal",
            TaskState.FAILED: "terminal",
            TaskState.CANCELLED: "terminal",
            TaskState.REFINING: "refinement",
        }
        return categories.get(self, "unknown")
