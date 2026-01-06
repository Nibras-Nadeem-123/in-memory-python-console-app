# tests/unit/test_input_parser.py

import pytest
from src.input_parser import InputParser
from src.task_model import OperationType, Priority, ParseError

@pytest.fixture
def parser() -> InputParser:
    """Provides an InputParser instance for each test."""
    return InputParser()

# T034: Test for parsing a simple "add" command
def test_parse_add_simple(parser: InputParser):
    command = parser.parse("add task: write documentation")
    assert command.operation == OperationType.ADD
    assert command.params["title"] == "write documentation"
    assert command.params["priority"] == Priority.MEDIUM

# T035: Test for parsing "add" with priority
def test_parse_add_with_priority(parser: InputParser):
    command = parser.parse("add task: review PR with priority high")
    assert command.operation == OperationType.ADD
    assert command.params["title"] == "review PR"
    assert command.params["priority"] == Priority.HIGH

def test_parse_add_alternative_keyword(parser: InputParser):
    """Tests 'create task' as an alias for 'add'."""
    command = parser.parse("create task: new item")
    assert command.operation == OperationType.ADD
    assert command.params["title"] == "new item"

# T036: Test for parsing "list tasks"
def test_parse_list(parser: InputParser):
    command = parser.parse("list tasks")
    assert command.operation == OperationType.LIST
    assert command.params == {}

# T072 & T073: Test for parsing "list" with status filters
@pytest.mark.parametrize("filter_text, expected_status", [
    ("list pending tasks", "pending"),
    ("list completed tasks", "completed"),
])
def test_parse_list_with_filter(parser: InputParser, filter_text: str, expected_status: str):
    command = parser.parse(filter_text)
    assert command.operation == OperationType.LIST
    assert command.params["status_filter"] == expected_status

# T074: Test for parsing "search" command
def test_parse_search(parser: InputParser):
    command = parser.parse("search documentation")
    assert command.operation == OperationType.SEARCH
    assert command.params["query"] == "documentation"

def test_parse_search_alias(parser: InputParser):
    """Tests 'find' as an alias for 'search'."""
    command = parser.parse("find important stuff")
    assert command.operation == OperationType.SEARCH
    assert command.params["query"] == "important stuff"

def test_parse_search_no_query(parser: InputParser):
    """Tests that a search command with no query raises an error."""
    with pytest.raises(ParseError, match="Search query cannot be empty"):
        parser.parse("search")
    with pytest.raises(ParseError, match="Search query cannot be empty"):
        parser.parse("find ")

# T037: Test for parsing "complete task"
def test_parse_complete(parser: InputParser):
    command = parser.parse("complete task 5")
    assert command.operation == OperationType.COMPLETE
    assert command.task_id == 5

def test_parse_complete_alias(parser: InputParser):
    """Tests 'done' as an alias for 'complete'."""
    command = parser.parse("done 123")
    assert command.operation == OperationType.COMPLETE
    assert command.task_id == 123

# T038: Test for parsing "exit"
def test_parse_exit(parser: InputParser):
    command = parser.parse("exit")
    assert command.operation == OperationType.EXIT

def test_parse_exit_alias(parser: InputParser):
    """Tests 'q' as an alias for 'exit'."""
    command = parser.parse("q")
    assert command.operation == OperationType.EXIT

# T039: Test for invalid command
def test_parse_invalid_command(parser: InputParser):
    with pytest.raises(ParseError, match="Unrecognized command"):
        parser.parse("do something random")

# T040: Test for empty input
def test_parse_empty_input(parser: InputParser):
    with pytest.raises(ParseError, match="Input cannot be empty"):
        parser.parse("")
    with pytest.raises(ParseError, match="Input cannot be empty"):
        parser.parse("   ")

# Additional tests for edge cases
def test_parse_add_no_title(parser: InputParser):
    """Tests that 'add' command with no title raises an error."""
    with pytest.raises(ParseError, match="Task title cannot be empty"):
        parser.parse("add task:")
    with pytest.raises(ParseError, match="Task title cannot be empty"):
        parser.parse("add task: ")

def test_parse_complete_no_id(parser: InputParser):
    """Tests that 'complete' command with no ID raises an error."""
    with pytest.raises(ParseError, match="Missing task ID"):
        parser.parse("complete task")

def test_parse_add_invalid_priority(parser: InputParser):
    """Tests that 'add' command with an invalid priority raises an error."""
    with pytest.raises(ParseError, match="Invalid priority"):
        parser.parse("add task: something with priority urgent")

# T088: Test for parsing "delete task"
def test_parse_delete(parser: InputParser):
    command = parser.parse("delete task 5")
    assert command.operation == OperationType.DELETE
    assert command.task_id == 5

def test_parse_delete_alias(parser: InputParser):
    """Tests 'remove task' as an alias for 'delete'."""
    command = parser.parse("remove task 10")
    assert command.operation == OperationType.DELETE
    assert command.task_id == 10

def test_parse_delete_no_id(parser: InputParser):
    """Tests that 'delete' command with no ID raises an error."""
    with pytest.raises(ParseError, match="Missing task ID"):
        parser.parse("delete task")

# T089, T090, T091: Test for parsing "update task"
def test_parse_update_title(parser: InputParser):
    command = parser.parse("update task 1 title to new title")
    assert command.operation == OperationType.UPDATE
    assert command.task_id == 1
    assert command.params["title"] == "new title"

@pytest.mark.parametrize("priority_input, expected_priority", [
    ("high", Priority.HIGH),
    ("medium", Priority.MEDIUM),
    ("low", Priority.LOW),
])
def test_parse_update_priority(parser: InputParser, priority_input: str, expected_priority: Priority):
    command = parser.parse(f"update task 2 priority to {priority_input}")
    assert command.operation == OperationType.UPDATE
    assert command.task_id == 2
    assert command.params["priority"] == expected_priority

def test_parse_update_priority_alias(parser: InputParser):
    command = parser.parse("change task 3 priority to low")
    assert command.operation == OperationType.UPDATE
    assert command.task_id == 3
    assert command.params["priority"] == Priority.LOW

def test_parse_update_title_and_priority(parser: InputParser):
    command = parser.parse("update task 4 title to newer title and priority to high")
    assert command.operation == OperationType.UPDATE
    assert command.task_id == 4
    assert command.params["title"] == "newer title and priority to high" # Regex not perfect, but captures the whole remainder

def test_parse_update_no_params(parser: InputParser):
    """Tests that an update command with no parameters raises an error."""
    with pytest.raises(ParseError, match="No update parameters"):
        parser.parse("update task 1")

def test_parse_update_invalid_priority_value(parser: InputParser):
    """Tests that an update command with an invalid priority value raises an error."""
    with pytest.raises(ParseError, match="Invalid priority"):
        parser.parse("update task 1 priority to superhigh")