# tests/integration/test_todo_workflows.py

import pytest
from src.input_parser import InputParser
from src.todo_executor import TodoExecutor
from src.task_store import TaskStore
from src.task_model import TaskStatus, Priority

@pytest.fixture
def parser() -> InputParser:
    return InputParser()

@pytest.fixture
def store() -> TaskStore:
    return TaskStore()

@pytest.fixture
def executor(store: TaskStore) -> TodoExecutor:
    return TodoExecutor(store)

# T057: Test complete workflow: add -> list -> complete
def test_full_workflow_add_list_complete(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # 1. Add 3 tasks
    cmd1 = parser.parse("add task: Task 1")
    res1 = executor.execute(cmd1)
    assert res1.success
    
    cmd2 = parser.parse("add task: Task 2")
    res2 = executor.execute(cmd2)
    assert res2.success
    
    cmd3 = parser.parse("add task: Task 3")
    res3 = executor.execute(cmd3)
    assert res3.success
    
    assert store.count() == 3

    # 2. List tasks
    list_cmd = parser.parse("list tasks")
    list_res = executor.execute(list_cmd)
    assert list_res.success
    assert len(list_res.data) == 3

    # 3. Complete one task
    complete_cmd = parser.parse("complete task 2")
    complete_res = executor.execute(complete_cmd)
    assert complete_res.success
    assert "marked as completed" in complete_res.message

    # 4. Verify state changes
    task1 = store.get(1)
    task2 = store.get(2)
    task3 = store.get(3)

    assert task1.status == TaskStatus.PENDING
    assert task2.status == TaskStatus.COMPLETED
    assert task3.status == TaskStatus.PENDING

# T058: Test workflow for adding with priority
def test_workflow_add_with_priority(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Add a task with high priority
    cmd = parser.parse("add task: High prio task with priority high")
    res = executor.execute(cmd)
    assert res.success

    # Verify it was stored correctly
    task = store.get(1)
    assert task is not None
    assert task.priority == Priority.HIGH
    assert store.count() == 1

# T059: Test workflow for an empty list
def test_workflow_empty_list(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Ensure store is empty
    assert store.count() == 0

    # List tasks
    list_cmd = parser.parse("list tasks")
    list_res = executor.execute(list_cmd)

    assert list_res.success
    assert list_res.data == []

# T080: Test workflow for filtering by status
def test_workflow_filter_by_status(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Add 5 tasks
    for i in range(5):
        executor.execute(parser.parse(f"add task: Task {i+1}"))
    
    # Complete tasks 2 and 4
    executor.execute(parser.parse("complete task 2"))
    executor.execute(parser.parse("complete task 4"))
    
    # Filter by pending
    pending_res = executor.execute(parser.parse("list pending tasks"))
    assert pending_res.success
    assert len(pending_res.data) == 3
    pending_ids = {task.id for task in pending_res.data}
    assert pending_ids == {1, 3, 5}

    # Filter by completed
    completed_res = executor.execute(parser.parse("list completed tasks"))
    assert completed_res.success
    assert len(completed_res.data) == 2
    completed_ids = {task.id for task in completed_res.data}
    assert completed_ids == {2, 4}

# T081 & T082: Test workflow for search
def test_workflow_search(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Add tasks with specific keywords
    executor.execute(parser.parse("add task: Implement new documentation"))
    executor.execute(parser.parse("add task: Write code for feature X"))
    executor.execute(parser.parse("add task: Document the API"))

    # Search for a keyword with multiple matches
    search_res = executor.execute(parser.parse("search doc"))
    assert search_res.success
    assert len(search_res.data) == 2
    search_ids = {task.id for task in search_res.data}
    assert search_ids == {1, 3}

    # Search for a keyword with a single match
    search_res_single = executor.execute(parser.parse("search code"))
    assert search_res_single.success
    assert len(search_res_single.data) == 1
    assert search_res_single.data[0].id == 2

    # Search for a keyword with no matches
    search_res_none = executor.execute(parser.parse("search xyz"))
    assert search_res_none.success
    assert len(search_res_none.data) == 0

# T098 & T100: Test workflow for deleting tasks
def test_workflow_delete_task(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Add 3 tasks
    for i in range(3):
        executor.execute(parser.parse(f"add task: Task {i+1} to delete"))
    
    assert store.count() == 3

    # Delete task 2
    delete_res = executor.execute(parser.parse("delete task 2"))
    assert delete_res.success
    assert "deleted" in delete_res.message
    
    assert store.count() == 2
    assert store.get(2) is None # Task 2 should be gone

    # Verify remaining tasks
    list_res = executor.execute(parser.parse("list tasks"))
    assert list_res.success
    assert len(list_res.data) == 2
    assert {task.id for task in list_res.data} == {1, 3}

    # Test deleting a non-existent task
    delete_non_existent_res = executor.execute(parser.parse("delete task 999"))
    assert not delete_non_existent_res.success
    assert "not found" in delete_non_existent_res.message
    assert store.count() == 2 # Count should not change

# T099: Test workflow for updating tasks
def test_workflow_update_task(parser: InputParser, executor: TodoExecutor, store: TaskStore):
    # Add a task
    executor.execute(parser.parse("add task: Original Task Title with priority medium"))
    task_id = 1

    # Update title
    update_title_res = executor.execute(parser.parse(f"update task {task_id} title to New Task Title"))
    assert update_title_res.success
    assert "title changed to 'New Task Title'" in update_title_res.message
    updated_task = store.get(task_id)
    assert updated_task.title == "New Task Title"
    assert updated_task.priority == Priority.MEDIUM # Priority should be unchanged

    # Update priority
    update_priority_res = executor.execute(parser.parse(f"update task {task_id} priority to high"))
    assert update_priority_res.success
    assert "priority changed to HIGH" in update_priority_res.message
    updated_task_2 = store.get(task_id)
    assert updated_task_2.title == "New Task Title" # Title should be unchanged
    assert updated_task_2.priority == Priority.HIGH

    # Update both (though parser handles one at a time via different commands)
    # This scenario is implicitly covered by executing two separate update commands.

    # Test updating a non-existent task
    update_non_existent_res = executor.execute(parser.parse("update task 999 title to ABC"))
    assert not update_non_existent_res.success
    assert "not found" in update_non_existent_res.message