"""Console input/output utilities."""

from typing import List

from core.models.todo_models import Todo


class ConsoleUI:
    """Handles console input/output formatting."""

    @staticmethod
    def print_welcome():
        """Display welcome message."""
        print("=" * 60)
        print(" " * 15 + "Phase 1: Spec-Driven Todo")
        print("=" * 60)
        print()
        print("Commands:")
        print("  add task: <title>    - Create new todo")
        print("  list                 - Show all todos")
        print("  complete <id>        - Mark todo as done")
        print("  exit                 - Quit application")
        print()

    @staticmethod
    def print_todos(todos: List[Todo]):
        """
        Display list of todos.

        Args:
            todos: List of todos to display
        """
        if not todos:
            print("No todos yet. Use 'add task: <title>' to create one.")
            return

        print(f"\nTodos ({len(todos)}):")
        print("-" * 60)
        for todo in todos:
            print(f"  {todo}")
        print()

    @staticmethod
    def print_success(message: str):
        """Print success message."""
        print(f"✓ {message}")

    @staticmethod
    def print_error(message: str):
        """Print error message."""
        print(f"✗ {message}")

    @staticmethod
    def read_input() -> str:
        """
        Read input from user.

        Returns:
            User input string
        """
        try:
            return input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            return "exit"
