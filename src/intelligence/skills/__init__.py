"""
Reusable Cognitive Skills for the Intelligence Framework.

This package provides the skill system for defining, registering, and
executing stateless, domain-agnostic cognitive skills.

Public API:
- Skill: Abstract base class for all skills
- SkillRegistry: Registry for managing skills
- SkillInput/SkillOutput: Type definitions for skill I/O
- Exceptions: SkillError, SkillValidationError, etc.
"""

from src.intelligence.skills.skill_interface import (
    # Core interface
    Skill,
    # Type definitions
    SkillInput,
    SkillOutput,
    SkillMetadata,
    # Exceptions
    SkillError,
    SkillValidationError,
    SkillExecutionError,
    SkillTimeoutError,
    SkillNotFoundError,
)

from src.intelligence.skills.skill_registry import (
    SkillRegistry,
    SYSTEM_SKILL_REGISTRY,
    get_global_registry,
    register_skill,
    get_skill,
)

__all__ = [
    # Core interface
    "Skill",
    # Type definitions
    "SkillInput",
    "SkillOutput",
    "SkillMetadata",
    # Exceptions
    "SkillError",
    "SkillValidationError",
    "SkillExecutionError",
    "SkillTimeoutError",
    "SkillNotFoundError",
    # Registry
    "SkillRegistry",
    "SYSTEM_SKILL_REGISTRY",
    "get_global_registry",
    "register_skill",
    "get_skill",
]
