"""Unit tests for Skill Composition."""

import pytest
from src.intelligence.sdd.skill_composition import (
    SkillComposer,
    SkillChainStep,
    ChainResult,
    create_sdd_chain
)
from src.intelligence.sdd.context import SDDContext
from src.intelligence.sdd.skills import IntentParsingSkill, AmbiguityDetectionSkill
from src.intelligence.skills.skill_interface import Skill, SkillExecutionError


class MockSkill(Skill):
    """Mock skill for testing."""

    def __init__(self, name_val, return_value="result"):
        self._name = name_val
        self._return_value = return_value

    @property
    def name(self) -> str:
        return self._name

    def execute(self, context, **kwargs):
        return self._return_value


class FailingSkill(Skill):
    """Mock skill that always fails."""

    @property
    def name(self) -> str:
        return "failing"

    def execute(self, context, **kwargs):
        raise SkillExecutionError("Intentional failure")


class TestSkillComposer:
    """Test suite for SkillComposer."""

    def test_register_chain(self):
        """Test registering a skill chain."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        steps = [
            SkillChainStep(MockSkill("skill1"), "output1"),
            SkillChainStep(MockSkill("skill2"), "output2")
        ]

        composer.register_chain("test_chain", steps)

        assert "test_chain" in composer.get_chains()

    def test_execute_chain_success(self):
        """Test successful chain execution."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        steps = [
            SkillChainStep(MockSkill("skill1", "result1"), "output1"),
            SkillChainStep(MockSkill("skill2", "result2"), "output2")
        ]
        composer.register_chain("test_chain", steps)

        result = composer.execute_chain("test_chain")

        assert isinstance(result, ChainResult)
        assert result.success is True
        assert result.outputs["output1"] == "result1"
        assert result.outputs["output2"] == "result2"
        assert len(result.errors) == 0

    def test_execute_chain_with_initial_input(self):
        """Test chain execution with initial input."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        steps = [
            SkillChainStep(MockSkill("skill1", "result"), "output1")
        ]
        composer.register_chain("test_chain", steps)

        result = composer.execute_chain(
            "test_chain",
            initial_input={"key": "value"}
        )

        assert result.success is True
        assert "key" in result.outputs
        assert result.outputs["key"] == "value"

    def test_execute_chain_fail_fast(self):
        """Test chain execution stops on first error with fail_fast=True."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        steps = [
            SkillChainStep(MockSkill("skill1", "result1"), "output1"),
            SkillChainStep(FailingSkill(), "output2"),
            SkillChainStep(MockSkill("skill3", "result3"), "output3")
        ]
        composer.register_chain("test_chain", steps)

        result = composer.execute_chain("test_chain", fail_fast=True)

        assert result.success is False
        assert len(result.errors) > 0
        # Should not execute skill3
        assert "output3" not in result.outputs

    def test_execute_chain_no_fail_fast(self):
        """Test chain execution continues on error with fail_fast=False."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        steps = [
            SkillChainStep(MockSkill("skill1", "result1"), "output1"),
            SkillChainStep(FailingSkill(), "output2"),
            SkillChainStep(MockSkill("skill3", "result3"), "output3")
        ]
        composer.register_chain("test_chain", steps)

        result = composer.execute_chain("test_chain", fail_fast=False)

        # Should have error but continue
        assert len(result.errors) > 0
        # Should execute skill3
        assert "output3" in result.outputs

    def test_execute_chain_not_registered(self):
        """Test executing unregistered chain raises error."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        with pytest.raises(SkillExecutionError, match="Chain not registered"):
            composer.execute_chain("nonexistent_chain")

    def test_execute_parallel(self):
        """Test parallel skill execution."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        skills = [
            MockSkill("skill1", "result1"),
            MockSkill("skill2", "result2"),
            MockSkill("skill3", "result3")
        ]

        result = composer.execute_parallel(skills)

        assert "outputs" in result
        assert "errors" in result
        assert len(result["outputs"]) == 3
        assert result["outputs"]["skill1"] == "result1"
        assert result["outputs"]["skill2"] == "result2"
        assert result["outputs"]["skill3"] == "result3"

    def test_execute_parallel_with_inputs(self):
        """Test parallel execution with individual inputs."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        skills = [MockSkill("skill1"), MockSkill("skill2")]
        inputs = [{"key1": "value1"}, {"key2": "value2"}]

        result = composer.execute_parallel(skills, inputs)

        assert len(result["outputs"]) == 2

    def test_execute_parallel_input_mismatch(self):
        """Test parallel execution raises error on input mismatch."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        skills = [MockSkill("skill1"), MockSkill("skill2")]
        inputs = [{"key": "value"}]  # Only 1 input for 2 skills

        with pytest.raises(SkillExecutionError, match="must match"):
            composer.execute_parallel(skills, inputs)

    def test_execute_parallel_with_failure(self):
        """Test parallel execution handles failures."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        skills = [
            MockSkill("skill1", "result1"),
            FailingSkill(),
            MockSkill("skill3", "result3")
        ]

        result = composer.execute_parallel(skills)

        assert len(result["outputs"]) == 2  # 2 successful
        assert len(result["errors"]) == 1   # 1 failed
        assert "failing" in result["errors"]

    def test_get_chains(self):
        """Test retrieving registered chain names."""
        context = SDDContext("test")
        composer = SkillComposer(context)

        composer.register_chain("chain1", [])
        composer.register_chain("chain2", [])

        chains = composer.get_chains()

        assert "chain1" in chains
        assert "chain2" in chains
        assert len(chains) == 2

    def test_chain_result_attributes(self):
        """Test ChainResult attributes."""
        result = ChainResult(
            success=True,
            outputs={"key": "value"},
            errors=[],
            execution_time=1.5
        )

        assert result.success is True
        assert result.outputs["key"] == "value"
        assert len(result.errors) == 0
        assert result.execution_time == 1.5


class TestCreateSDDChain:
    """Test suite for create_sdd_chain factory."""

    def test_create_sdd_chain_returns_composer(self):
        """Test create_sdd_chain returns SkillComposer."""
        context = SDDContext("test")

        composer = create_sdd_chain(context)

        assert isinstance(composer, SkillComposer)

    def test_create_sdd_chain_registers_chains(self):
        """Test create_sdd_chain registers default chains."""
        context = SDDContext("test")

        composer = create_sdd_chain(context)

        chains = composer.get_chains()

        # Should register default SDD chains
        assert "parse_intent" in chains
        assert "generate_spec" in chains
        assert "create_plan" in chains
        assert "provide_guidance" in chains

    def test_create_sdd_chain_parse_intent(self):
        """Test parse_intent chain."""
        context = SDDContext("create a spec for user authentication")

        composer = create_sdd_chain(context)

        result = composer.execute_chain(
            "parse_intent",
            initial_input={"user_input": "create a spec"}
        )

        # Should have intent and ambiguities
        assert "intent" in result.outputs or "ambiguities" in result.outputs
