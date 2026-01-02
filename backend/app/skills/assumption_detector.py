"""Assumption detection skill."""

from typing import List

from app.core.context import RequestContext
from app.models.spec import Assumption, ConfidenceLevel
from app.skills.base import Skill


class AssumptionDetectorSkill(Skill):
    """
    Detects implicit assumptions in user intent.

    Detection strategy:
    1. Identify missing information (authentication, scale, data persistence)
    2. Detect ambiguous statements
    3. Flag areas needing clarification
    """

    @property
    def name(self) -> str:
        """Return skill name."""
        return "AssumptionDetector"

    def execute(self, context: RequestContext) -> List[Assumption]:
        """
        Detect assumptions from intent.

        Args:
            context: Request context with user intent

        Returns:
            List of detected assumptions
        """
        text = context.intent.text
        assumptions = []

        # Check for authentication assumptions
        assumptions.extend(self._check_auth_assumptions(text))

        # Check for scale assumptions
        assumptions.extend(self._check_scale_assumptions(text))

        # Check for persistence assumptions
        assumptions.extend(self._check_persistence_assumptions(text))

        # Check for platform assumptions
        assumptions.extend(self._check_platform_assumptions(text))

        return assumptions

    def _check_auth_assumptions(self, text: str) -> List[Assumption]:
        """Check for authentication-related assumptions."""
        assumptions = []
        text_lower = text.lower()

        if "user" in text_lower and "auth" not in text_lower and "login" not in text_lower:
            assumptions.append(
                Assumption(
                    description="Authentication mechanism not specified - assuming simple auth",
                    confidence=ConfidenceLevel.MEDIUM,
                    needs_clarification=True,
                )
            )

        return assumptions

    def _check_scale_assumptions(self, text: str) -> List[Assumption]:
        """Check for scale-related assumptions."""
        assumptions = []
        text_lower = text.lower()

        # Single vs multi-user
        if "user" in text_lower and "users" not in text_lower:
            assumptions.append(
                Assumption(
                    description="Single-user system assumed - no multi-tenancy mentioned",
                    confidence=ConfidenceLevel.MEDIUM,
                    needs_clarification=True,
                )
            )

        # Scale not mentioned
        if not any(word in text_lower for word in ["scale", "concurrent", "load", "performance"]):
            assumptions.append(
                Assumption(
                    description="Small-scale system assumed - no performance requirements specified",
                    confidence=ConfidenceLevel.LOW,
                    needs_clarification=False,
                )
            )

        return assumptions

    def _check_persistence_assumptions(self, text: str) -> List[Assumption]:
        """Check for data persistence assumptions."""
        assumptions = []
        text_lower = text.lower()

        if not any(word in text_lower for word in ["database", "persist", "store", "save"]):
            assumptions.append(
                Assumption(
                    description="Data persistence strategy not specified",
                    confidence=ConfidenceLevel.LOW,
                    needs_clarification=True,
                )
            )

        return assumptions

    def _check_platform_assumptions(self, text: str) -> List[Assumption]:
        """Check for platform-related assumptions."""
        assumptions = []
        text_lower = text.lower()

        if not any(word in text_lower for word in ["web", "mobile", "desktop", "api"]):
            assumptions.append(
                Assumption(
                    description="Platform not specified - assuming web application",
                    confidence=ConfidenceLevel.MEDIUM,
                    needs_clarification=False,
                )
            )

        return assumptions
