"""
Core Runtime Architecture for the Intelligence Framework.

This module provides the RuntimeEngine for executing plans through agent
routing and skill invocation. It is the execution layer of the system,
responsible for the mechanical execution of plans created by the engine.

Key Components:
- Action: A single step in an execution plan
- ExecutionPlan: Ordered sequence of actions
- Outcome: Result of plan execution
- Agent: Decision-making unit that invokes skills
- AgentRegistry: Registry for managing agents
- RuntimeEngine: Orchestrates plan execution
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Type
import uuid

from src.intelligence.context import ExecutionContext
from src.intelligence.skills.skill_interface import (
    Skill,
    SkillError,
    SkillExecutionError,
    SkillNotFoundError,
)
from src.intelligence.skills.skill_registry import SkillRegistry


# =============================================================================
# Exceptions
# =============================================================================

class RuntimeError(Exception):
    """Base exception for runtime errors."""
    pass


class RoutingError(RuntimeError):
    """Raised when agent routing fails."""
    pass


class PlanValidationError(RuntimeError):
    """Raised when plan validation fails."""
    pass


class MaxStepsExceededError(RuntimeError):
    """Raised when maximum execution steps are exceeded."""
    pass


class ExecutionError(RuntimeError):
    """Raised when plan execution fails."""
    pass


# =============================================================================
# Data Structures
# =============================================================================

class ExecutionStatus(str, Enum):
    """Status of an execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Action:
    """
    A single step in an execution plan.

    Attributes:
        skill: Name of the skill to invoke
        args: Arguments to pass to the skill
        description: Optional human-readable description
        agent_hint: Optional hint for agent routing
    """
    skill: str
    args: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    agent_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "skill": self.skill,
            "args": self.args,
            "description": self.description,
            "agent_hint": self.agent_hint,
        }


@dataclass
class ExecutionPlan:
    """
    An ordered sequence of actions to be executed.

    Attributes:
        actions: List of actions to execute in order
        metadata: Additional plan metadata
    """
    actions: List[Action] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.actions)

    def __iter__(self):
        return iter(self.actions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "actions": [a.to_dict() for a in self.actions],
            "metadata": self.metadata,
        }


@dataclass
class Outcome:
    """
    The result of an execution.

    Attributes:
        status: Final execution status
        result: The final result value (if successful)
        error: Error message (if failed)
        context: The final execution context
        execution_time_ms: Total execution time in milliseconds
        steps_executed: Number of steps that were executed
    """
    status: ExecutionStatus
    result: Any = None
    error: Optional[str] = None
    context: Optional[ExecutionContext] = None
    execution_time_ms: float = 0.0
    steps_executed: int = 0

    @property
    def success(self) -> bool:
        """Whether the execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes context for serialization)."""
        return {
            "status": self.status.value,
            "result": str(self.result)[:500] if self.result else None,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "steps_executed": self.steps_executed,
        }


# =============================================================================
# Agent Framework
# =============================================================================

class Agent(ABC):
    """
    Abstract base class for agents.

    An agent is a decision-making unit responsible for a specific category
    of tasks. Agents route to and invoke skills based on the action type.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the agent."""
        pass

    @property
    def description(self) -> str:
        """Description of the agent's capabilities."""
        return ""

    @abstractmethod
    def can_handle(self, action: Action) -> bool:
        """
        Check if this agent can handle the given action.

        Args:
            action: The action to check

        Returns:
            True if this agent can handle the action
        """
        pass

    @abstractmethod
    def execute(
        self,
        action: Action,
        context: ExecutionContext,
        skill_registry: SkillRegistry,
    ) -> Any:
        """
        Execute an action.

        Args:
            action: The action to execute
            context: The execution context
            skill_registry: Registry to get skills from

        Returns:
            The result of the action execution

        Raises:
            ExecutionError: If execution fails
        """
        pass


class GeneralAgent(Agent):
    """
    A general-purpose agent that can handle any action.

    This is the default agent that simply routes actions to their
    corresponding skills without any special handling.
    """

    @property
    def name(self) -> str:
        return "general"

    @property
    def description(self) -> str:
        return "General-purpose agent for executing any skill"

    def can_handle(self, action: Action) -> bool:
        """General agent can handle any action."""
        return True

    def execute(
        self,
        action: Action,
        context: ExecutionContext,
        skill_registry: SkillRegistry,
    ) -> Any:
        """Execute the action by invoking the corresponding skill."""
        try:
            skill = skill_registry.get(action.skill)
            result = skill.execute(context, **action.args)
            return result
        except SkillNotFoundError as e:
            raise ExecutionError(f"Skill not found: {action.skill}") from e
        except SkillError as e:
            raise ExecutionError(f"Skill execution failed: {e}") from e
        except Exception as e:
            raise ExecutionError(f"Unexpected error during execution: {e}") from e


class AgentRegistry:
    """
    Registry for managing agents.

    Provides agent registration, lookup, and routing based on action type.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._default_agent: Optional[Agent] = None

    def register(self, agent: Agent, as_default: bool = False) -> None:
        """
        Register an agent.

        Args:
            agent: The agent to register
            as_default: Whether to set as the default agent
        """
        self._agents[agent.name] = agent
        if as_default:
            self._default_agent = agent

    def get(self, name: str) -> Agent:
        """Get an agent by name."""
        if name not in self._agents:
            raise RoutingError(f"Agent '{name}' not found.")
        return self._agents[name]

    def route(self, action: Action) -> Agent:
        """
        Find an appropriate agent for the action.

        Args:
            action: The action to route

        Returns:
            An agent that can handle the action

        Raises:
            RoutingError: If no suitable agent is found
        """
        # Check for explicit agent hint
        if action.agent_hint and action.agent_hint in self._agents:
            return self._agents[action.agent_hint]

        # Find an agent that can handle the action
        for agent in self._agents.values():
            if agent.can_handle(action):
                return agent

        # Fall back to default agent
        if self._default_agent:
            return self._default_agent

        raise RoutingError(f"No agent found to handle action: {action.skill}")

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())


# =============================================================================
# Runtime Engine
# =============================================================================

class RuntimeEngine:
    """
    Manages the entire runtime environment and orchestrates plan execution.

    The RuntimeEngine is responsible for:
    - Creating execution contexts
    - Routing actions to appropriate agents
    - Managing the execution lifecycle
    - Handling errors and logging
    """

    DEFAULT_MAX_STEPS = 100

    def __init__(
        self,
        skill_registry: SkillRegistry,
        agent_registry: Optional[AgentRegistry] = None,
        max_steps: int = DEFAULT_MAX_STEPS,
    ) -> None:
        """
        Initialize the runtime engine.

        Args:
            skill_registry: Registry of available skills
            agent_registry: Registry of available agents (optional)
            max_steps: Maximum number of steps per execution
        """
        self._skill_registry = skill_registry
        self._agent_registry = agent_registry or AgentRegistry()
        self._max_steps = max_steps
        self._running = False

        # Register default general agent if no agents registered
        if not self._agent_registry.list_agents():
            self._agent_registry.register(GeneralAgent(), as_default=True)

    def start(self) -> None:
        """Start the runtime engine."""
        self._running = True

    def shutdown(self) -> None:
        """Shutdown the runtime engine."""
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if the engine is running."""
        return self._running

    def validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Validate an execution plan.

        Args:
            plan: The plan to validate

        Raises:
            PlanValidationError: If the plan is invalid
        """
        if len(plan.actions) > self._max_steps:
            raise PlanValidationError(
                f"Plan has {len(plan.actions)} actions, exceeds max of {self._max_steps}"
            )

        for i, action in enumerate(plan.actions):
            if not action.skill:
                raise PlanValidationError(f"Action {i} has no skill specified")

            # Verify skill exists
            if not self._skill_registry.has(action.skill):
                raise PlanValidationError(
                    f"Action {i} references unknown skill: {action.skill}"
                )

    def execute_plan(
        self,
        plan: ExecutionPlan,
        goal: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> Outcome:
        """
        Execute a plan and return the outcome.

        Args:
            plan: The execution plan
            goal: Optional goal metadata
            context: Optional existing context (new one created if not provided)

        Returns:
            The execution outcome
        """
        start_time = datetime.now(timezone.utc)

        # Create or use provided context
        if context is None:
            context = ExecutionContext.create(goal=goal or {})

        context.append_event("plan_submitted", {
            "action_count": len(plan.actions),
            "plan_metadata": plan.metadata,
        })
        context.status = "in_progress"

        steps_executed = 0
        last_result = None
        error_message = None

        try:
            for i, action in enumerate(plan.actions):
                if i >= self._max_steps:
                    raise MaxStepsExceededError(
                        f"Execution exceeded maximum of {self._max_steps} steps"
                    )

                context.append_event("action_start", {
                    "step": i + 1,
                    "skill": action.skill,
                    "args": action.args,
                    "description": action.description,
                })

                # Route to appropriate agent
                agent = self._agent_registry.route(action)
                context.append_event("agent_routed", {
                    "step": i + 1,
                    "agent": agent.name,
                })

                # Execute the action
                result = agent.execute(action, context, self._skill_registry)
                last_result = result

                context.append_event("action_success", {
                    "step": i + 1,
                    "result_preview": str(result)[:100] if result else None,
                })

                steps_executed = i + 1

            # All actions completed successfully
            context.status = "success"
            context.append_event("plan_success", {
                "steps_completed": steps_executed,
                "final_state_keys": list(context.state.keys()),
            })

            status = ExecutionStatus.SUCCESS

        except MaxStepsExceededError as e:
            context.status = "failed"
            error_message = str(e)
            context.append_event("plan_failure", {"error": error_message, "type": "max_steps"})
            status = ExecutionStatus.FAILED

        except ExecutionError as e:
            context.status = "failed"
            error_message = str(e)
            context.append_event("plan_failure", {"error": error_message, "type": "execution"})
            status = ExecutionStatus.FAILED

        except Exception as e:
            context.status = "failed"
            error_message = f"Unexpected error: {e}"
            context.append_event("plan_failure", {"error": error_message, "type": "unexpected"})
            status = ExecutionStatus.FAILED

        end_time = datetime.now(timezone.utc)
        execution_time_ms = (end_time - start_time).total_seconds() * 1000

        return Outcome(
            status=status,
            result=last_result,
            error=error_message,
            context=context,
            execution_time_ms=execution_time_ms,
            steps_executed=steps_executed,
        )

    # Backwards compatibility alias
    def submit_plan(
        self,
        goal: Dict[str, Any],
        plan: ExecutionPlan,
    ) -> ExecutionContext:
        """
        Submit and execute a plan (backwards compatibility).

        Args:
            goal: The goal metadata
            plan: The execution plan

        Returns:
            The final execution context
        """
        outcome = self.execute_plan(plan, goal=goal)
        return outcome.context


# =============================================================================
# Backwards Compatibility
# =============================================================================

# Re-export SkillExecutionError for backwards compatibility
SkillExecutionError = ExecutionError
