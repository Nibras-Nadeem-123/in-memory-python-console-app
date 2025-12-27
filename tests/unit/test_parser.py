"""Unit tests for parser module."""

import pytest

from src.parser import detect_system_command, is_complete_statement


class TestIsCompleteStatement:
    """Tests for is_complete_statement function."""

    def test_complete_simple_expression(self) -> None:
        """Test that simple expression is complete."""
        assert is_complete_statement("2 + 2") is True

    def test_complete_assignment(self) -> None:
        """Test that variable assignment is complete."""
        assert is_complete_statement("x = 10") is True

    def test_complete_print_statement(self) -> None:
        """Test that print statement is complete."""
        assert is_complete_statement('print("hello")') is True

    def test_incomplete_function_definition(self) -> None:
        """Test that function definition without body is incomplete."""
        assert is_complete_statement("def foo():") is False

    def test_incomplete_class_definition(self) -> None:
        """Test that class definition without body is incomplete."""
        assert is_complete_statement("class Bar:") is False

    def test_incomplete_if_statement(self) -> None:
        """Test that if statement without body is incomplete."""
        assert is_complete_statement("if x > 5:") is False

    def test_incomplete_for_loop(self) -> None:
        """Test that for loop without body is incomplete."""
        assert is_complete_statement("for i in range(10):") is False

    def test_incomplete_unclosed_bracket(self) -> None:
        """Test that unclosed bracket makes statement incomplete."""
        assert is_complete_statement("[1, 2, 3") is False

    def test_incomplete_unclosed_paren(self) -> None:
        """Test that unclosed parenthesis makes statement incomplete."""
        assert is_complete_statement("print(") is False

    def test_incomplete_unclosed_brace(self) -> None:
        """Test that unclosed brace makes statement incomplete."""
        assert is_complete_statement("{'key': 'value'") is False

    def test_complete_multiline_function(self) -> None:
        """Test that complete multiline function is recognized."""
        code = """def greet(name):
    return f"Hello, {name}!\""""
        assert is_complete_statement(code) is True

    def test_complete_multiline_class(self) -> None:
        """Test that complete multiline class is recognized."""
        code = """class Person:
    def __init__(self, name):
        self.name = name"""
        assert is_complete_statement(code) is True

    def test_incomplete_trailing_backslash(self) -> None:
        """Test that trailing backslash indicates continuation."""
        assert is_complete_statement("x = 1 + \\") is False

    def test_complete_multiline_string(self) -> None:
        """Test that complete multiline string is recognized."""
        code = '''"""This is
a multiline
string"""'''
        assert is_complete_statement(code) is True

    def test_incomplete_unclosed_multiline_string(self) -> None:
        """Test that unclosed multiline string is incomplete."""
        code = '''"""This is incomplete'''
        assert is_complete_statement(code) is False

    def test_empty_string_is_complete(self) -> None:
        """Test that empty input is considered complete."""
        assert is_complete_statement("") is True

    def test_whitespace_only_is_complete(self) -> None:
        """Test that whitespace-only input is complete."""
        assert is_complete_statement("   \n  \t  ") is True

    def test_complete_with_comment(self) -> None:
        """Test that statement with comment is complete."""
        assert is_complete_statement("x = 10  # assign value") is True

    def test_incomplete_with_comment_after_colon(self) -> None:
        """Test that comment after colon doesn't make statement complete."""
        assert is_complete_statement("def foo():  # define function") is False

    def test_syntax_error_is_complete(self) -> None:
        """Test that syntax error (not EOF-related) is considered complete."""
        # Malformed code that's not incomplete, just wrong
        assert is_complete_statement("x = = 10") is True


class TestDetectSystemCommand:
    """Tests for detect_system_command function."""

    def test_detect_help_command(self) -> None:
        """Test detection of help command."""
        command, args = detect_system_command("help")
        assert command == "help"
        assert args == []

    def test_detect_exit_command(self) -> None:
        """Test detection of exit command."""
        command, args = detect_system_command("exit")
        assert command == "exit"
        assert args == []

    def test_detect_quit_command(self) -> None:
        """Test detection of quit command."""
        command, args = detect_system_command("quit")
        assert command == "quit"
        assert args == []

    def test_detect_vars_command(self) -> None:
        """Test detection of vars command."""
        command, args = detect_system_command("vars")
        assert command == "vars"
        assert args == []

    def test_detect_clear_command(self) -> None:
        """Test detection of clear command."""
        command, args = detect_system_command("clear")
        assert command == "clear"
        assert args == []

    def test_detect_save_command_with_filename(self) -> None:
        """Test detection of save command with filename argument."""
        command, args = detect_system_command("save session.json")
        assert command == "save"
        assert args == ["session.json"]

    def test_detect_load_command_with_filename(self) -> None:
        """Test detection of load command with filename argument."""
        command, args = detect_system_command("load my_session.json")
        assert command == "load"
        assert args == ["my_session.json"]

    def test_detect_save_with_path(self) -> None:
        """Test save command with file path."""
        command, args = detect_system_command("save /tmp/session.json")
        assert command == "save"
        assert args == ["/tmp/session.json"]

    def test_detect_history_command(self) -> None:
        """Test detection of history command."""
        command, args = detect_system_command("history")
        assert command == "history"
        assert args == []

    def test_python_expression_not_detected_as_command(self) -> None:
        """Test that Python expression is not detected as system command."""
        command, args = detect_system_command("x = 10")
        assert command is None
        assert args == []

    def test_python_function_call_not_detected(self) -> None:
        """Test that Python function call is not detected as system command."""
        command, args = detect_system_command("print('hello')")
        assert command is None
        assert args == []

    def test_empty_input_not_detected(self) -> None:
        """Test that empty input is not a command."""
        command, args = detect_system_command("")
        assert command is None
        assert args == []

    def test_whitespace_only_not_detected(self) -> None:
        """Test that whitespace-only input is not a command."""
        command, args = detect_system_command("   \t  ")
        assert command is None
        assert args == []

    def test_case_insensitive_command_detection(self) -> None:
        """Test that commands are case-insensitive."""
        command, args = detect_system_command("HELP")
        assert command == "help"
        assert args == []

    def test_command_with_multiple_arguments(self) -> None:
        """Test command with multiple arguments."""
        command, args = detect_system_command("save my_session.json backup")
        assert command == "save"
        assert args == ["my_session.json", "backup"]

    def test_command_with_extra_whitespace(self) -> None:
        """Test command with extra whitespace is handled correctly."""
        command, args = detect_system_command("  save   session.json  ")
        assert command == "save"
        assert args == ["session.json"]
