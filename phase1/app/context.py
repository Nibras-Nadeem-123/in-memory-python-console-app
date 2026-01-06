"""Application context - holds state and dependencies."""

from phase1.app.spec.parser import SpecParser
from core.services.todo_service import TodoService


class AppContext:
    """
    Application context holding dependencies and state.

    Separates initialization from execution.
    """

    def __init__(self):
        """Initialize context with parser and service."""
        self.parser = SpecParser()
        self.todo_service = TodoService()
