"""
Core intelligence framework primitives.

Provides foundational types and enumerations for task management,
workflow stages, and execution states.
"""

from .task_stage import TaskStage
from .task_state import TaskState

__all__ = [
    "TaskStage",
    "TaskState",
]
