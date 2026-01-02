"""Application context - holds state and dependencies."""

from app.spec.parser import SpecParser
from app.todo.service import TodoService


class AppContext:
    """
    Application context holding dependencies and state.

    Separates initialization from execution.
    """

    def __init__(self):
        """Initialize context with parser and service."""
        self.parser = SpecParser()
        self.todo_service = TodoService()
