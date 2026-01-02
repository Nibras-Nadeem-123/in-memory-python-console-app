"""Best Practices Skill for Spec-Driven Development.

Provides language/framework-specific best practices and patterns.
"""

from typing import Dict, Any, List
from src.intelligence.sdd.data_models import Plan
from src.intelligence.skills.skill_interface import Skill, SkillInput, SkillOutput
from src.intelligence.sdd.context import SDDContext


class BestPracticesSkill(Skill):
    """Skill for providing best practices recommendations.

    Offers:
    - Language-specific patterns
    - Framework conventions
    - Testing strategies
    - Code organization standards
    """

    # Best practices by technology
    BEST_PRACTICES = {
        "python": {
            "naming": [
                "Use snake_case for variables and functions",
                "Use PascalCase for classes",
                "Use UPPER_CASE for constants",
                "Use _leading_underscore for internal/private"
            ],
            "structure": [
                "Separate models, services, and API layers",
                "Use __init__.py to mark packages",
                "Place tests in tests/ directory matching src/",
                "Use absolute imports (from src import x)"
            ],
            "testing": [
                "Write unit tests for all public methods",
                "Use pytest fixtures for setup/teardown",
                "Mock external dependencies",
                "Aim for >80% code coverage"
            ],
            "patterns": [
                "Use dataclasses for simple data models",
                "Use context managers for resource cleanup",
                "Use type hints for better IDE support",
                "Implement __repr__ for debugging"
            ]
        },
        "javascript": {
            "naming": [
                "Use camelCase for variables and functions",
                "Use PascalCase for classes and components",
                "Use UPPER_CASE for constants",
                "Use _leading_underscore for internal/private"
            ],
            "structure": [
                "Separate components, hooks, and utilities",
                "Use index.js for barrel exports",
                "Place tests in __tests__/ or .test.js files",
                "Use absolute imports with aliases"
            ],
            "testing": [
                "Write unit tests for pure functions",
                "Use mocking for external dependencies",
                "Test components with React Testing Library",
                "Aim for >80% code coverage"
            ],
            "patterns": [
                "Use functional components and hooks",
                "Implement error boundaries",
                "Use TypeScript for type safety",
                "Follow SRP (Single Responsibility Principle)"
            ]
        }
    }

    @property
    def name(self) -> str:
        return "best_practices"

    @property
    def description(self) -> str:
        return "Provides language/framework-specific best practices."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def input_schema(self) -> SkillInput:
        return SkillInput(
            name="plan",
            type=Plan,
            description="Implementation plan with architecture details",
            required=True
        )

    @property
    def output_schema(self) -> SkillOutput:
        return SkillOutput(
            name="practices",
            type=Dict[str, List[str]],
            description="Best practices organized by category"
        )

    def execute(self, context: SDDContext, plan: Plan = None, **kwargs: Any) -> Dict[str, List[str]]:
        """Provide best practices recommendations.

        Args:
            context: The SDD execution context.
            plan: Plan object with architecture details.
            **kwargs: Additional arguments (e.g., language, framework).

        Returns:
            Dictionary of best practices by category.
        """
        # Detect technology
        language = kwargs.get("language", self._detect_language(plan.architecture if plan else ""))

        # Get practices for language
        practices = self.BEST_PRACTICES.get(language, self._get_default_practices())

        # Log recommendation
        context._log_event("best_practices_provided", {
            "language": language,
            "categories": list(practices.keys())
        })

        return practices

    def _detect_language(self, architecture: str) -> str:
        """Detect programming language from architecture."""
        arch_lower = architecture.lower()

        if any(lang in arch_lower for lang in ["python", "django", "flask"]):
            return "python"
        elif any(lang in arch_lower for lang in ["javascript", "typescript", "node", "react"]):
            return "javascript"
        elif any(lang in arch_lower for lang in ["java", "spring"]):
            return "java"
        elif any(lang in arch_lower for lang in ["c#", ".net"]):
            return "csharp"
        else:
            return "python"  # Default

    def _get_default_practices(self) -> Dict[str, List[str]]:
        """Get generic best practices as fallback."""
        return {
            "naming": [
                "Use consistent naming conventions",
                "Make names descriptive and self-documenting",
                "Avoid abbreviations unless widely understood"
            ],
            "structure": [
                "Organize code by layer/domain",
                "Keep files focused (single responsibility)",
                "Use consistent directory structure"
            ],
            "testing": [
                "Write tests before implementation (TDD)",
                "Test both happy path and edge cases",
                "Mock external dependencies"
            ],
            "patterns": [
                "Follow SOLID principles",
                "Implement error handling",
                "Add logging for debugging",
                "Document public APIs"
            ]
        }
