"""Base agent interface for Spec-Driven Development system."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.intelligence.context import ExecutionContext


class Agent(ABC):
    """Base class for all SDD reasoning agents.

    All agents:
    - Have a unique name
    - Declare what they can handle via can_handle()
    - Execute via execute()
    - Only interact through the provided context
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique agent identifier."""
        ...

    @abstractmethod
    def can_handle(self, context: ExecutionContext) -> bool:
        """Return True if this agent should handle the current context state."""
        ...

    @abstractmethod
    def execute(self, context: ExecutionContext, **kwargs: Any) -> Any:
        """Execute the agent's primary function.

        Args:
            context: The SDD execution context containing intent, artifacts, and history.
            **kwargs: Agent-specific arguments.

        Returns:
            Result of agent execution (e.g., parsed Intent, generated Spec).
        """
        ...
