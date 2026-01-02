"""Unit tests for task models."""

from datetime import datetime

import pytest

from src.task_model import Intent, Operation, Task


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_defaults(self) -> None:
        """Test creating a task with minimal arguments."""
        task = Task(id=1, title="Buy milk")

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.status == "pending"
        assert task.due_date is None
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_all_fields(self) -> None:
        """Test creating a task with all fields."""
        now = datetime.now()
        task = Task(
            id=1,
            title="Buy milk",
            status="pending",
            due_date="tomorrow",
            created_at=now
        )

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.status == "pending"
        assert task.due_date == "tomorrow"
        assert task.created_at == now

    def test_task_status_must_be_valid(self) -> None:
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            Task(id=1, title="Test", status="invalid")

    def test_task_title_cannot_be_empty(self) -> None:
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(id=1, title="")

    def test_task_completed_status(self) -> None:
        """Test creating a completed task."""
        task = Task(id=1, title="Done task", status="completed")

        assert task.status == "completed"


class TestIntent:
    """Tests for the Intent dataclass."""

    def test_intent_add(self) -> None:
        """Test creating an add intent."""
        intent = Intent(action="add", new_title="Buy milk")

        assert intent.action == "add"
        assert intent.target is None
        assert intent.new_title == "Buy milk"
        assert intent.due_date is None

    def test_intent_add_with_due_date(self) -> None:
        """Test creating an add intent with due date."""
        intent = Intent(action="add", new_title="Buy milk", due_date="tomorrow")

        assert intent.action == "add"
        assert intent.new_title == "Buy milk"
        assert intent.due_date == "tomorrow"

    def test_intent_list(self) -> None:
        """Test creating a list intent."""
        intent = Intent(action="list")

        assert intent.action == "list"
        assert intent.target is None
        assert intent.new_title is None

    def test_intent_complete(self) -> None:
        """Test creating a complete intent."""
        intent = Intent(action="complete", target="Buy milk")

        assert intent.action == "complete"
        assert intent.target == "Buy milk"

    def test_intent_update(self) -> None:
        """Test creating an update intent."""
        intent = Intent(action="update", target="Buy milk", new_title="Buy eggs")

        assert intent.action == "update"
        assert intent.target == "Buy milk"
        assert intent.new_title == "Buy eggs"


class TestOperation:
    """Tests for the Operation dataclass."""

    def test_operation_add(self) -> None:
        """Test creating an add operation."""
        task = Task(id=1, title="Test")
        operation = Operation(action="add", task_id=1, before_state=None)

        assert operation.action == "add"
        assert operation.task_id == 1
        assert operation.before_state is None
        assert isinstance(operation.timestamp, datetime)

    def test_operation_complete(self) -> None:
        """Test creating a complete operation with before_state."""
        before = Task(id=1, title="Test", status="pending")
        after = Task(id=1, title="Test", status="completed")

        operation = Operation(action="complete", task_id=1, before_state=before)

        assert operation.action == "complete"
        assert operation.task_id == 1
        assert operation.before_state == before
        assert operation.before_state.status == "pending"
