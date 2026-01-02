"""Unit tests for task store."""

import pytest

from src.task_store import (
    AlreadyCompletedError,
    AmbiguousTaskError,
    NoHistoryError,
    TaskNotFoundError,
    TaskStore,
)


class TestTaskStore:
    """Tests for the TaskStore class."""

    def test_initial_state(self) -> None:
        """Test that a new store starts empty."""
        store = TaskStore()

        assert len(store.tasks) == 0
        assert store.history == []

    def test_add_task(self) -> None:
        """Test adding a task."""
        store = TaskStore()

        task = store.add_task("Buy milk")

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.status == "pending"
        assert task.due_date is None
        assert len(store.tasks) == 1
        assert store.tasks[1] == task

    def test_add_task_with_due_date(self) -> None:
        """Test adding a task with due date."""
        store = TaskStore()

        task = store.add_task("Buy milk", due_date="tomorrow")

        assert task.due_date == "tomorrow"

    def test_add_multiple_tasks(self) -> None:
        """Test adding multiple tasks."""
        store = TaskStore()

        task1 = store.add_task("Buy milk")
        task2 = store.add_task("Buy eggs")
        task3 = store.add_task("Buy bread")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        assert len(store.tasks) == 3

    def test_list_tasks_empty(self) -> None:
        """Test listing empty task list."""
        store = TaskStore()

        tasks = store.list_tasks()

        assert tasks == []

    def test_list_tasks_sorted(self) -> None:
        """Test that list returns tasks sorted by ID."""
        store = TaskStore()

        store.add_task("Third")
        store.add_task("First")
        store.add_task("Second")

        tasks = store.list_tasks()

        assert len(tasks) == 3
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[2].id == 3

    def test_find_task_by_title(self) -> None:
        """Test finding a task by title substring."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy eggs")

        task = store.find_task("milk")

        assert task.title == "Buy milk"

    def test_find_task_by_id(self) -> None:
        """Test finding a task by ID reference."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy eggs")

        task = store.find_task("task 1")

        assert task.id == 1
        assert task.title == "Buy milk"

    def test_find_task_by_hash(self) -> None:
        """Test finding a task by #ID reference."""
        store = TaskStore()
        store.add_task("Buy milk")

        task = store.find_task("#1")

        assert task.id == 1

    def test_find_task_not_found(self) -> None:
        """Test that TaskNotFoundError is raised for non-existent task."""
        store = TaskStore()
        store.add_task("Buy milk")

        with pytest.raises(TaskNotFoundError):
            store.find_task("nonexistent")

    def test_find_task_ambiguous(self) -> None:
        """Test that AmbiguousTaskError is raised for multiple matches."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy milk today")

        with pytest.raises(AmbiguousTaskError) as exc_info:
            store.find_task("Buy milk")

        assert "Buy milk" in str(exc_info.value)

    def test_update_task_title(self) -> None:
        """Test updating a task title."""
        store = TaskStore()
        store.add_task("Buy milk")

        updated = store.update_task(1, title="Buy eggs")

        assert updated.title == "Buy eggs"
        assert store.tasks[1].title == "Buy eggs"

    def test_update_task_due_date(self) -> None:
        """Test updating a task due date."""
        store = TaskStore()
        store.add_task("Buy milk")

        updated = store.update_task(1, due_date="tomorrow")

        assert updated.due_date == "tomorrow"

    def test_update_task_not_found(self) -> None:
        """Test that TaskNotFoundError is raised for non-existent task."""
        store = TaskStore()

        with pytest.raises(TaskNotFoundError):
            store.update_task(999, title="New title")

    def test_complete_task(self) -> None:
        """Test completing a task."""
        store = TaskStore()
        store.add_task("Buy milk")

        completed = store.complete_task(1)

        assert completed.status == "completed"
        assert store.tasks[1].status == "completed"

    def test_complete_task_already_completed(self) -> None:
        """Test that AlreadyCompletedError is raised for already completed task."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.complete_task(1)

        with pytest.raises(AlreadyCompletedError):
            store.complete_task(1)

    def test_complete_task_not_found(self) -> None:
        """Test that TaskNotFoundError is raised for non-existent task."""
        store = TaskStore()

        with pytest.raises(TaskNotFoundError):
            store.complete_task(999)

    def test_delete_task(self) -> None:
        """Test deleting a task."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy eggs")

        deleted = store.delete_task(1)

        assert deleted.title == "Buy milk"
        assert len(store.tasks) == 1
        assert 1 not in store.tasks
        assert 2 in store.tasks

    def test_delete_task_not_found(self) -> None:
        """Test that TaskNotFoundError is raised for non-existent task."""
        store = TaskStore()

        with pytest.raises(TaskNotFoundError):
            store.delete_task(999)

    def test_undo_add(self) -> None:
        """Test undoing an add operation."""
        store = TaskStore()
        store.add_task("Buy milk")

        operation = store.undo()

        assert operation.action == "add"
        assert len(store.tasks) == 0

    def test_undo_complete(self) -> None:
        """Test undoing a complete operation."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.complete_task(1)

        operation = store.undo()

        assert operation.action == "complete"
        assert store.tasks[1].status == "pending"

    def test_undo_update(self) -> None:
        """Test undoing an update operation."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.update_task(1, title="Buy eggs")

        operation = store.undo()

        assert operation.action == "update"
        assert store.tasks[1].title == "Buy milk"

    def test_undo_delete(self) -> None:
        """Test undoing a delete operation."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.delete_task(1)

        operation = store.undo()

        assert operation.action == "delete"
        assert len(store.tasks) == 1
        assert store.tasks[1].title == "Buy milk"

    def test_undo_empty_history(self) -> None:
        """Test that NoHistoryError is raised for empty history."""
        store = TaskStore()

        with pytest.raises(NoHistoryError):
            store.undo()

    def test_multiple_undos(self) -> None:
        """Test undoing multiple operations."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy eggs")
        store.complete_task(1)

        store.undo()  # Undo complete
        store.undo()  # Undo add "Buy eggs"

        assert len(store.tasks) == 1
        assert store.tasks[1].status == "pending"

    def test_history_tracked(self) -> None:
        """Test that operations are tracked in history."""
        store = TaskStore()
        store.add_task("Buy milk")
        store.add_task("Buy eggs")
        store.complete_task(1)

        assert len(store.history) == 3
        assert store.history[0].action == "add"
        assert store.history[1].action == "add"
        assert store.history[2].action == "complete"
