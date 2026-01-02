"""
Skill Registry for the Intelligence Framework.

This module provides the SkillRegistry class for managing the registration,
discovery, and retrieval of cognitive skills. The registry is the central
point for skill management in the system.

Key Features:
- Register and unregister skills
- Retrieve skills by name
- List all registered skills
- Query skills by tags/metadata
"""
from __future__ import annotations

from typing import Dict, List, Optional, Callable, Any

from src.intelligence.skills.skill_interface import (
    Skill,
    SkillMetadata,
    SkillNotFoundError,
    SkillError,
)


class SkillRegistry:
    """
    Manages the registration and retrieval of all available cognitive skills.

    The registry provides a centralized location for skill management,
    allowing skills to be registered, discovered, and retrieved by name.

    Example:
        registry = SkillRegistry()
        registry.register(MySkill())
        skill = registry.get("my_skill")
        result = skill.execute(context, arg1="value")
    """

    def __init__(self) -> None:
        """Initialize an empty skill registry."""
        self._skills: Dict[str, Skill] = {}
        self._metadata: Dict[str, SkillMetadata] = {}

    def register(self, skill: Skill) -> None:
        """
        Register a new skill with the registry.

        Args:
            skill: An instance of a class that implements the Skill interface

        Raises:
            ValueError: If a skill with the same name is already registered
            TypeError: If the provided object is not a Skill instance
        """
        if not isinstance(skill, Skill):
            raise TypeError(f"Expected Skill instance, got {type(skill).__name__}")

        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' is already registered.")

        self._skills[skill.name] = skill
        self._metadata[skill.name] = skill.metadata

    def unregister(self, name: str) -> None:
        """
        Remove a skill from the registry.

        Args:
            name: The name of the skill to remove

        Raises:
            SkillNotFoundError: If no skill with the given name is found
        """
        if name not in self._skills:
            raise SkillNotFoundError(f"Skill '{name}' not found.")

        del self._skills[name]
        del self._metadata[name]

    def get(self, name: str) -> Skill:
        """
        Retrieve a registered skill by its name.

        Args:
            name: The name of the skill to retrieve

        Returns:
            The skill instance

        Raises:
            SkillNotFoundError: If no skill with the given name is found
        """
        if name not in self._skills:
            raise SkillNotFoundError(f"Skill '{name}' not found.")
        return self._skills[name]

    # Alias for backwards compatibility
    def get_skill(self, name: str) -> Skill:
        """Alias for get() - backwards compatibility."""
        return self.get(name)

    def has(self, name: str) -> bool:
        """
        Check if a skill is registered.

        Args:
            name: The name of the skill to check

        Returns:
            True if the skill is registered, False otherwise
        """
        return name in self._skills

    def list_skills(self) -> Dict[str, Skill]:
        """
        Get all registered skills.

        Returns:
            A copy of the skills dictionary
        """
        return self._skills.copy()

    def list_names(self) -> List[str]:
        """
        Get the names of all registered skills.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    def get_metadata(self, name: str) -> SkillMetadata:
        """
        Get metadata for a registered skill.

        Args:
            name: The name of the skill

        Returns:
            The skill's metadata

        Raises:
            SkillNotFoundError: If no skill with the given name is found
        """
        if name not in self._metadata:
            raise SkillNotFoundError(f"Skill '{name}' not found.")
        return self._metadata[name]

    def find_by_tag(self, tag: str) -> List[Skill]:
        """
        Find all skills with a specific tag.

        Args:
            tag: The tag to search for

        Returns:
            List of skills with the specified tag
        """
        return [
            skill for skill in self._skills.values()
            if tag in skill.metadata.tags
        ]

    def clear(self) -> None:
        """Remove all registered skills."""
        self._skills.clear()
        self._metadata.clear()

    def __len__(self) -> int:
        """Return the number of registered skills."""
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        """Check if a skill is registered."""
        return name in self._skills

    def __iter__(self):
        """Iterate over skill names."""
        return iter(self._skills)

    def __repr__(self) -> str:
        return f"SkillRegistry(skills={list(self._skills.keys())})"


# =============================================================================
# Global Registry Instance
# =============================================================================

# A global instance for the system to use
# This can be used as a singleton for simple use cases
SYSTEM_SKILL_REGISTRY = SkillRegistry()


def get_global_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    return SYSTEM_SKILL_REGISTRY


def register_skill(skill: Skill) -> None:
    """Register a skill with the global registry."""
    SYSTEM_SKILL_REGISTRY.register(skill)


def get_skill(name: str) -> Skill:
    """Get a skill from the global registry."""
    return SYSTEM_SKILL_REGISTRY.get(name)
