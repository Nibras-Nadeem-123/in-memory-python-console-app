"""Shared domain models for Phase 2.

These models represent the core domain concepts without any
infrastructure or database-specific details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Todo:
    """Todo item - shared domain model.

    This is a pure domain model that can be used across different
    parts of the application without coupling to database or API concerns.

    Attributes:
        id: Unique identifier (None for new todos)
        title: Task title
        description: Optional task details
        status: Current state ('pending' or 'completed')
        created_at: Creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
    """
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
