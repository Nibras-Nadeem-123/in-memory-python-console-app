"""
Orchestration engine for spec generation.

Coordinates the flow from intent to structured specification.
"""

from app.core.context import RequestContext
from app.core.spec_builder import SpecBuilder
from app.models.intent import UserIntent
from app.models.spec import StructuredSpec


class Engine:
    """
    Main orchestrator for spec generation pipeline.

    Delegates to SpecBuilder for actual generation logic.
    """

    def __init__(self) -> None:
        """Initialize engine with spec builder."""
        self.spec_builder = SpecBuilder()

    def execute(self, intent: UserIntent) -> StructuredSpec:
        """
        Execute spec generation pipeline.

        Args:
            intent: User intent input

        Returns:
            Generated structured specification

        Raises:
            ValueError: If intent is invalid or spec cannot be generated
        """
        # Create request context
        context = RequestContext(intent)

        # Build specification
        spec = self.spec_builder.build(context)

        return spec
