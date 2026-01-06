# tests/unit/test_task_model.py

import pytest
from datetime import datetime
from src.task_model import (
    Task,
    TaskStatus,
    Priority,
    OperationType,
    Command,
    CommandResult,
    ValidationError,
    ParseError
)

# T022: Unit tests for Task model
def test_task_creation_valid():
    """Tests successful creation of a Task."""
    now = datetime.now()
    task = Task(
        id=1,
        title="Test Task",
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        created_at=now
    )
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM
    assert task.created_at == now

@pytest.mark.parametrize("invalid_id", [0, -1, "a", None])
def test_task_creation_invalid_id(invalid_id):
    """Tests that creating a Task with an invalid ID raises ValidationError."""
    with pytest.raises(ValidationError, match="Task ID must be a positive integer"):
        Task(
            id=invalid_id,
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            created_at=datetime.now()
        )

@pytest.mark.parametrize("invalid_title", ["", " ", "a" * 201])
def test_task_creation_invalid_title(invalid_title):
    """Tests that creating a Task with an invalid title raises ValidationError."""
    with pytest.raises(ValidationError, match="Task title must be between 1 and 200 characters"):
        Task(
            id=1,
            title=invalid_title,
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            created_at=datetime.now()
        )

def test_task_creation_invalid_enums():
    """Tests that creating a Task with invalid enum values raises ValidationError."""
    with pytest.raises(ValidationError, match="Invalid task status"):
        Task(id=1, title="t", status="invalid", priority=Priority.LOW, created_at=datetime.now())

    with pytest.raises(ValidationError, match="Invalid priority"):
        Task(id=1, title="t", status=TaskStatus.PENDING, priority="invalid", created_at=datetime.now())

# T023: Unit tests for enums
def test_task_status_enum():
    """Tests the values of the TaskStatus enum."""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.COMPLETED.value == "completed"

def test_priority_enum():
    """Tests the values of the Priority enum."""
    assert Priority.HIGH.value == "high"
    assert Priority.MEDIUM.value == "medium"
    assert Priority.LOW.value == "low"

def test_operation_type_enum():
    """Tests the values of the OperationType enum."""
    assert OperationType.ADD.value == "add"
    assert OperationType.LIST.value == "list"
    assert OperationType.COMPLETE.value == "complete"
    assert OperationType.DELETE.value == "delete"
    assert OperationType.UPDATE.value == "update"
    assert OperationType.SEARCH.value == "search"
    assert OperationType.EXIT.value == "exit"

# T024: Unit tests for Command and CommandResult
def test_command_creation():
    """Tests successful creation of a Command."""
    cmd = Command(operation=OperationType.ADD, params={"title": "test"})
    assert cmd.operation == OperationType.ADD
    assert cmd.task_id is None
    assert cmd.params == {"title": "test"}

def test_command_creation_with_id():
    """Tests successful creation of a Command with a task ID."""
    cmd = Command(operation=OperationType.COMPLETE, task_id=5)
    assert cmd.operation == OperationType.COMPLETE
    assert cmd.task_id == 5
    assert cmd.params == {}

def test_command_result_creation():
    """Tests successful creation of a CommandResult."""
    res = CommandResult(success=True, message="Done")
    assert res.success is True
    assert res.message == "Done"
    assert res.data is None

def test_command_result_with_data():
    """Tests successful creation of a CommandResult with data."""
    task = Task(1, "t", TaskStatus.PENDING, Priority.LOW, datetime.now())
    res = CommandResult(success=True, message="Found", data=[task])
    assert res.success is True
    assert res.message == "Found"
    assert res.data == [task]

# Test custom exceptions
def test_parse_error():
    """Tests the ParseError custom exception."""
    with pytest.raises(ParseError) as e:
        raise ParseError("msg", suggestion="try this")
    assert e.value.message == "msg"
    assert e.value.suggestion == "try this"

def test_validation_error():
    """Tests the ValidationError custom exception."""
    with pytest.raises(ValidationError) as e:
        raise ValidationError("msg")
    assert e.value.message == "msg"
