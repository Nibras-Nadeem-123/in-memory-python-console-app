"""SDD-specific error handling.

Custom exceptions for Spec-Driven Development stages.
"""


class SDDError(Exception):
    """Base exception for SDD-related errors."""
    pass


class IntentParsingError(SDDError):
    """Raised when intent parsing fails."""

    def __init__(self, message: str, text: str = ""):
        self.message = message
        self.text = text
        super().__init__(self.message)


class SpecGenerationError(SDDError):
    """Raised when specification generation fails."""

    def __init__(self, message: str, intent_type: str = ""):
        self.message = message
        self.intent_type = intent_type
        super().__init__(self.message)


class PlanGenerationError(SDDError):
    """Raised when plan generation fails."""

    def __init__(self, message: str, spec_id: str = ""):
        self.message = message
        self.spec_id = spec_id
        super().__init__(self.message)


class GuideGenerationError(SDDError):
    """Raised when guide generation fails."""

    def __init__(self, message: str, plan_id: str = ""):
        self.message = message
        self.plan_id = plan_id
        super().__init__(self.message)


class WorkflowError(SDDError):
    """Raised when workflow execution fails."""

    def __init__(self, message: str, stage: str = ""):
        self.message = message
        self.stage = stage
        super().__init__(self.message)


class ValidationError(SDDError):
    """Raised when artifact validation fails."""

    def __init__(self, message: str, artifact_type: str = ""):
        self.message = message
        self.artifact_type = artifact_type
        super().__init__(self.message)


class AmbiguityError(SDDError):
    """Raised when ambiguous input is detected."""

    def __init__(self, message: str, ambiguities: list = None):
        self.message = message
        self.ambiguities = ambiguities or []
        super().__init__(self.message)


class CircularDependencyError(SDDError):
    """Raised when circular task dependencies are detected."""

    def __init__(self, message: str, cycles: list = None):
        self.message = message
        self.cycles = cycles or []
        super().__init__(self.message)
