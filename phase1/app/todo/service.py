"""Todo service layer - business logic and state management."""

from datetime import datetime
from typing import Dict, List, Optional

from .models import Todo, TodoStatus


class TodoNotFoundError(Exception):
    """Raised when a todo with given ID does not exist."""
    pass


class TodoService:
    """
    Manages todo state and operations.

    This is the EXECUTION layer - performs actions based on specifications.
    """

    def __init__(self):
        """Initialize with empty todo list."""
        self._todos: Dict[int, Todo] = {}
        self._next_id: int = 1

    def add_todo(self, title: str) -> Todo:
        """
        Create a new todo.

        Args:
            title: Todo title

        Returns:
            Created todo with assigned ID
        """
        todo = Todo(
            id=self._next_id,
            title=title,
            status=TodoStatus.PENDING,
            created_at=datetime.now()
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get_all_todos(self) -> List[Todo]:
        """
        Get all todos sorted by ID.

        Returns:
            List of all todos
        """
        return sorted(self._todos.values(), key=lambda t: t.id)

    def complete_todo(self, todo_id: int) -> Todo:
        """
        Mark a todo as completed.

        Args:
            todo_id: ID of todo to complete

        Returns:
            Updated todo

        Raises:
            TodoNotFoundError: If todo doesn't exist
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(f"Todo #{todo_id} not found")

        todo = self._todos[todo_id]
        completed_todo = todo.complete()
        self._todos[todo_id] = completed_todo
        return completed_todo

    def count(self) -> int:
        """Get total number of todos."""
        return len(self._todos)
