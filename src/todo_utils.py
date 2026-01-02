"""Utility functions for the todo system.

Provides helper functions for formatting and date handling.
"""

from typing import Optional


def format_task_list(tasks: list, show_ids: bool = True) -> str:
    """Format a list of tasks for display.

    Args:
        tasks: List of Task objects.
        show_ids: Whether to show task IDs.

    Returns:
        Formatted string representation.
    """
    if not tasks:
        return "No tasks found"

    lines = []
    for task in tasks:
        status_marker = "[x]" if task.status == "completed" else "[ ]"

        if show_ids:
            line = f"{status_marker} #{task.id}: {task.title}"
        else:
            line = f"{status_marker} {task.title}"

        if task.due_date:
            line += f" (due: {task.due_date})"

        lines.append(line)

    return "\n".join(lines)


def format_single_task(task, show_id: bool = True) -> str:
    """Format a single task for display.

    Args:
        task: Task object.
        show_id: Whether to show task ID.

    Returns:
        Formatted string representation.
    """
    status_marker = "[x]" if task.status == "completed" else "[ ]"

    if show_id:
        base = f"{status_marker} #{task.id}: {task.title}"
    else:
        base = f"{status_marker} {task.title}"

    if task.due_date:
        base += f" (due: {task.due_date})"

    return base


def extract_due_date(text: str) -> tuple[str, Optional[str]]:
    """Extract due date from text.

    Looks for patterns like "by Friday", "by tomorrow", "due Jan 15".

    Args:
        text: The text to search.

    Returns:
        Tuple of (cleaned_text, due_date_or_None).
    """
    import re

    # Patterns for due date extraction
    due_patterns = [
        r"\s+by\s+(.+)$",
        r"\s+due\s+(.+)$",
        r"\s+due\s+date\s+(.+)$",
        r"\s+on\s+(.+)$",
    ]

    for pattern in due_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            due_date = match.group(1).strip()
            cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            return cleaned, due_date

    return text, None


def parse_task_reference(reference: str) -> dict:
    """Parse a task reference into components.

    Args:
        reference: The reference string (e.g., "task 1", "#1", "buy milk").

    Returns:
        Dictionary with type and value.
    """
    import re

    reference = reference.strip()

    # Check for "task X" format
    task_match = re.match(r"^task\s+(\d+)$", reference, re.IGNORECASE)
    if task_match:
        return {"type": "id", "value": int(task_match.group(1))}

    # Check for "#X" format
    hash_match = re.match(r"^#(\d+)$", reference, re.IGNORECASE)
    if hash_match:
        return {"type": "id", "value": int(hash_match.group(1))}

    # Default to title search
    return {"type": "title", "value": reference}
