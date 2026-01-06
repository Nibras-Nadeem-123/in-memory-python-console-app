# tests/unit/test_todo_executor.py

import pytest
from src.todo_executor import TodoExecutor
from src.task_store import TaskStore
from src.task_model import Command, OperationType, Priority, TaskStatus

@pytest.fixture
def store() -> TaskStore:
    """Provides a clean TaskStore instance for each test."""
    return TaskStore()

@pytest.fixture
def executor(store: TaskStore) -> TodoExecutor:
    """Provides a TodoExecutor instance using the clean store."""
    return TodoExecutor(store)

# T046: Test for execute ADD command
def test_execute_add_command(executor: TodoExecutor, store: TaskStore):
    """Tests that an ADD command creates a task in the store."""
    command = Command(
        operation=OperationType.ADD,
        params={"title": "test task", "priority": Priority.MEDIUM}
    )
    result = executor.execute(command)

    assert result.success is True
    assert "Task #1 created" in result.message
    assert store.count() == 1
    
    task = store.get(1)
    assert task is not None
    assert task.title == "test task"
    assert task.priority == Priority.MEDIUM
    assert task.status == TaskStatus.PENDING

# T049: Test for ADD with different priorities
@pytest.mark.parametrize("priority_enum, priority_str", [
    (Priority.HIGH, "HIGH"),
    (Priority.LOW, "LOW"),
])
def test_execute_add_with_priority(executor: TodoExecutor, store: TaskStore, priority_enum, priority_str):
    """Tests ADD command with various priorities."""
    command = Command(
        operation=OperationType.ADD,
        params={"title": "priority test", "priority": priority_enum}
    )
    result = executor.execute(command)
    
    assert result.success is True
    assert f"(priority: {priority_str})" in result.message
    
    task = store.get(1)
    assert task is not None
    assert task.priority == priority_enum

# T047: Test for execute LIST command
def test_execute_list_command(executor: TodoExecutor, store: TaskStore):
    """Tests that a LIST command returns tasks from the store."""
    # Add some tasks first
    add_cmd1 = Command(operation=OperationType.ADD, params={"title": "t1", "priority": Priority.LOW})
    add_cmd2 = Command(operation=OperationType.ADD, params={"title": "t2", "priority": Priority.HIGH})
    executor.execute(add_cmd1)
    executor.execute(add_cmd2)

    list_cmd = Command(operation=OperationType.LIST)
    result = executor.execute(list_cmd)

    assert result.success is True
    assert result.data is not None
    assert len(result.data) == 2
    assert result.data[0].title == "t1"
    assert result.data[1].title == "t2"

def test_execute_list_empty(executor: TodoExecutor):
    """Tests that LIST on an empty store returns an empty list."""
    list_cmd = Command(operation=OperationType.LIST)
    result = executor.execute(list_cmd)
    
    assert result.success is True
    assert result.data == []

# T077 & T078: Test for execute LIST with filters
def test_execute_list_with_filters(executor: TodoExecutor, store: TaskStore):
    """Tests that LIST command works with status filters."""
    # Add one pending and one completed task
    executor.execute(Command(operation=OperationType.ADD, params={"title": "pending task", "priority": Priority.LOW}))
    executor.execute(Command(operation=OperationType.ADD, params={"title": "completed task", "priority": Priority.LOW}))
    executor.execute(Command(operation=OperationType.COMPLETE, task_id=2))
    
    # Test 'pending' filter
    pending_cmd = Command(operation=OperationType.LIST, params={"status_filter": "pending"})
    pending_result = executor.execute(pending_cmd)
    assert pending_result.success is True
    assert len(pending_result.data) == 1
    assert pending_result.data[0].id == 1
    assert pending_result.data[0].status == TaskStatus.PENDING

    # Test 'completed' filter
    completed_cmd = Command(operation=OperationType.LIST, params={"status_filter": "completed"})
    completed_result = executor.execute(completed_cmd)
    assert completed_result.success is True
    assert len(completed_result.data) == 1
    assert completed_result.data[0].id == 2
    assert completed_result.data[0].status == TaskStatus.COMPLETED

# T079: Test for execute SEARCH command
def test_execute_search_command(executor: TodoExecutor, store: TaskStore):
    """Tests that a SEARCH command returns matching tasks."""
    executor.execute(Command(operation=OperationType.ADD, params={"title": "first task with keyword", "priority": Priority.LOW}))
    executor.execute(Command(operation=OperationType.ADD, params={"title": "second task", "priority": Priority.LOW}))
    executor.execute(Command(operation=OperationType.ADD, params={"title": "another keyword task", "priority": Priority.LOW}))

    # Search with matches
    search_cmd = Command(operation=OperationType.SEARCH, params={"query": "keyword"})
    result = executor.execute(search_cmd)
    assert result.success is True
    assert "Found 2 tasks" in result.message
    assert len(result.data) == 2
    assert result.data[0].id == 1
    assert result.data[1].id == 3

    # Search with no matches
    search_no_match_cmd = Command(operation=OperationType.SEARCH, params={"query": "xyz"})
    result_no_match = executor.execute(search_no_match_cmd)
    assert result_no_match.success is True
    assert "Found 0 tasks" in result_no_match.message
    assert len(result_no_match.data) == 0

# T048 & T050: Test for execute COMPLETE command (success and error cases)
def test_execute_complete_command(executor: TodoExecutor, store: TaskStore):
    """Tests successfully completing a task."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "task to complete", "priority": Priority.MEDIUM})
    executor.execute(add_cmd) # Task ID is 1
    
    complete_cmd = Command(operation=OperationType.COMPLETE, task_id=1)
    result = executor.execute(complete_cmd)

    assert result.success is True
    assert "marked as completed" in result.message
    
    task = store.get(1)
    assert task is not None
    assert task.status == TaskStatus.COMPLETED

def test_execute_complete_not_found(executor: TodoExecutor):
    """Tests completing a task that does not exist."""
    complete_cmd = Command(operation=OperationType.COMPLETE, task_id=999)
    result = executor.execute(complete_cmd)
    
    assert result.success is False
    assert "not found" in result.message

def test_execute_complete_already_completed(executor: TodoExecutor):
    """Tests completing a task that is already complete."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "t", "priority": Priority.LOW})
    executor.execute(add_cmd) # Task ID is 1
    
    # Complete it once
    executor.execute(Command(operation=OperationType.COMPLETE, task_id=1))
    
    # Try to complete it again
    result = executor.execute(Command(operation=OperationType.COMPLETE, task_id=1))
    
    assert result.success is False
    assert "is already completed" in result.message

# Test for HELP command
def test_execute_help_command(executor: TodoExecutor):
    """Tests that the HELP command returns a help message."""
    help_cmd = Command(operation=OperationType.HELP)
    result = executor.execute(help_cmd)
    
    assert result.success is True
    assert "Available commands" in result.message

# T094: Test for execute DELETE command
def test_execute_delete_command(executor: TodoExecutor, store: TaskStore):
    """Tests successfully deleting a task."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "task to delete", "priority": Priority.MEDIUM})
    executor.execute(add_cmd) # Task ID is 1
    
    assert store.count() == 1
    delete_cmd = Command(operation=OperationType.DELETE, task_id=1)
    result = executor.execute(delete_cmd)
    
    assert result.success is True
    assert "deleted" in result.message
    assert store.count() == 0
    assert store.get(1) is None

def test_execute_delete_not_found(executor: TodoExecutor):
    """Tests deleting a task that does not exist."""
    delete_cmd = Command(operation=OperationType.DELETE, task_id=999)
    result = executor.execute(delete_cmd)
    
    assert result.success is False
    assert "not found" in result.message

# T095, T096, T097: Test for execute UPDATE command
def test_execute_update_title(executor: TodoExecutor, store: TaskStore):
    """Tests successfully updating a task's title."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "original title", "priority": Priority.MEDIUM})
    executor.execute(add_cmd) # Task ID is 1

    update_cmd = Command(operation=OperationType.UPDATE, task_id=1, params={"title": "new title"})
    result = executor.execute(update_cmd)

    assert result.success is True
    assert "title changed to 'new title'" in result.message
    task = store.get(1)
    assert task is not None
    assert task.title == "new title"

def test_execute_update_priority(executor: TodoExecutor, store: TaskStore):
    """Tests successfully updating a task's priority."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "task", "priority": Priority.MEDIUM})
    executor.execute(add_cmd) # Task ID is 1

    update_cmd = Command(operation=OperationType.UPDATE, task_id=1, params={"priority": Priority.HIGH})
    result = executor.execute(update_cmd)

    assert result.success is True
    assert "priority changed to HIGH" in result.message
    task = store.get(1)
    assert task is not None
    assert task.priority == Priority.HIGH

def test_execute_update_title_and_priority(executor: TodoExecutor, store: TaskStore):
    """Tests successfully updating both title and priority."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "old title", "priority": Priority.LOW})
    executor.execute(add_cmd) # Task ID is 1

    update_cmd = Command(
        operation=OperationType.UPDATE,
        task_id=1,
        params={"title": "new title", "priority": Priority.HIGH}
    )
    result = executor.execute(update_cmd)

    assert result.success is True
    assert "title changed to 'new title'" in result.message
    assert "priority changed to HIGH" in result.message
    task = store.get(1)
    assert task is not None
    assert task.title == "new title"
    assert task.priority == Priority.HIGH

def test_execute_update_not_found(executor: TodoExecutor):
    """Tests updating a task that does not exist."""
    update_cmd = Command(operation=OperationType.UPDATE, task_id=999, params={"title": "new title"})
    result = executor.execute(update_cmd)
    
    assert result.success is False
    assert "not found" in result.message

def test_execute_update_no_changes(executor: TodoExecutor, store: TaskStore):
    """Tests updating a task with no actual changes."""
    add_cmd = Command(operation=OperationType.ADD, params={"title": "task", "priority": Priority.MEDIUM})
    executor.execute(add_cmd) # Task ID is 1

    update_cmd = Command(operation=OperationType.UPDATE, task_id=1, params={}) # Empty params
    result = executor.execute(update_cmd)

    assert result.success is False
    assert "No changes specified" in result.message