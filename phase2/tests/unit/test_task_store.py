# tests/unit/test_task_store.py

import pytest
from datetime import datetime
from src.task_store import TaskStore
from src.task_model import Task, TaskStatus, Priority

@pytest.fixture
def store() -> TaskStore:
    """Provides a clean TaskStore instance for each test."""
    return TaskStore()

@pytest.fixture
def sample_task() -> Task:
    """Provides a sample task for testing."""
    # The ID is a placeholder, as the store will assign a new one.
    return Task(id=999, title="Test Task", status=TaskStatus.PENDING, priority=Priority.MEDIUM, created_at=datetime.now())

# T025: Unit tests for TaskStore.add()
def test_add_task(store: TaskStore, sample_task: Task):
    """Tests adding a single task and that it gets assigned ID 1."""
    task_id = store.add(sample_task)
    assert task_id == 1
    assert store.count() == 1
    
    retrieved_task = store.get(task_id)
    assert retrieved_task is not None
    assert retrieved_task.id == 1
    assert retrieved_task.title == sample_task.title

def test_add_multiple_tasks_sequential_ids(store: TaskStore, sample_task: Task):
    """Tests that adding multiple tasks results in sequential IDs."""
    task_id_1 = store.add(sample_task)
    task_id_2 = store.add(sample_task)
    task_id_3 = store.add(sample_task)
    
    assert task_id_1 == 1
    assert task_id_2 == 2
    assert task_id_3 == 3
    assert store.count() == 3

# T026: Unit tests for TaskStore.get()
def test_get_task_found(store: TaskStore, sample_task: Task):
    """Tests retrieving a task that exists."""
    task_id = store.add(sample_task)
    retrieved_task = store.get(task_id)
    assert retrieved_task is not None
    assert retrieved_task.id == task_id

def test_get_task_not_found(store: TaskStore):
    """Tests that getting a non-existent task returns None."""
    assert store.get(123) is None

# T027: Unit tests for TaskStore CRUD operations
def test_get_all_tasks(store: TaskStore, sample_task: Task):
    """Tests retrieving all tasks."""
    store.add(sample_task)
    store.add(sample_task)
    
    all_tasks = store.get_all()
    assert len(all_tasks) == 2
    assert all_tasks[0].id == 1
    assert all_tasks[1].id == 2

def test_get_all_empty(store: TaskStore):
    """Tests get_all on an empty store."""
    assert store.get_all() == []

def test_update_task_found(store: TaskStore, sample_task: Task):
    """Tests updating an existing task."""
    task_id = store.add(sample_task)
    
    updated_task = Task(
        id=task_id,
        title="Updated Title",
        status=TaskStatus.COMPLETED,
        priority=Priority.HIGH,
        created_at=sample_task.created_at
    )
    
    result = store.update(task_id, updated_task)
    assert result is True
    
    retrieved_task = store.get(task_id)
    assert retrieved_task is not None
    assert retrieved_task.title == "Updated Title"
    assert retrieved_task.status == TaskStatus.COMPLETED
    assert retrieved_task.priority == Priority.HIGH

def test_update_task_not_found(store: TaskStore, sample_task: Task):
    """Tests that updating a non-existent task fails."""
    assert store.update(123, sample_task) is False

def test_delete_task_found(store: TaskStore, sample_task: Task):
    """Tests deleting an existing task."""
    task_id = store.add(sample_task)
    assert store.count() == 1
    
    result = store.delete(task_id)
    assert result is True
    assert store.count() == 0
    assert store.get(task_id) is None

def test_delete_task_not_found(store: TaskStore):
    """Tests that deleting a non-existent task fails."""
    assert store.delete(123) is False

# Additional tests for full coverage
def test_count(store: TaskStore, sample_task: Task):
    """Tests the count method."""
    assert store.count() == 0
    store.add(sample_task)
    assert store.count() == 1
    store.add(sample_task)
    assert store.count() == 2

def test_filter_by_status(store: TaskStore, sample_task: Task):
    """Tests filtering tasks by their status."""
    task1 = Task(id=0, title="T1", status=TaskStatus.PENDING, priority=Priority.LOW, created_at=datetime.now())
    task2 = Task(id=0, title="T2", status=TaskStatus.COMPLETED, priority=Priority.LOW, created_at=datetime.now())
    task3 = Task(id=0, title="T3", status=TaskStatus.PENDING, priority=Priority.LOW, created_at=datetime.now())
    store.add(task1)
    store.add(task2)
    store.add(task3)

    pending_tasks = store.filter_by_status(TaskStatus.PENDING)
    completed_tasks = store.filter_by_status(TaskStatus.COMPLETED)

    assert len(pending_tasks) == 2
    assert pending_tasks[0].id == 1
    assert pending_tasks[1].id == 3
    
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == 2

def test_search(store: TaskStore, sample_task: Task):
    """Tests searching for tasks by title keyword."""
    task1 = Task(id=0, title="Documentation for API", status=TaskStatus.PENDING, priority=Priority.LOW, created_at=datetime.now())
    task2 = Task(id=0, title="Write unit tests", status=TaskStatus.PENDING, priority=Priority.LOW, created_at=datetime.now())
    task3 = Task(id=0, title="Document the new feature", status=TaskStatus.PENDING, priority=Priority.LOW, created_at=datetime.now())
    store.add(task1)
    store.add(task2)
    store.add(task3)

    search_results = store.search("doc")
    assert len(search_results) == 2
    assert search_results[0].id == 1
    assert search_results[1].id == 3

    search_results_case = store.search("API")
    assert len(search_results_case) == 1
    assert search_results_case[0].id == 1

    search_no_match = store.search("xyz")
    assert len(search_no_match) == 0