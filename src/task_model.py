"""Data models for the todo system.

Defines Task, Intent, and Operation as pure data containers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique internal identifier (never reused).
        title: Task description.
        status: Either "pending" or "completed".
        due_date: Optional natural language due date.
        created_at: Timestamp of task creation.
    """
    id: int
    title: str
    status: str = "pending"
    due_date: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task state after initialization."""
        if not self.title:
            raise ValueError("Task title cannot be empty")
        if self.status not in ("pending", "completed"):
            raise ValueError(f"Invalid status: {self.status}. Must be 'pending' or 'completed'")


@dataclass
class Intent:
    """Parsed representation of a user command.

    Attributes:
        action: The command action (add, list, update, complete, delete, undo, help, exit).
        target: Task reference for targeted actions (title substring or ID).
        new_title: New title for add/update actions.
        due_date: Due date for add/update actions.
    """
    action: str
    target: Optional[str] = None
    new_title: Optional[str] = None
    due_date: Optional[str] = None


@dataclass
class Operation:
    """Records a state-changing operation for undo support.

    Attributes:
        action: The action type that was performed.
        task_id: The ID of the affected task (None for add).
        before_state: Snapshot of task state before operation (None for add).
        timestamp: When the operation occurred.
    """
    action: str
    task_id: Optional[int]
    before_state: Optional[Task]
    timestamp: datetime = field(default_factory=datetime.now)
