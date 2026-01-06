# src/todo_utils.py

from typing import List
from src.task_model import Task, TaskStatus

def format_task(task: Task) -> str:
    """
    Formats a single task for display.
    Example: "[1] ☐ Write tests (HIGH) - 2025-12-31"
    """
    status_symbol = "☑" if task.status == TaskStatus.COMPLETED else "☐"
    return (
        f"[{task.id}] {status_symbol} {task.title} "
        f"({task.priority.value.upper()}) - {task.created_at.strftime('%Y-%m-%d')}"
    )

def format_task_list(tasks: List[Task]) -> str:
    """Formats a list of tasks for display with headers."""
    if not tasks:
        return "No tasks found."
    
    count = len(tasks)
    header = f"Found {count} task{'s' if count > 1 else ''}:\n"
    
    return header + "\n".join(format_task(task) for task in tasks)

def validate_title(title: str) -> bool:
    """
    Checks if a title is valid (1-200 chars, non-empty after stripping).
    """
    return 1 <= len(title.strip()) <= 200

def normalize_text(text: str) -> str:
    """
    Normalizes text by converting to lowercase and stripping whitespace.
    """
    return text.lower().strip()
