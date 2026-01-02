"""Unit tests for input parser."""

import pytest

from src.input_parser import (
    AmbiguousInputError,
    InputParser,
    MissingTitleError,
    UnknownCommandError,
)


class TestInputParser:
    """Tests for the InputParser class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = InputParser()

    # Add command tests
    def test_add_task(self) -> None:
        """Test parsing add task command."""
        intent = self.parser.parse("add task Buy milk")

        assert intent.action == "add"
        assert intent.new_title == "Buy milk"
        assert intent.due_date is None

    def test_add_task_short(self) -> None:
        """Test parsing short add command."""
        intent = self.parser.parse("add Buy milk")

        assert intent.action == "add"
        assert intent.new_title == "Buy milk"

    def test_add_task_with_due_date(self) -> None:
        """Test parsing add task with due date."""
        intent = self.parser.parse("add task Buy milk by tomorrow")

        assert intent.action == "add"
        assert intent.new_title == "Buy milk"
        assert intent.due_date == "tomorrow"

    def test_add_new_task(self) -> None:
        """Test parsing new task command."""
        intent = self.parser.parse("new task Finish report")

        assert intent.action == "add"
        assert intent.new_title == "Finish report"

    def test_add_create_task(self) -> None:
        """Test parsing create task command."""
        intent = self.parser.parse("create task Write tests")

        assert intent.action == "add"
        assert intent.new_title == "Write tests"

    def test_add_missing_title(self) -> None:
        """Test that missing title raises MissingTitleError."""
        with pytest.raises(MissingTitleError):
            self.parser.parse("add task")

    # List command tests
    def test_list_tasks(self) -> None:
        """Test parsing list tasks command."""
        intent = self.parser.parse("list tasks")

        assert intent.action == "list"

    def test_list_short(self) -> None:
        """Test parsing short list command."""
        intent = self.parser.parse("list")

        assert intent.action == "list"

    def test_show_tasks(self) -> None:
        """Test parsing show tasks command."""
        intent = self.parser.parse("show tasks")

        assert intent.action == "list"

    # Complete command tests
    def test_complete_task(self) -> None:
        """Test parsing complete task command."""
        intent = self.parser.parse("complete Buy milk")

        assert intent.action == "complete"
        assert intent.target == "Buy milk"

    def test_mark_done(self) -> None:
        """Test parsing mark done command."""
        intent = self.parser.parse("mark Buy milk done")

        assert intent.action == "complete"
        assert intent.target == "Buy milk"

    def test_finish_task(self) -> None:
        """Test parsing finish task command."""
        intent = self.parser.parse("finish Buy milk")

        assert intent.action == "complete"
        assert intent.target == "Buy milk"

    def test_done_task(self) -> None:
        """Test parsing done task command."""
        intent = self.parser.parse("done Buy milk")

        assert intent.action == "complete"
        assert intent.target == "Buy milk"

    # Update command tests
    def test_update_task(self) -> None:
        """Test parsing update task command."""
        intent = self.parser.parse("update Buy milk to Buy eggs")

        assert intent.action == "update"
        assert intent.target == "Buy milk"
        assert intent.new_title == "Buy eggs"

    def test_change_task(self) -> None:
        """Test parsing change task command."""
        intent = self.parser.parse("change Buy milk to Buy eggs")

        assert intent.action == "update"
        assert intent.target == "Buy milk"
        assert intent.new_title == "Buy eggs"

    def test_set_due_date(self) -> None:
        """Test parsing set due date command."""
        intent = self.parser.parse("set due date for Buy milk to tomorrow")

        assert intent.action == "update"
        assert intent.target == "Buy milk"
        assert intent.due_date == "tomorrow"

    # Delete command tests
    def test_delete_task(self) -> None:
        """Test parsing delete task command."""
        intent = self.parser.parse("delete Buy milk")

        assert intent.action == "delete"
        assert intent.target == "Buy milk"

    def test_remove_task(self) -> None:
        """Test parsing remove task command."""
        intent = self.parser.parse("remove Buy milk")

        assert intent.action == "delete"
        assert intent.target == "Buy milk"

    def test_drop_task(self) -> None:
        """Test parsing drop task command."""
        intent = self.parser.parse("drop Buy milk")

        assert intent.action == "delete"
        assert intent.target == "Buy milk"

    # Undo command tests
    def test_undo(self) -> None:
        """Test parsing undo command."""
        intent = self.parser.parse("undo")

        assert intent.action == "undo"

    def test_undo_last(self) -> None:
        """Test parsing undo last command."""
        intent = self.parser.parse("undo last")

        assert intent.action == "undo"

    # Help command tests
    def test_help(self) -> None:
        """Test parsing help command."""
        intent = self.parser.parse("help")

        assert intent.action == "help"

    def test_show_help(self) -> None:
        """Test parsing show help command."""
        intent = self.parser.parse("show help")

        assert intent.action == "help"

    def test_commands(self) -> None:
        """Test parsing commands command."""
        intent = self.parser.parse("commands")

        assert intent.action == "help"

    # Exit command tests
    def test_exit(self) -> None:
        """Test parsing exit command."""
        intent = self.parser.parse("exit")

        assert intent.action == "exit"

    def test_quit(self) -> None:
        """Test parsing quit command."""
        intent = self.parser.parse("quit")

        assert intent.action == "exit"

    def test_bye(self) -> None:
        """Test parsing bye command."""
        intent = self.parser.parse("bye")

        assert intent.action == "exit"

    def test_goodbye(self) -> None:
        """Test parsing goodbye command."""
        intent = self.parser.parse("goodbye")

        assert intent.action == "exit"

    # Edge cases
    def test_empty_input(self) -> None:
        """Test that empty input raises AmbiguousInputError."""
        with pytest.raises(AmbiguousInputError):
            self.parser.parse("")

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only input raises AmbiguousInputError."""
        with pytest.raises(AmbiguousInputError):
            self.parser.parse("   ")

    def test_unknown_command(self) -> None:
        """Test that unknown command raises UnknownCommandError."""
        with pytest.raises(UnknownCommandError):
            self.parser.parse("frobnicate the widget")

    def test_case_insensitive(self) -> None:
        """Test that commands are case-insensitive."""
        intent1 = self.parser.parse("ADD TASK Buy milk")
        intent2 = self.parser.parse("Add Task Buy milk")
        intent3 = self.parser.parse("add task Buy milk")

        assert intent1.action == "add"
        assert intent2.action == "add"
        assert intent3.action == "add"

    def test_update_missing_new_title(self) -> None:
        """Test that update without new title raises MissingTitleError."""
        with pytest.raises(MissingTitleError):
            self.parser.parse("update Buy milk to")

    def test_update_due_date_extraction(self) -> None:
        """Test that due date is extracted in update command."""
        intent = self.parser.parse("update Buy milk to Buy eggs by Friday")

        assert intent.new_title == "Buy eggs"
        assert intent.due_date == "Friday"
