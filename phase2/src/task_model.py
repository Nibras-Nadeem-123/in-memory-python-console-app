# src/task_model.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# T006: Define enums
class TaskStatus(Enum):
    """Represents the completion state of a task."""
    PENDING = "pending"
    COMPLETED = "completed"

class Priority(Enum):
    """Represents the importance level of a task."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class OperationType(Enum):
    """Represents the type of operation to execute."""
    ADD = "add"
    LIST = "list"
    COMPLETE = "complete"
    DELETE = "delete"
    UPDATE = "update"
    SEARCH = "search"
    EXIT = "exit"
    HELP = "help" # Added for better UX

# T010: Define custom exceptions
class ParseError(Exception):
    """Raised when user input cannot be parsed into a valid Command."""
    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

class ValidationError(Exception):
    """Raised when a command is valid but contains invalid data."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# T007: Define Task dataclass
@dataclass(frozen=True)
class Task:
    """Represents a single todo item in the system."""
    id: int
    title: str
    status: TaskStatus
    priority: Priority
    created_at: datetime

    def __post_init__(self):
        """Validation for the Task dataclass."""
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValidationError("Task ID must be a positive integer.")
        if not self.title or not (1 <= len(self.title) <= 200):
            raise ValidationError("Task title must be between 1 and 200 characters.")
        if not isinstance(self.status, TaskStatus):
            raise ValidationError("Invalid task status.")
        if not isinstance(self.priority, Priority):
            raise ValidationError("Invalid priority.")
        if not isinstance(self.created_at, datetime):
            raise ValidationError("Invalid created_at timestamp.")

# T008: Define Command dataclass
@dataclass(frozen=True)
class Command:
    """Represents a parsed user command ready for execution."""
    operation: OperationType
    task_id: Optional[int] = None
    params: Dict[str, Any] = field(default_factory=dict)

# T009: Define CommandResult dataclass
@dataclass(frozen=True)
class CommandResult:
    """Represents the outcome of executing a command."""
    success: bool
    message: str
    data: Optional[List[Task]] = None