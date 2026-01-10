from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    """Todo item stored in database.

    Attributes:
        id: Auto-incrementing primary key
        title: Task title (required, 1-200 characters)
        description: Optional task details (max 1000 characters)
        status: Current state ('pending' or 'completed')
        created_at: Creation timestamp in UTC
        updated_at: Last update timestamp in UTC
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoBase(SQLModel):
    """Base fields for Todo."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""
    pass


class TodoUpdate(TodoBase):
    """Schema for updating an existing todo.

    All fields are optional - only provided fields are updated.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = None


class TodoResponse(SQLModel):
    """Schema for todo response from API."""
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class TodoStatusUpdate(SQLModel):
    """Schema for updating todo status only."""
    status: str
