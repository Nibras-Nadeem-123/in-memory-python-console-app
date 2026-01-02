"""Request-scoped context for spec generation."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from app.models.intent import UserIntent


class RequestContext:
    """
    Request-scoped state container for spec generation.

    Holds the user intent and tracks intermediate processing state.
    Lifecycle: Created per request, discarded after response.
    """

    def __init__(self, intent: UserIntent) -> None:
        """
        Initialize request context.

        Args:
            intent: User intent to process
        """
        self.intent = intent
        self.request_id: UUID = intent.request_id
        self.start_time: datetime = datetime.utcnow()
        self.state: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """
        Store intermediate state.

        Args:
            key: State key
            value: State value
        """
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve intermediate state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            Stored value or default
        """
        return self.state.get(key, default)

    def has(self, key: str) -> bool:
        """
        Check if state key exists.

        Args:
            key: State key to check

        Returns:
            True if key exists
        """
        return key in self.state

    @property
    def elapsed_ms(self) -> float:
        """
        Calculate elapsed processing time in milliseconds.

        Returns:
            Processing time in milliseconds
        """
        delta = datetime.utcnow() - self.start_time
        return delta.total_seconds() * 1000.0
