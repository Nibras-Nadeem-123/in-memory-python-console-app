"""
Skill Interface for the Intelligence Framework.

This module defines the core abstractions for reusable, stateless,
domain-agnostic cognitive skills. Skills are the fundamental building
blocks of all system functionality.

Key Components:
- Skill: Abstract base class for all skills
- SkillInput/SkillOutput: Type definitions for skill I/O
- Skill exceptions for error handling
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypeVar, Generic

# Type variables for generic skill I/O
T = TypeVar("T")


# =============================================================================
# Exceptions
# =============================================================================

class SkillError(Exception):
    """Base exception for skill-related errors."""
    pass


class SkillValidationError(SkillError):
    """Raised when skill input validation fails."""
    pass


class SkillExecutionError(SkillError):
    """Raised when skill execution fails."""
    pass


class SkillTimeoutError(SkillError):
    """Raised when skill execution times out."""
    pass


class SkillNotFoundError(SkillError):
    """Raised when a requested skill is not found."""
    pass


# =============================================================================
# Type Definitions
# =============================================================================

@dataclass
class SkillInput:
    """
    Structured input for a skill execution.

    Attributes:
        args: Positional arguments as a dictionary
        context_keys: Keys to read from execution context state
        metadata: Additional metadata for the execution
    """
    args: Dict[str, Any] = field(default_factory=dict)
    context_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillOutput:
    """
    Structured output from a skill execution.

    Attributes:
        result: The primary result of the skill execution
        state_updates: Key-value pairs to update in context state
        metadata: Additional metadata about the execution
        success: Whether the skill execution was successful
        error: Error message if execution failed
    """
    result: Any = None
    state_updates: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


@dataclass
class SkillMetadata:
    """
    Metadata describing a skill's capabilities and requirements.

    Attributes:
        name: Unique identifier for the skill
        description: Human-readable description
        version: Skill version string
        input_schema: Description of expected inputs
        output_schema: Description of outputs
        tags: Categorization tags
        timeout_seconds: Maximum execution time
    """
    name: str
    description: str = ""
    version: str = "1.0.0"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    timeout_seconds: Optional[float] = None


# =============================================================================
# Skill Interface
# =============================================================================

class Skill(ABC):
    """
    Abstract base class for a stateless, domain-agnostic, reusable skill.

    Skills are the fundamental building blocks of the intelligence system.
    They must be:
    - Stateless: No memory of previous invocations
    - Domain-agnostic: No hardcoded domain-specific logic
    - Composable: Output compatible as input to other skills

    Example:
        class EchoSkill(Skill):
            @property
            def name(self) -> str:
                return "echo"

            @property
            def description(self) -> str:
                return "Echoes the input message"

            def execute(self, context, **kwargs) -> Any:
                message = kwargs.get("message", "")
                context.state["last_echo"] = message
                return message
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name/identifier of the skill.

        This is used for registration and lookup in the skill registry.
        Must be unique across all registered skills.
        """
        pass

    @property
    def description(self) -> str:
        """Human-readable description of what the skill does."""
        return ""

    @property
    def version(self) -> str:
        """Version string for the skill."""
        return "1.0.0"

    @property
    def metadata(self) -> SkillMetadata:
        """Full metadata for the skill."""
        return SkillMetadata(
            name=self.name,
            description=self.description,
            version=self.version,
        )

    @abstractmethod
    def execute(self, context: Any, **kwargs: Any) -> Any:
        """
        Execute the skill's logic.

        This method should be stateless - all required information must
        be provided via the context or kwargs.

        Args:
            context: The current ExecutionContext for logging and state access
            **kwargs: Skill-specific arguments

        Returns:
            The result of the skill execution. This could be data to be
            stored in context state or a final result.

        Raises:
            SkillValidationError: If input validation fails
            SkillExecutionError: If execution fails
            SkillTimeoutError: If execution times out
        """
        pass

    def validate_inputs(self, **kwargs: Any) -> None:
        """
        Validate inputs before execution.

        Override this method to add custom validation logic.

        Args:
            **kwargs: The inputs to validate

        Raises:
            SkillValidationError: If validation fails
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
