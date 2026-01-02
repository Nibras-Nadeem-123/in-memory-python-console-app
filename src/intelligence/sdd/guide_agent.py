"""Execution Guidance Agent for Spec-Driven Development.

Provides implementation-ready guidance including code scaffolding,
best practices, and implementation order for building from specifications.
"""

from typing import Dict, Any, List
from .agent_base import Agent
from .data_models import Guide, Task
from .context import SDDContext
from .templates.spec_template import SPEC_TEMPLATE
from ..utils import format_output, log_event


class GuideAgent(Agent):
    """Agent responsible for Stage 4: Execution Guidance.

    Generates implementation guide with:
    - Code scaffolding templates
    - Best practices and conventions
    - Implementation order
    - Testing recommendations
    """

    @property
    def name(self) -> str:
        return "guide"

    def can_handle(self, context: SDDContext) -> bool:
        """Return True if this agent should handle current context.

        GuideAgent handles:
        - Context with plan artifact (Stage 3 complete)
        - Context with spec artifact (Stage 2 complete)

        Args:
            context: The SDD execution context.

        Returns:
            bool: True if agent should process this context.
        """
        # Check for plan artifact
        plan = context.get_latest_artifact("plan")
        spec = context.get_latest_artifact("spec")

        # Only proceed if we have both spec and plan
        if plan is not None and spec is not None:
            return True
        return False

    def execute(self, context: SDDContext, **kwargs: Any) -> Guide:
        """Generate implementation guide from plan.

        Args:
            context: The SDD execution context.
            **kwargs: Additional arguments.

        Returns:
            Guide: Implementation guidance document.
        """
        # Get plan from context
        plan = context.get_latest_artifact("plan")
        spec = context.get_latest_artifact("spec")
        if plan is None or spec is None:
            log_event(context, "plan_missing", {
                "message": "Plan artifact not found"
            })
            raise ValueError("Plan artifact required for guide generation")

        # Extract spec content
        spec_content = spec.content if isinstance(spec.content, str) else str(spec.content)

        # Generate guide content
        guide_content = self._generate_guide(context, spec_content)

        # Create guide object
        guide = Guide(
            title=self._generate_guide_title(spec_content),
            getting_started=self._get_started_section(spec_content),
            implementation_order=self._determine_implementation_order(spec_content),
            code_patterns=self._generate_code_patterns(spec_content),
            testing_recommendations=self._generate_testing_recommendations(spec_content)
        )

        # Store artifact
        plan_artifact_id = None
        spec_artifact_id = None
        for aid, artifact in context.artifacts.items():
            if artifact.artifact_type == "plan":
                plan_artifact_id = aid
            elif artifact.artifact_type == "spec":
                spec_artifact_id = aid

        context.add_artifact("guide", guide.content, {
            "plan_id": plan_artifact_id,
            "spec_id": spec_artifact_id
        })

        log_event(context, "guide_generated", {
            "title": guide.title,
            "sections_count": len(guide_content)
        })

        return guide

    def _generate_guide_title(self, spec_content: str) -> str:
        """Generate guide title from spec."""
        # Extract key entities (first few meaningful words)
        words = spec_content.split()[:15]
        entity = words[0] if len(words) > 0 else "System"
        return f"Implementation Guide: {entity} Development"

    def _get_started_section(self, spec_content: str) -> str:
        """Generate getting started section."""
        steps = [
            "1. Review the generated specification (spec.md)",
            "2. Set up the project structure following the architecture notes.",
            "3. Implement the core components and data models.",
            "4. Follow the implementation order in the plan.",
            "5. Write and run tests as you complete each component.",
            "6. Document any deviations or architectural decisions."
        ]
        return "To get started with this implementation:\n- " + "\n- ".join(steps)

    def _determine_implementation_order(self, spec_content: str) -> str:
        """Determine logical implementation order."""
        # Simple heuristic: database before services before endpoints
        if "database" in spec_content.lower():
            return "Data layer (models) → Service layer → API layer"
        elif "API" in spec_content.lower() or "REST" in spec_content.upper():
            return "API layer → Service layer → Frontend (if any)"
        else:
            return "Models → Services → Endpoints (if any)"

    def _generate_code_patterns(self, spec_content: str) -> str:
        """Generate code pattern recommendations."""
        patterns = [
            "Use Python dataclasses for models",
            "Follow REST naming conventions (e.g., GET /users/{id})",
            "Apply dependency injection for external services",
            "Implement async/await for I/O operations",
            "Use environment variables for configuration",
        ]
        return "\n".join([f"- {p}" for p in patterns])

    def _generate_testing_recommendations(self, spec_content: str) -> str:
        """Generate testing recommendations."""
        recommendations = [
            "Write unit tests for all components",
            "Write integration tests for data flows",
            "Test edge cases: empty inputs, invalid data, concurrent access",
            "Aim for >80% code coverage on SDD components",
            "Document test cases with Given-When-Then format",
        ]
        return "\n".join([f"- {r}" for r in recommendations])

    def _generate_guide(self, context: SDDContext, spec_content: str) -> str:
        """Generate complete guide content."""
        sections = [
            f"# {self._generate_guide_title(spec_content)}",
            "",
            "## Getting Started",
            self._get_started_section(spec_content),
            "",
            "## Implementation Order",
            f"Implement components in this order: {self._determine_implementation_order(spec_content)}",
            "",
            "## Code Patterns & Conventions",
            self._generate_code_patterns(spec_content),
            "",
            "## Testing Recommendations",
            self._generate_testing_recommendations(spec_content),
        ]
        return "\n".join(sections)


def log_event(context: SDDContext, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the context and display output."""
    context.add_event(f"sdd_{event_type}", details)
    format_output(context, event_type, details)
