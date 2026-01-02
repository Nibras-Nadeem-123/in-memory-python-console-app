"""Tests for the Core Runtime Architecture."""
import pytest
from typing import Any, Dict
from src.intelligence.context import ExecutionContext
from src.intelligence.skills.skill_interface import Skill
from src.intelligence.skills.skill_registry import SkillRegistry
from src.intelligence.runtime import (
    RuntimeEngine,
    Agent,
    GeneralAgent,
    AgentRegistry,
    Action,
    ExecutionPlan,
    Outcome,
    ExecutionStatus,
    ExecutionError,
    RoutingError,
)


# =============================================================================
# Mock Skill for Testing
# =============================================================================

class MockSkill(Skill):
    """A mock skill for testing purposes."""

    def __init__(
        self,
        name: str,
        return_value: Any = None,
        raise_exception: Exception | None = None,
    ):
        self._name = name
        self._return_value = return_value
        self._raise_exception = raise_exception

    @property
    def name(self) -> str:
        return self._name

    def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
        context.add_event(f"{self.name}_executed", kwargs)
        if self._raise_exception:
            raise self._raise_exception
        context.state[f"{self.name}_result"] = self._return_value
        return self._return_value


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def dummy_context():
    """Create a dummy execution context for testing."""
    return ExecutionContext(execution_id="test_exec_runtime")


@pytest.fixture
def mock_skill_registry():
    """Create a skill registry with mock skills."""
    registry = SkillRegistry()
    registry.register(MockSkill("skill_one", return_value="Result One"))
    registry.register(MockSkill("skill_two", return_value="Result Two"))
    registry.register(MockSkill("failing_skill", raise_exception=ValueError("Skill failed!")))
    return registry


@pytest.fixture
def runtime_engine(mock_skill_registry):
    """Create a runtime engine with mock skills."""
    return RuntimeEngine(mock_skill_registry)


@pytest.fixture
def sample_goal():
    """Sample goal for testing."""
    return {"description": "test goal"}


# =============================================================================
# Agent Tests
# =============================================================================

def test_agent_execute_action_success(mock_skill_registry, dummy_context):
    """Test successful action execution through agent."""
    agent = GeneralAgent()
    action = Action(skill="skill_one", args={"input": 1})
    result = agent.execute(action, dummy_context, mock_skill_registry)
    assert result == "Result One"
    assert dummy_context.state["skill_one_result"] == "Result One"
    assert any(e.type == "skill_one_executed" for e in dummy_context.history)


def test_agent_execute_action_skill_not_found(mock_skill_registry, dummy_context):
    """Test agent execution with non-existent skill."""
    agent = GeneralAgent()
    action = Action(skill="non_existent_skill", args={})
    with pytest.raises(ExecutionError, match="Skill not found"):
        agent.execute(action, dummy_context, mock_skill_registry)


def test_agent_execute_action_skill_raises_exception(mock_skill_registry, dummy_context):
    """Test agent execution when skill raises an exception."""
    agent = GeneralAgent()
    action = Action(skill="failing_skill", args={})
    with pytest.raises(ExecutionError, match="Skill failed"):
        agent.execute(action, dummy_context, mock_skill_registry)


# =============================================================================
# AgentRegistry Tests
# =============================================================================

def test_agent_registry_register_and_get():
    """Test registering and retrieving agents."""
    registry = AgentRegistry()
    agent = GeneralAgent()
    registry.register(agent)

    retrieved = registry.get("general")
    assert retrieved is agent


def test_agent_registry_route():
    """Test routing actions to agents."""
    registry = AgentRegistry()
    agent = GeneralAgent()
    registry.register(agent, as_default=True)

    action = Action(skill="any_skill", args={})
    routed = registry.route(action)
    assert routed is agent


# =============================================================================
# RuntimeEngine Tests
# =============================================================================

def test_runtime_engine_execute_plan_success(runtime_engine, sample_goal):
    """Test successful plan execution."""
    plan = ExecutionPlan(actions=[
        Action(skill="skill_one", args={"step": 1}),
        Action(skill="skill_two", args={"step": 2}),
    ])

    outcome = runtime_engine.execute_plan(plan, goal=sample_goal)

    assert outcome.status == ExecutionStatus.SUCCESS
    assert outcome.success is True
    assert outcome.context is not None
    assert outcome.context.goal == sample_goal
    assert outcome.context.state["skill_one_result"] == "Result One"
    assert outcome.context.state["skill_two_result"] == "Result Two"
    assert outcome.steps_executed == 2


def test_runtime_engine_execute_plan_failure(runtime_engine, sample_goal):
    """Test plan execution with failing skill."""
    plan = ExecutionPlan(actions=[
        Action(skill="skill_one", args={"step": 1}),
        Action(skill="failing_skill", args={"step": 2}),
        Action(skill="skill_two", args={"step": 3}),  # Should not execute
    ])

    outcome = runtime_engine.execute_plan(plan, goal=sample_goal)

    assert outcome.status == ExecutionStatus.FAILED
    assert outcome.success is False
    assert outcome.error is not None
    assert "skill_one_result" in outcome.context.state
    assert "skill_two_result" not in outcome.context.state  # Should not have executed
    assert any("failing_skill_executed" in e.type for e in outcome.context.history)


def test_runtime_engine_execute_empty_plan(runtime_engine, sample_goal):
    """Test executing an empty plan."""
    plan = ExecutionPlan(actions=[])
    outcome = runtime_engine.execute_plan(plan, goal=sample_goal)

    assert outcome.status == ExecutionStatus.SUCCESS
    assert outcome.steps_executed == 0


def test_runtime_engine_submit_plan_backwards_compat(runtime_engine, sample_goal):
    """Test backwards-compatible submit_plan method."""
    plan = ExecutionPlan(actions=[
        Action(skill="skill_one", args={}),
    ])

    # submit_plan returns ExecutionContext for backwards compatibility
    context = runtime_engine.submit_plan(sample_goal, plan)

    assert isinstance(context, ExecutionContext)
    assert context.status == "success"


def test_runtime_engine_lifecycle():
    """Test runtime engine start/shutdown."""
    registry = SkillRegistry()
    engine = RuntimeEngine(registry)

    assert not engine.is_running

    engine.start()
    assert engine.is_running

    engine.shutdown()
    assert not engine.is_running


# =============================================================================
# Outcome Tests
# =============================================================================

def test_outcome_to_dict():
    """Test Outcome serialization."""
    outcome = Outcome(
        status=ExecutionStatus.SUCCESS,
        result="test result",
        steps_executed=3,
        execution_time_ms=150.5,
    )

    data = outcome.to_dict()
    assert data["status"] == "success"
    assert data["result"] == "test result"
    assert data["steps_executed"] == 3
    assert data["execution_time_ms"] == 150.5
