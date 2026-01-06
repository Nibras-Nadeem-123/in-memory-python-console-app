# tests/unit/test_todo_utils.py

import pytest
from datetime import datetime
from src.task_model import Task, TaskStatus, Priority
from src.todo_utils import (
    format_task,
    format_task_list,
    validate_title,
    normalize_text,
)

@pytest.fixture
def pending_task() -> Task:
    """Provides a sample pending task."""
    return Task(
        id=1,
        title="Write tests",
        status=TaskStatus.PENDING,
        priority=Priority.HIGH,
        created_at=datetime(2025, 1, 1)
    )

@pytest.fixture
def completed_task() -> Task:
    """Provides a sample completed task."""
    return Task(
        id=2,
        title="Deploy feature",
        status=TaskStatus.COMPLETED,
        priority=Priority.MEDIUM,
        created_at=datetime(2025, 1, 2)
    )

# T028: Unit tests for utilities
def test_format_task_pending(pending_task: Task):
    """Tests formatting for a pending task."""
    expected = "[1] ☐ Write tests (HIGH) - 2025-01-01"
    assert format_task(pending_task) == expected

def test_format_task_completed(completed_task: Task):
    """Tests formatting for a completed task."""
    expected = "[2] ☑ Deploy feature (MEDIUM) - 2025-01-02"
    assert format_task(completed_task) == expected

def test_format_task_list_empty():
    """Tests formatting an empty list of tasks."""
    assert format_task_list([]) == "No tasks found."

def test_format_task_list_multiple(pending_task: Task, completed_task: Task):
    """Tests formatting a list of multiple tasks."""
    tasks = [pending_task, completed_task]
    expected_header = "Found 2 tasks:\n"
    expected_task1 = "[1] ☐ Write tests (HIGH) - 2025-01-01"
    expected_task2 = "[2] ☑ Deploy feature (MEDIUM) - 2025-01-02"
    
    formatted_list = format_task_list(tasks)
    
    assert formatted_list.startswith(expected_header)
    assert expected_task1 in formatted_list
    assert expected_task2 in formatted_list

@pytest.mark.parametrize("title, is_valid", [
    ("This is a valid title", True),
    ("a", True),
    ("a" * 200, True),
    ("", False),
    ("   ", False),
    ("a" * 201, False),
])
def test_validate_title(title: str, is_valid: bool):
    """Tests the title validation logic."""
    assert validate_title(title) == is_valid

@pytest.mark.parametrize("input_text, expected_text", [
    ("  Some Text  ", "some text"),
    ("ANOTHER TEXT", "another text"),
    ("  MixedCase Text ", "mixedcase text"),
    ("text", "text"),
])
def test_normalize_text(input_text: str, expected_text: str):
    """Tests the text normalization logic."""
    assert normalize_text(input_text) == expected_text
