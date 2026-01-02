"""Base skill interface for spec generation."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.context import RequestContext


class Skill(ABC):
    """
    Base interface for all spec generation skills.

    Skills are stateless, composable units that extract specific
    information from user intent.
    """

    @abstractmethod
    def execute(self, context: RequestContext) -> Any:
        """
        Execute skill logic.

        Args:
            context: Request context containing intent and state

        Returns:
            Skill-specific output (varies by skill)

        Raises:
            ValueError: If skill cannot extract required information
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Skill name for identification.

        Returns:
            Human-readable skill name
        """
        pass
