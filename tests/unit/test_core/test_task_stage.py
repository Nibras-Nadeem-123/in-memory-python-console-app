"""
Tests for the TaskStage enum.

This module contains unit tests for the TaskStage enumeration,
verifying stage values, transitions, and helper methods.
"""

import pytest

from src.intelligence.core.task_stage import TaskStage


class TestTaskStageValues:
    """Tests for TaskStage enum values."""

    def test_all_stages_defined(self) -> None:
        """Verify all 10 stages are defined."""
        expected_stages = [
            "INPUT",
            "INTERPRET",
            "TRANSFORM",
            "PLAN",
            "VALIDATE",
            "APPROVE",
            "EXECUTING",
            "EVALUATING",
            "REFINING",
            "TERMINATE",
        ]
        actual_stages = [stage.name for stage in TaskStage]
        assert set(expected_stages) == set(actual_stages)

    def test_stage_count(self) -> None:
        """Verify exactly 10 stages are defined."""
        assert len(TaskStage) == 10

    def test_stage_values_are_auto_incremented(self) -> None:
        """Verify stage values are 1-10."""
        values = [stage.value for stage in TaskStage]
        assert values == list(range(1, 11))


class TestTaskStageFromString:
    """Tests for TaskStage.from_string() method."""

    def test_valid_stage_name_lowercase(self) -> None:
        """Test creating stage from lowercase string."""
        stage = TaskStage.from_string("interpret")
        assert stage == TaskStage.INTERPRET

    def test_valid_stage_name_uppercase(self) -> None:
        """Test creating stage from uppercase string."""
        stage = TaskStage.from_string("INTERPRET")
        assert stage == TaskStage.INTERPRET

    def test_valid_stage_name_mixed_case(self) -> None:
        """Test creating stage from mixed case string."""
        stage = TaskStage.from_string("InTeRpReT")
        assert stage == TaskStage.INTERPRET

    def test_valid_stage_with_whitespace(self) -> None:
        """Test creating stage with surrounding whitespace."""
        stage = TaskStage.from_string("  interpret  ")
        assert stage == TaskStage.INTERPRET

    def test_invalid_stage_name_raises_value_error(self) -> None:
        """Test that invalid stage name raises ValueError."""
        with pytest.raises(ValueError):
            TaskStage.from_string("invalid_stage")

    def test_empty_string_raises_value_error(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            TaskStage.from_string("")


class TestTaskStageIsTerminal:
    """Tests for TaskStage.is_terminal() method."""

    def test_terminate_is_terminal(self) -> None:
        """Test that TERMINATE is a terminal stage."""
        assert TaskStage.TERMINATE.is_terminal() is True

    def test_other_stages_are_not_terminal(self) -> None:
        """Test that all non-TERMINATE stages are not terminal."""
        non_terminal = [s for s in TaskStage if s != TaskStage.TERMINATE]
        for stage in non_terminal:
            assert stage.is_terminal() is False


class TestTaskStageCanTransitionTo:
    """Tests for TaskStage.can_transition_to() method."""

    def test_input_to_interpret(self) -> None:
        """Test valid transition from INPUT to INTERPRET."""
        assert TaskStage.INPUT.can_transition_to(TaskStage.INTERPRET) is True

    def test_input_to_other_fails(self) -> None:
        """Test that INPUT cannot transition directly to other stages."""
        invalid_targets = [
            TaskStage.TRANSFORM,
            TaskStage.PLAN,
            TaskStage.EXECUTING,
            TaskStage.TERMINATE,
        ]
        for target in invalid_targets:
            assert TaskStage.INPUT.can_transition_to(target) is False

    def test_linear_progression_valid(self) -> None:
        """Test that linear progression through stages is valid."""
        stages = [
            TaskStage.INPUT,
            TaskStage.INTERPRET,
            TaskStage.TRANSFORM,
            TaskStage.PLAN,
            TaskStage.VALIDATE,
            TaskStage.APPROVE,
            TaskStage.EXECUTING,
            TaskStage.EVALUATING,
        ]
        for i in range(len(stages) - 1):
            assert stages[i].can_transition_to(stages[i + 1]) is True

    def test_evaluating_to_refining(self) -> None:
        """Test that EVALUATING can transition to REFINING."""
        assert TaskStage.EVALUATING.can_transition_to(TaskStage.REFINING) is True

    def test_evaluating_to_terminate(self) -> None:
        """Test that EVALUATING can transition to TERMINATE."""
        assert TaskStage.EVALUATING.can_transition_to(TaskStage.TERMINATE) is True

    def test_refining_can_loop_back_to_plan(self) -> None:
        """Test that REFINING can transition back to PLAN."""
        assert TaskStage.REFINING.can_transition_to(TaskStage.PLAN) is True

    def test_refining_to_terminate(self) -> None:
        """Test that REFINING can transition to TERMINATE."""
        assert TaskStage.REFINING.can_transition_to(TaskStage.TERMINATE) is True

    def test_terminate_cannot_transition(self) -> None:
        """Test that TERMINATE cannot transition to any stage."""
        for target in TaskStage:
            assert TaskStage.TERMINATE.can_transition_to(target) is False


class TestTaskStageGetDescription:
    """Tests for TaskStage.get_description() method."""

    def test_each_stage_has_description(self) -> None:
        """Test that every stage has a non-empty description."""
        for stage in TaskStage:
            description = stage.get_description()
            assert isinstance(description, str)
            assert len(description) > 0

    def test_descriptions_are_meaningful(self) -> None:
        """Test that descriptions are meaningful and descriptive."""
        descriptions = {
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
        for stage, expected in descriptions.items():
            assert stage.get_description() == expected


class TestTaskStageGetOutputType:
    """Tests for TaskStage.get_output_type() method."""

    def test_each_stage_has_output_type(self) -> None:
        """Test that every stage has an output type."""
        for stage in TaskStage:
            output_type = stage.get_output_type()
            assert isinstance(output_type, str)
            assert len(output_type) > 0

    def test_output_types_match_specification(self) -> None:
        """Test that output types match the intelligence model specification."""
        expected_types = {
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
        for stage, expected in expected_types.items():
            assert stage.get_output_type() == expected


class TestTaskStageIteration:
    """Tests for TaskStage iteration order."""

    def test_iteration_order_matches_lifecycle(self) -> None:
        """Test that iteration order follows the lifecycle."""
        stages = list(TaskStage)
        expected_order = [
            TaskStage.INPUT,
            TaskStage.INTERPRET,
            TaskStage.TRANSFORM,
            TaskStage.PLAN,
            TaskStage.VALIDATE,
            TaskStage.APPROVE,
            TaskStage.EXECUTING,
            TaskStage.EVALUATING,
            TaskStage.REFINING,
            TaskStage.TERMINATE,
        ]
        assert stages == expected_order
