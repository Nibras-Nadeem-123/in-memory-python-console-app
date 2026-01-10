"""Custom exceptions for the backend application."""


class TodoNotFoundError(Exception):
    """Raised when todo with specified ID does not exist."""

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"Todo with id {todo_id} not found")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")


class DatabaseError(Exception):
    """Raised when database operation fails."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)
