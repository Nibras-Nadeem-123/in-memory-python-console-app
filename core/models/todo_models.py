"""Data models for todo domain."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TodoStatus(Enum):
    """Status of a todo item."""
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Todo:
    """
    A todo item.

    Represents domain entity in the execution layer.
    """
    id: int
    title: str
    status: TodoStatus
    created_at: datetime

    def complete(self) -> 'Todo':
        """
        Mark todo as completed.

        Returns a new Todo with completed status (immutable pattern).
        """
        return Todo(
            id=self.id,
            title=self.title,
            status=TodoStatus.COMPLETED,
            created_at=self.created_at
        )

    def __str__(self) -> str:
        """String representation for console display."""
        status_icon = "☑" if self.status == TodoStatus.COMPLETED else "☐"
        return f"[{self.id}] {status_icon} {self.title}"
