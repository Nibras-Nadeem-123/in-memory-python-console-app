# tests/integration/test_sdd_workflow.py

import pytest
from src.input_parser import InputParser
from src.todo_executor import TodoExecutor
from src.task_store import TaskStore

# T060: Test for spec-driven flow validation
def test_sdd_flow_parse_has_no_side_effects():
    """
    Validates the Spec-Driven Development flow:
    1. Parsing a command (creating the "spec") should have NO side effects.
    2. Executing the command SHOULD have side effects (state change).
    """
    # Setup
    parser = InputParser()
    store = TaskStore()
    executor = TodoExecutor(store)
    
    command_text = "add task: a new thing"
    
    # 1. Parse the command
    command = parser.parse(command_text)
    
    # === Verification Step 1: Assert NO side effects after parsing ===
    # The store should be empty because parsing should not change state.
    assert store.count() == 0, "Parsing should not modify the application state."

    # 2. Execute the command
    result = executor.execute(command)
    
    # === Verification Step 2: Assert side effects after execution ===
    # The store should now contain one item.
    assert result.success is True
    assert store.count() == 1, "Execution should modify the application state."

    task = store.get(1)
    assert task is not None
    assert task.title == "a new thing"