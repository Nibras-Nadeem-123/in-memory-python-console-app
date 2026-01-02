"""
Execution engine - orchestrates the flow from specification to execution.

This demonstrates the spec-driven pattern:
  Input → [Parser: SPEC] → [Engine: EXECUTION] → Output
"""

from app.context import AppContext
from app.spec.models import Operation, Specification
from app.spec.parser import ParseError
from app.todo.service import TodoNotFoundError
from app.utils.console import ConsoleUI


class Engine:
    """
    Orchestrates specification execution.

    Receives structured specifications and delegates to appropriate handlers.
    """

    def __init__(self, context: AppContext):
        """
        Initialize engine with application context.

        Args:
            context: Application context with dependencies
        """
        self.context = context
        self.ui = ConsoleUI()

    def execute_specification(self, spec: Specification) -> bool:
        """
        Execute a specification.

        Args:
            spec: Parsed specification to execute

        Returns:
            True to continue REPL, False to exit
        """
        try:
            if spec.operation == Operation.EXIT:
                return False

            elif spec.operation == Operation.ADD:
                self._handle_add(spec)

            elif spec.operation == Operation.LIST:
                self._handle_list()

            elif spec.operation == Operation.COMPLETE:
                self._handle_complete(spec)

            return True

        except TodoNotFoundError as e:
            self.ui.print_error(str(e))
            return True

        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            return True

    def _handle_add(self, spec: Specification):
        """Handle ADD operation."""
        todo = self.context.todo_service.add_todo(spec.task_title)
        self.ui.print_success(f"Todo #{todo.id} created: '{todo.title}'")

    def _handle_list(self):
        """Handle LIST operation."""
        todos = self.context.todo_service.get_all_todos()
        self.ui.print_todos(todos)

    def _handle_complete(self, spec: Specification):
        """Handle COMPLETE operation."""
        todo = self.context.todo_service.complete_todo(spec.task_id)
        self.ui.print_success(f"Todo #{todo.id} marked as completed")
