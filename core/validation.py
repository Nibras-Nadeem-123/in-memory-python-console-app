"""Validation rules for shared domain models.

These validation rules can be used across different parts of the application
to ensure data consistency.
"""

from typing import List
from core.models import Todo


def validate_todo(todo: Todo) -> List[str]:
    """Validate a Todo object.

    Args:
        todo: Todo object to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate title
    if not todo.title or not todo.title.strip():
        errors.append("Title is required")
    elif len(todo.title) > 200:
        errors.append("Title must be at most 200 characters")

    # Validate description
    if todo.description and len(todo.description) > 1000:
        errors.append("Description must be at most 1000 characters")

    # Validate status
    if todo.status not in ['pending', 'completed']:
        errors.append("Status must be 'pending' or 'completed'")

    return errors
