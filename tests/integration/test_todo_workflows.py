"""Integration tests for todo workflows.

Tests complete user journeys from input to output.
"""

from src.task_store import TaskStore
from src.todo_cli import TodoCLI
from src.todo_executor import TodoExecutor


class TestTodoWorkflows:
    """Integration tests for complete workflows."""

    def test_add_list_workflow(self) -> None:
        """Test add task then list workflow."""
        cli = TodoCLI()

        # Add a task
        result = cli.execute("add task Buy milk")
        assert result.success
        assert "Buy milk" in result.message

        # List tasks
        result = cli.execute("list")
        assert result.success
        assert "Buy milk" in result.message
        assert "[ ]" in result.message  # pending marker

    def test_add_complete_list_workflow(self) -> None:
        """Test add, complete, list workflow."""
        cli = TodoCLI()

        # Add task
        result = cli.execute("add task Buy milk")
        assert result.success

        # Complete task
        result = cli.execute("complete Buy milk")
        assert result.success
        assert "Completed" in result.message

        # List - should show completed
        result = cli.execute("list")
        assert result.success
        assert "[x]" in result.message  # completed marker

    def test_add_complete_undo_list_workflow(self) -> None:
        """Test add, complete, undo, list workflow."""
        cli = TodoCLI()

        # Add task
        cli.execute("add task Buy milk")

        # Complete task
        cli.execute("complete Buy milk")

        # Undo
        result = cli.execute("undo")
        assert result.success
        assert "Undid" in result.message

        # List - should be pending again
        result = cli.execute("list")
        assert result.success
        assert "[ ]" in result.message
        assert "[x]" not in result.message

    def test_add_update_list_workflow(self) -> None:
        """Test add, update, list workflow."""
        cli = TodoCLI()

        # Add task
        cli.execute("add task Buy milk")

        # Update task
        result = cli.execute("update Buy milk to Buy eggs")
        assert result.success
        assert "Buy eggs" in result.message

        # List - should show new title
        result = cli.execute("list")
        assert result.success
        assert "Buy eggs" in result.message
        assert "Buy milk" not in result.message

    def test_add_delete_list_workflow(self) -> None:
        """Test add, delete, list workflow."""
        cli = TodoCLI()

        # Add two tasks
        cli.execute("add task Buy milk")
        cli.execute("add task Buy eggs")

        # Delete one
        result = cli.execute("delete Buy milk")
        assert result.success
        assert "Deleted" in result.message

        # List - should only show remaining
        result = cli.execute("list")
        assert result.success
        assert "Buy eggs" in result.message
        assert "Buy milk" not in result.message

    def test_multiple_tasks_order(self) -> None:
        """Test that multiple tasks are shown in ID order."""
        cli = TodoCLI()

        # Add tasks
        cli.execute("add task Third task")
        cli.execute("add task First task")
        cli.execute("add task Second task")

        # List - should be in ID order (1, 2, 3)
        result = cli.execute("list")
        lines = result.message.split("\n")

        # Each line should have the correct task
        # Line 1: "Your tasks:"
        # Line 2: "  1. [ ] Third task" (ID 1)
        # Line 3: "  2. [ ] First task" (ID 2)
        # Line 4: "  3. [ ] Second task" (ID 3)
        assert "Third task" in lines[1]  # ID 1
        assert "First task" in lines[2]  # ID 2
        assert "Second task" in lines[3]  # ID 3

    def test_error_task_not_found_suggests_create(self) -> None:
        """Test that non-existent task error suggests creation."""
        cli = TodoCLI()

        result = cli.execute("complete nonexistent task")

        assert not result.success
        assert "not found" in result.message.lower()
        assert "create" in result.message.lower()

    def test_help_command(self) -> None:
        """Test help command shows all commands."""
        cli = TodoCLI()

        result = cli.execute("help")

        assert result.success
        assert "add" in result.message
        assert "list" in result.message
        assert "complete" in result.message
        assert "update" in result.message
        assert "delete" in result.message
        assert "undo" in result.message
        assert "help" in result.message
        assert "exit" in result.message

    def test_exit_command(self) -> None:
        """Test exit command."""
        cli = TodoCLI()

        result = cli.execute("exit")

        assert result.success
        assert "Goodbye" in result.message

    def test_due_date_handling(self) -> None:
        """Test due date is preserved and displayed."""
        cli = TodoCLI()

        # Add with due date
        result = cli.execute("add task Buy milk by tomorrow")
        assert result.success
        assert "tomorrow" in result.message

        # List should show due date
        result = cli.execute("list")
        assert "tomorrow" in result.message

    def test_workflow_with_different_phrasings(self) -> None:
        """Test that different phrasings work for same action."""
        cli = TodoCLI()

        # Test complete with different phrasings on different tasks
        cli.execute("add task First task")
        result = cli.execute("complete First task")
        assert result.success

        cli.execute("add task Second task")
        result = cli.execute("mark Second task done")
        assert result.success

        cli.execute("add task Third task")
        result = cli.execute("finish Third task")
        assert result.success

        # All should be completed
        result = cli.execute("list")
        assert result.success
        assert "[x]" in result.message

    def test_task_reference_by_title_substring(self) -> None:
        """Test referencing task by partial title match."""
        cli = TodoCLI()

        cli.execute("add task Buy groceries at store")

        # Should match with just part of title
        result = cli.execute("complete groceries")
        assert result.success

    def test_empty_list_after_all_completed(self) -> None:
        """Test list shows meaningful message when all tasks done."""
        cli = TodoCLI()

        cli.execute("add task Buy milk")
        cli.execute("complete Buy milk")

        # List should show completed task
        result = cli.execute("list")
        assert "Buy milk" in result.message
