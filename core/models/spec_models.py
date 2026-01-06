"""Data models for specifications."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Operation(Enum):
    """Supported todo operations."""
    ADD = "add"
    LIST = "list"
    COMPLETE = "complete"
    EXIT = "exit"


@dataclass(frozen=True)
class Specification:
    """
    Structured specification parsed from user input.

    Represents the WHAT (intent) before execution (the HOW).
    """
    operation: Operation
    task_title: Optional[str] = None
    task_id: Optional[int] = None

    def __post_init__(self):
        """Validate specification."""
        if self.operation == Operation.ADD and not self.task_title:
            raise ValueError("ADD operation requires task_title")
        if self.operation == Operation.COMPLETE and self.task_id is None:
            raise ValueError("COMPLETE operation requires task_id")
