"""
Task Stage Enumeration for the Intelligence Framework.

This module defines the TaskStage enum representing the 10 stages of the
intelligence task lifecycle, from INPUT to TERMINATE.

Each stage represents a distinct phase in the reasoning-to-execution pipeline,
where the system interprets user intent, transforms it into structured meaning,
plans actions, validates and approves the plan, executes skills, evaluates results,
and optionally refines before termination.
"""

from enum import Enum, auto
from typing import Any


class TaskStage(Enum):
    """
    Represents the current stage of a reasoning task in the intelligence pipeline.

    The intelligence framework processes tasks through a defined lifecycle.
    Each stage represents a distinct phase with specific responsibilities
    and outputs that feed into subsequent stages.

    Stages:
        INPUT: Initial receipt of user input
        INTERPRET: Parse user intent from raw input
        TRANSFORM: Convert intent to structured meaning
        PLAN: Generate actionable sequence from goal
        VALIDATE: Verify plan soundness before execution
        APPROVE: Authorize plan execution
        EXECUTING: Skills are being dispatched
        EVALUATING: Outcome is being assessed against intent
        REFINING: Iterating on output (conditional)
        TERMINATE: Task completed (any state)

    Example:
        >>> stage = TaskStage.INTERPRET
        >>> stage.value
        'interpret'
        >>> stage.name
        'INTERPRET'
    """

    #: Initial stage - raw user input has been received
    #: Outputs: RawInput with metadata (timestamp, trace ID)
    INPUT = auto()

    #: Parse user intent from raw input using pattern matching
    #: Outputs: ParsedIntent with confidence score
    INTERPRET = auto()

    #: Convert parsed intent to structured semantic representation
    #: Outputs: StructuredMeaning (domain-agnostic)
    TRANSFORM = auto()

    #: Generate actionable sequence from goal through decomposition
    #: Outputs: ActionPlan with skill invocations
    PLAN = auto()

    #: Verify plan soundness (skill availability, constraints, dependencies)
    #: Outputs: ValidationResult (pass/fail with reasons)
    VALIDATE = auto()

    #: Authorize plan execution (human-in-loop or automated)
    #: Outputs: ApprovedPlan
    APPROVE = auto()

    #: Skills are being dispatched and executed
    #: Outputs: ExecutionResult with intermediate traces
    EXECUTING = auto()

    #: Outcome is being assessed against original intent
    #: Outputs: EvaluationReport with quality metrics
    EVALUATING = auto()

    #: Conditional stage - improve outcome if evaluation fails thresholds
    #: Outputs: Refined plan or escalation
    REFINING = auto()

    #: Terminal stage - task completed (success, failure, or cancellation)
    #: Outputs: TaskCompletion with final state
    TERMINATE = auto()

    @classmethod
    def from_string(cls, stage_name: str) -> "TaskStage":
        """
        Create a TaskStage from a string value.

        Args:
            stage_name: String representation of the stage (case-insensitive)

        Returns:
            Corresponding TaskStage enum value

        Raises:
            ValueError: If stage_name is not a valid TaskStage

        Example:
            >>> TaskStage.from_string("interpret")
            <TaskStage.INTERPRET>
            >>> TaskStage.from_string("PLAN")
            <TaskStage.PLAN>
        """
        normalized = stage_name.strip().upper()
        for member in cls:
            if member.name == normalized:
                return member
        raise ValueError(f"Invalid stage name: {stage_name}")

    def is_terminal(self) -> bool:
        """
        Check if this stage is a terminal stage.

        Terminal stages are those that represent the end of a task's lifecycle:
        TERMINATE is the only truly terminal stage, but REFINING can lead
        back to earlier stages.

        Returns:
            True if this is a terminal stage, False otherwise

        Example:
            >>> TaskStage.TERMINATE.is_terminal()
            True
            >>> TaskStage.EXECUTING.is_terminal()
            False
        """
        return self == TaskStage.TERMINATE

    def can_transition_to(self, next_stage: "TaskStage") -> bool:
        """
        Check if transition to another stage is valid.

        Defines the valid progression through the intelligence pipeline.
        Most stages follow a linear progression, with REFINING being
        conditional and able to loop back to earlier stages.

        Args:
            next_stage: The stage to transition to

        Returns:
            True if the transition is valid, False otherwise

        Example:
            >>> TaskStage.INPUT.can_transition_to(TaskStage.INTERPRET)
            True
            >>> TaskStage.INPUT.can_transition_to(TaskStage.EXECUTING)
            False
            >>> TaskStage.EVALUATING.can_transition_to(TaskStage.REFINING)
            True
        """
        valid_transitions: dict[TaskStage, list[TaskStage]] = {
            TaskStage.INPUT: [TaskStage.INTERPRET],
            TaskStage.INTERPRET: [TaskStage.TRANSFORM],
            TaskStage.TRANSFORM: [TaskStage.PLAN],
            TaskStage.PLAN: [TaskStage.VALIDATE],
            TaskStage.VALIDATE: [TaskStage.APPROVE],
            TaskStage.APPROVE: [TaskStage.EXECUTING],
            TaskStage.EXECUTING: [TaskStage.EVALUATING],
            TaskStage.EVALUATING: [TaskStage.REFINING, TaskStage.TERMINATE],
            TaskStage.REFINING: [TaskStage.PLAN, TaskStage.TERMINATE],
            TaskStage.TERMINATE: [],  # Terminal - no transitions
        }
        return next_stage in valid_transitions.get(self, [])

    def get_description(self) -> str:
        """
        Get a human-readable description of this stage.

        Returns:
            Description of what happens in this stage

        Example:
            >>> TaskStage.INTERPRET.get_description()
            'Parse user intent from raw input'
        """
        descriptions: dict[TaskStage, str] = {
            TaskStage.INPUT: "Receive raw user input",
            TaskStage.INTERPRET: "Parse user intent from raw input",
            TaskStage.TRANSFORM: "Convert intent to structured meaning",
            TaskStage.PLAN: "Generate actionable sequence from goal",
            TaskStage.VALIDATE: "Verify plan soundness before execution",
            TaskStage.APPROVE: "Authorize plan execution",
            TaskStage.EXECUTING: "Dispatch and execute skills",
            TaskStage.EVALUATING: "Assess outcome against intent",
            TaskStage.REFINING: "Improve outcome through iteration",
            TaskStage.TERMINATE: "Task completed",
        }
        return descriptions.get(self, "Unknown stage")

    def get_output_type(self) -> str:
        """
        Get the type of output produced in this stage.

        Returns:
            String name of the output type

        Example:
            >>> TaskStage.INTERPRET.get_output_type()
            'ParsedIntent'
        """
        output_types: dict[TaskStage, str] = {
            TaskStage.INPUT: "RawInput",
            TaskStage.INTERPRET: "ParsedIntent",
            TaskStage.TRANSFORM: "StructuredMeaning",
            TaskStage.PLAN: "ActionPlan",
            TaskStage.VALIDATE: "ValidationResult",
            TaskStage.APPROVE: "ApprovedPlan",
            TaskStage.EXECUTING: "ExecutionResult",
            TaskStage.EVALUATING: "EvaluationReport",
            TaskStage.REFINING: "RefinedPlan",
            TaskStage.TERMINATE: "TaskCompletion",
        }
        return output_types.get(self, "Unknown")
