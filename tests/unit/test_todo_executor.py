"""Unit tests for todo executor."""

import pytest

from src.task_store import TaskStore
from src.todo_executor import ExecutionResult, TodoExecutor


class TestTodoExecutor:
    """Tests for the TodoExecutor class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = TaskStore()
        self.executor = TodoExecutor(self.store)

    def test_add_task(self) -> None:
        """Test executing add task command."""
        result = self.executor.execute("add task Buy milk")

        assert result.success
        assert "Buy milk" in result.message
        assert result.data is not None
        assert result.data["task"].title == "Buy milk"

    def test_add_task_with_due_date(self) -> None:
        """Test executing add task with due date."""
        result = self.executor.execute("add task Buy milk by tomorrow")

        assert result.success
        assert "Buy milk" in result.message
        assert "tomorrow" in result.message

    def test_add_task_no_title(self) -> None:
        """Test add without title fails."""
        result = self.executor.execute("add task")

        assert not result.success
        assert "title" in result.message.lower()

    def test_list_empty(self) -> None:
        """Test listing empty tasks."""
        result = self.executor.execute("list")

        assert result.success
        assert "No tasks found" in result.message

    def test_list_with_tasks(self) -> None:
        """Test listing tasks."""
        self.executor.execute("add task Buy milk")
        self.executor.execute("add task Buy eggs")

        result = self.executor.execute("list")

        assert result.success
        assert "Buy milk" in result.message
        assert "Buy eggs" in result.message
        assert "[ ]" in result.message  # pending marker

    def test_complete_task(self) -> None:
        """Test completing a task."""
        self.executor.execute("add task Buy milk")

        result = self.executor.execute("complete Buy milk")

        assert result.success
        assert "Completed" in result.message

    def test_complete_task_not_found(self) -> None:
        """Test completing non-existent task."""
        result = self.executor.execute("complete nonexistent")

        assert not result.success
        assert "not found" in result.message.lower()

    def test_complete_task_already_done(self) -> None:
        """Test completing already completed task."""
        self.executor.execute("add task Buy milk")
        self.executor.execute("complete Buy milk")
        # Try again
        result = self.executor.execute("complete Buy milk")

        assert not result.success
        assert "already completed" in result.message.lower()

    def test_update_task(self) -> None:
        """Test updating a task."""
        self.executor.execute("add task Buy milk")

        result = self.executor.execute("update Buy milk to Buy eggs")

        assert result.success
        assert "Buy eggs" in result.message
        assert self.store.tasks[1].title == "Buy eggs"

    def test_update_task_not_found(self) -> None:
        """Test updating non-existent task."""
        result = self.executor.execute("update nonexistent to something")

        assert not result.success
        assert "not found" in result.message.lower()

    def test_delete_task(self) -> None:
        """Test deleting a task."""
        self.executor.execute("add task Buy milk")

        result = self.executor.execute("delete Buy milk")

        assert result.success
        assert "Deleted" in result.message
        assert len(self.store.tasks) == 0

    def test_delete_task_not_found(self) -> None:
        """Test deleting non-existent task."""
        result = self.executor.execute("delete nonexistent")

        assert not result.success
        assert "not found" in result.message.lower()

    def test_undo_add(self) -> None:
        """Test undoing an add operation."""
        self.executor.execute("add task Buy milk")
        assert len(self.store.tasks) == 1

        result = self.executor.execute("undo")

        assert result.success
        assert "Undid" in result.message
        assert len(self.store.tasks) == 0

    def test_undo_complete(self) -> None:
        """Test undoing a complete operation."""
        self.executor.execute("add task Buy milk")
        self.executor.execute("complete Buy milk")
        assert self.store.tasks[1].status == "completed"

        result = self.executor.execute("undo")

        assert result.success
        assert self.store.tasks[1].status == "pending"

    def test_undo_nothing(self) -> None:
        """Test undo with no history."""
        result = self.executor.execute("undo")

        assert not result.success
        assert "Nothing to undo" in result.message

    def test_help(self) -> None:
        """Test help command."""
        result = self.executor.execute("help")

        assert result.success
        assert "Available commands" in result.message
        assert "add" in result.message
        assert "list" in result.message

    def test_exit(self) -> None:
        """Test exit command."""
        result = self.executor.execute("exit")

        assert result.success
        assert "Goodbye" in result.message

    def test_unknown_command(self) -> None:
        """Test unknown command."""
        result = self.executor.execute("frobnicate")

        assert not result.success
        assert "Unknown command" in result.message

    def test_empty_input(self) -> None:
        """Test empty input handling."""
        result = self.executor.execute("")

        assert not result.success
        assert "I didn't understand" in result.message

    def test_task_reference_by_id(self) -> None:
        """Test referencing task by ID."""
        self.executor.execute("add task Buy milk")

        result = self.executor.execute("complete task 1")

        assert result.success
        assert self.store.tasks[1].status == "completed"

    def test_task_reference_by_hash(self) -> None:
        """Test referencing task by #ID."""
        self.executor.execute("add task Buy milk")

        result = self.executor.execute("complete #1")

        assert result.success

    def test_ambiguous_reference(self) -> None:
        """Test ambiguous task reference."""
        self.executor.execute("add task Buy milk")
        self.executor.execute("add task Buy more milk")

        # "Buy" matches both tasks (ambiguous)
        result = self.executor.execute("complete Buy")

        assert not result.success
        assert "Multiple" in result.message or "multiple" in result.message
