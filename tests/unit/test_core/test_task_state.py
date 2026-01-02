"""
Tests for the TaskState enum.

This module contains unit tests for the TaskState enumeration,
verifying state values, transitions, categories, and helper methods.
"""

import pytest

from src.intelligence.core.task_state import TaskState


class TestTaskStateValues:
    """Tests for TaskState enum values."""

    def test_all_states_defined(self) -> None:
        """Verify all 12 states are defined."""
        expected_states = [
            "PENDING",
            "INTERPRETED",
            "TRANSFORMED",
            "PLANNED",
            "VALIDATED",
            "APPROVED",
            "EXECUTING",
            "EVALUATING",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
            "REFINING",
        ]
        actual_states = [state.name for state in TaskState]
        assert set(expected_states) == set(actual_states)

    def test_state_count(self) -> None:
        """Verify exactly 12 states are defined."""
        assert len(TaskState) == 12

    def test_state_values_are_auto_incremented(self) -> None:
        """Verify state values are 1-12."""
        values = [state.value for state in TaskState]
        assert values == list(range(1, 13))


class TestTaskStateFromString:
    """Tests for TaskState.from_string() method."""

    def test_valid_state_name_lowercase(self) -> None:
        """Test creating state from lowercase string."""
        state = TaskState.from_string("pending")
        assert state == TaskState.PENDING

    def test_valid_state_name_uppercase(self) -> None:
        """Test creating state from uppercase string."""
        state = TaskState.from_string("PENDING")
        assert state == TaskState.PENDING

    def test_valid_state_name_mixed_case(self) -> None:
        """Test creating state from mixed case string."""
        state = TaskState.from_string("PeNdInG")
        assert state == TaskState.PENDING

    def test_valid_state_with_whitespace(self) -> None:
        """Test creating state with surrounding whitespace."""
        state = TaskState.from_string("  pending  ")
        assert state == TaskState.PENDING

    def test_invalid_state_name_raises_value_error(self) -> None:
        """Test that invalid state name raises ValueError."""
        with pytest.raises(ValueError):
            TaskState.from_string("invalid_state")

    def test_empty_string_raises_value_error(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            TaskState.from_string("")


class TestTaskStateIsTerminal:
    """Tests for TaskState.is_terminal() method."""

    def test_completed_is_terminal(self) -> None:
        """Test that COMPLETED is a terminal state."""
        assert TaskState.COMPLETED.is_terminal() is True

    def test_failed_is_terminal(self) -> None:
        """Test that FAILED is a terminal state."""
        assert TaskState.FAILED.is_terminal() is True

    def test_cancelled_is_terminal(self) -> None:
        """Test that CANCELLED is a terminal state."""
        assert TaskState.CANCELLED.is_terminal() is True

    def test_other_states_are_not_terminal(self) -> None:
        """Test that non-terminal states return False."""
        non_terminal = [
            TaskState.PENDING,
            TaskState.INTERPRETED,
            TaskState.TRANSFORMED,
            TaskState.PLANNED,
            TaskState.VALIDATED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.EVALUATING,
            TaskState.REFINING,
        ]
        for state in non_terminal:
            assert state.is_terminal() is False


class TestTaskStateIsActive:
    """Tests for TaskState.is_active() method."""

    def test_active_states_return_true(self) -> None:
        """Test that non-terminal states are active."""
        active_states = [
            TaskState.PENDING,
            TaskState.INTERPRETED,
            TaskState.TRANSFORMED,
            TaskState.PLANNED,
            TaskState.VALIDATED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.EVALUATING,
            TaskState.REFINING,
        ]
        for state in active_states:
            assert state.is_active() is True

    def test_terminal_states_return_false(self) -> None:
        """Test that terminal states are not active."""
        terminal_states = [
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        ]
        for state in terminal_states:
            assert state.is_active() is False


class TestTaskStateCanTransitionTo:
    """Tests for TaskState.can_transition_to() method."""

    def test_pending_to_interpreted(self) -> None:
        """Test valid transition from PENDING to INTERPRETED."""
        assert TaskState.PENDING.can_transition_to(TaskState.INTERPRETED) is True

    def test_pending_to_other_fails(self) -> None:
        """Test that PENDING cannot transition directly to other states."""
        invalid_targets = [
            TaskState.TRANSFORMED,
            TaskState.EXECUTING,
            TaskState.COMPLETED,
        ]
        for target in invalid_targets:
            assert TaskState.PENDING.can_transition_to(target) is False

    def test_linear_progression_valid(self) -> None:
        """Test that linear progression through states is valid."""
        states = [
            TaskState.PENDING,
            TaskState.INTERPRETED,
            TaskState.TRANSFORMED,
            TaskState.PLANNED,
            TaskState.VALIDATED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.EVALUATING,
        ]
        for i in range(len(states) - 1):
            assert states[i].can_transition_to(states[i + 1]) is True

    def test_evaluating_to_completed(self) -> None:
        """Test that EVALUATING can transition to COMPLETED."""
        assert TaskState.EVALUATING.can_transition_to(TaskState.COMPLETED) is True

    def test_evaluating_to_failed(self) -> None:
        """Test that EVALUATING can transition to FAILED."""
        assert TaskState.EVALUATING.can_transition_to(TaskState.FAILED) is True

    def test_evaluating_to_refining(self) -> None:
        """Test that EVALUATING can transition to REFINING."""
        assert TaskState.EVALUATING.can_transition_to(TaskState.REFINING) is True

    def test_refining_to_planned(self) -> None:
        """Test that REFINING can transition back to PLANNED."""
        assert TaskState.REFINING.can_transition_to(TaskState.PLANNED) is True

    def test_refining_to_completed(self) -> None:
        """Test that REFINING can transition to COMPLETED."""
        assert TaskState.REFINING.can_transition_to(TaskState.COMPLETED) is True

    def test_refining_to_failed(self) -> None:
        """Test that REFINING can transition to FAILED."""
        assert TaskState.REFINING.can_transition_to(TaskState.FAILED) is True

    def test_completed_cannot_transition(self) -> None:
        """Test that COMPLETED cannot transition to any state."""
        for target in TaskState:
            assert TaskState.COMPLETED.can_transition_to(target) is False

    def test_failed_cannot_transition(self) -> None:
        """Test that FAILED cannot transition to any state."""
        for target in TaskState:
            assert TaskState.FAILED.can_transition_to(target) is False

    def test_cancelled_cannot_transition(self) -> None:
        """Test that CANCELLED cannot transition to any state."""
        for target in TaskState:
            assert TaskState.CANCELLED.can_transition_to(target) is False


class TestTaskStateGetDescription:
    """Tests for TaskState.get_description() method."""

    def test_each_state_has_description(self) -> None:
        """Test that every state has a non-empty description."""
        for state in TaskState:
            description = state.get_description()
            assert isinstance(description, str)
            assert len(description) > 0

    def test_descriptions_are_meaningful(self) -> None:
        """Test that descriptions are meaningful and descriptive."""
        expected = {
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
        for state, desc in expected.items():
            assert state.get_description() == desc


class TestTaskStateGetStageMapping:
    """Tests for TaskState.get_stage_mapping() method."""

    def test_each_state_has_stage_mapping(self) -> None:
        """Test that every state has a stage mapping."""
        from src.intelligence.core.task_stage import TaskStage

        for state in TaskState:
            stage = state.get_stage_mapping()
            assert isinstance(stage, TaskStage)

    def test_stage_mappings_match_lifecycle(self) -> None:
        """Test that stage mappings follow the lifecycle."""
        from src.intelligence.core.task_stage import TaskStage

        mappings = {
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
        for state, expected_stage in mappings.items():
            assert state.get_stage_mapping() == expected_stage


class TestTaskStateGetCategory:
    """Tests for TaskState.get_category() method."""

    def test_pending_category(self) -> None:
        """Test PENDING category is 'pending'."""
        assert TaskState.PENDING.get_category() == "pending"

    def test_processing_category(self) -> None:
        """Test processing states have 'processing' category."""
        processing_states = [
            TaskState.INTERPRETED,
            TaskState.TRANSFORMED,
            TaskState.PLANNED,
            TaskState.VALIDATED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.EVALUATING,
        ]
        for state in processing_states:
            assert state.get_category() == "processing"

    def test_terminal_category(self) -> None:
        """Test terminal states have 'terminal' category."""
        terminal_states = [
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
        ]
        for state in terminal_states:
            assert state.get_category() == "terminal"

    def test_refining_category(self) -> None:
        """Test REFINING category is 'refinement'."""
        assert TaskState.REFINING.get_category() == "refinement"

    def test_all_states_have_categories(self) -> None:
        """Test that every state has a category."""
        for state in TaskState:
            category = state.get_category()
            assert isinstance(category, str)
            assert len(category) > 0
            assert category != "unknown"


class TestTaskStateIteration:
    """Tests for TaskState iteration order."""

    def test_iteration_order_matches_lifecycle(self) -> None:
        """Test that iteration order follows the lifecycle."""
        states = list(TaskState)
        expected_order = [
            TaskState.PENDING,
            TaskState.INTERPRETED,
            TaskState.TRANSFORMED,
            TaskState.PLANNED,
            TaskState.VALIDATED,
            TaskState.APPROVED,
            TaskState.EXECUTING,
            TaskState.EVALUATING,
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.CANCELLED,
            TaskState.REFINING,
        ]
        assert states == expected_order
