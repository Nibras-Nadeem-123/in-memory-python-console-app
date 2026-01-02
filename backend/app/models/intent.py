"""User intent input models."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class UserIntent(BaseModel):
    """Natural language user intent input."""

    text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Natural language description of desired system (50-500 words)",
    )
    request_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this request",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the intent was submitted",
    )

    @field_validator("text")
    @classmethod
    def validate_word_count(cls, v: str) -> str:
        """Validate word count is between 50 and 500 words."""
        words = len(v.split())
        if words < 50:
            raise ValueError(f"Text must contain at least 50 words. Received: {words} words.")
        if words > 500:
            raise ValueError(f"Text must contain at most 500 words. Received: {words} words.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag.",
            }
        }
    }
