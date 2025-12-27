"""Unit tests for formatter module."""

from typing import Any, Dict, List, Tuple

import pytest

from src.formatter import format_command_history, format_error, format_help_message, format_variable_list


class TestFormatError:
    """Tests for format_error function."""

    def test_format_name_error(self) -> None:
        """Test formatting NameError with suggestion."""
        exc = NameError("name 'undefined_var' is not defined")
        result = format_error(exc)

        assert "Error Type: NameError" in result
        assert "Description:" in result
        assert "Suggestion:" in result
        assert "undefined_var" in result
        assert "vars" in result.lower()

    def test_format_syntax_error(self) -> None:
        """Test formatting SyntaxError."""
        exc = SyntaxError("invalid syntax")
        result = format_error(exc)

        assert "Error Type: SyntaxError" in result
        assert "invalid syntax" in result
        assert "Suggestion:" in result

    def test_format_type_error(self) -> None:
        """Test formatting TypeError."""
        exc = TypeError("unsupported operand type(s)")
        result = format_error(exc)

        assert "Error Type: TypeError" in result
        assert "Type mismatch" in result
        assert "compatible types" in result

    def test_format_zero_division_error(self) -> None:
        """Test formatting ZeroDivisionError."""
        exc = ZeroDivisionError("division by zero")
        result = format_error(exc)

        assert "Error Type: ZeroDivisionError" in result
        assert "Division by zero" in result
        assert "divisor" in result.lower()

    def test_format_import_error(self) -> None:
        """Test formatting ImportError (security block)."""
        exc = ImportError("Security: Module 'os' is blocked")
        result = format_error(exc)

        assert "Error Type: ImportError" in result
        assert "blocked" in result.lower()
        assert "whitelisted" in result.lower()

    def test_format_value_error(self) -> None:
        """Test formatting ValueError."""
        exc = ValueError("invalid literal for int()")
        result = format_error(exc)

        assert "Error Type: ValueError" in result
        assert "Invalid value" in result

    def test_format_key_error(self) -> None:
        """Test formatting KeyError."""
        exc = KeyError("missing_key")
        result = format_error(exc)

        assert "Error Type: KeyError" in result
        assert "Key not found" in result

    def test_format_index_error(self) -> None:
        """Test formatting IndexError."""
        exc = IndexError("list index out of range")
        result = format_error(exc)

        assert "Error Type: IndexError" in result
        assert "Index out of range" in result

    def test_format_attribute_error(self) -> None:
        """Test formatting AttributeError."""
        exc = AttributeError("'int' object has no attribute 'append'")
        result = format_error(exc)

        assert "Error Type: AttributeError" in result
        assert "Attribute does not exist" in result

    def test_format_generic_exception(self) -> None:
        """Test formatting generic exception."""
        exc = Exception("Some generic error")
        result = format_error(exc)

        assert "Error Type: Exception" in result
        assert "Some generic error" in result

    def test_error_has_three_sections(self) -> None:
        """Test that error message has all three required sections."""
        exc = NameError("test")
        result = format_error(exc)

        assert "Error Type:" in result
        assert "Description:" in result
        assert "Suggestion:" in result


class TestFormatVariableList:
    """Tests for format_variable_list function."""

    def test_format_empty_list(self) -> None:
        """Test formatting empty variable list."""
        result = format_variable_list([])
        assert result == "No variables in session."

    def test_format_single_variable(self) -> None:
        """Test formatting single variable."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("x", 10, {"type": "int", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"})
        ]
        result = format_variable_list(variables)

        assert "Name" in result
        assert "Type" in result
        assert "Value" in result
        assert "Created" in result
        assert "Modified" in result
        assert "x" in result
        assert "int" in result
        assert "10" in result

    def test_format_multiple_variables(self) -> None:
        """Test formatting multiple variables."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("x", 10, {"type": "int", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"}),
            ("name", "Alice", {"type": "str", "created": "2025-12-27T10:01:00", "modified": "2025-12-27T10:01:00"}),
        ]
        result = format_variable_list(variables)

        assert "x" in result
        assert "name" in result
        assert "10" in result
        assert "Alice" in result

    def test_format_truncates_long_values(self) -> None:
        """Test that long values are truncated with ellipsis."""
        long_value = "a" * 100
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("long_var", long_value, {"type": "str", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"})
        ]
        result = format_variable_list(variables)

        assert "..." in result
        # Value should be truncated to fit column width (check data line, not separator)
        assert len(result.split("\n")[3].split("|")[3].strip()) <= 20

    def test_format_includes_timestamps(self) -> None:
        """Test that formatted output includes timestamps."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("x", 10, {"type": "int", "created": "2025-12-27T10:00:00.123456", "modified": "2025-12-27T10:05:30.654321"})
        ]
        result = format_variable_list(variables)

        # Should include timestamp (without microseconds)
        assert "2025-12-27 10:00:00" in result
        assert "2025-12-27 10:05:30" in result

    def test_format_has_table_structure(self) -> None:
        """Test that output has table structure with borders."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("x", 10, {"type": "int", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"})
        ]
        result = format_variable_list(variables)

        # Check for table borders
        assert "+" in result
        assert "-" in result
        assert "|" in result

    def test_format_list_variable(self) -> None:
        """Test formatting variable with list value."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("data", [1, 2, 3], {"type": "list", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"})
        ]
        result = format_variable_list(variables)

        assert "data" in result
        assert "list" in result
        assert "[1, 2, 3]" in result

    def test_format_dict_variable(self) -> None:
        """Test formatting variable with dict value."""
        variables: List[Tuple[str, Any, Dict[str, Any]]] = [
            ("config", {"key": "value"}, {"type": "dict", "created": "2025-12-27T10:00:00", "modified": "2025-12-27T10:00:00"})
        ]
        result = format_variable_list(variables)

        assert "config" in result
        assert "dict" in result


class TestFormatCommandHistory:
    """Tests for format_command_history function."""

    def test_format_empty_history(self) -> None:
        """Test formatting empty command history."""
        result = format_command_history([])
        assert result == "No command history."

    def test_format_single_command(self) -> None:
        """Test formatting single command in history."""
        history = [{"id": 1, "command": "x = 10"}]
        result = format_command_history(history)

        assert "Command History:" in result
        assert "[1]" in result
        assert "x = 10" in result

    def test_format_multiple_commands(self) -> None:
        """Test formatting multiple commands."""
        history = [
            {"id": 1, "command": "x = 10"},
            {"id": 2, "command": "y = 20"},
            {"id": 3, "command": "z = x + y"},
        ]
        result = format_command_history(history)

        assert "[1]" in result
        assert "[2]" in result
        assert "[3]" in result
        assert "x = 10" in result
        assert "y = 20" in result

    def test_format_respects_limit(self) -> None:
        """Test that formatting respects the limit parameter."""
        history = [{"id": i, "command": f"cmd{i}"} for i in range(1, 21)]
        result = format_command_history(history, limit=5)

        # Should only show last 5
        assert "[16]" in result
        assert "[20]" in result
        # Should not show earlier ones
        assert "[1]" not in result
        assert "[10]" not in result

    def test_format_shows_truncation_message(self) -> None:
        """Test that truncation message appears when history exceeds limit."""
        history = [{"id": i, "command": f"cmd{i}"} for i in range(1, 21)]
        result = format_command_history(history, limit=5)

        assert "15 more commands" in result

    def test_format_truncates_long_commands(self) -> None:
        """Test that long commands are truncated."""
        long_command = "x = " + "a" * 100
        history = [{"id": 1, "command": long_command}]
        result = format_command_history(history)

        assert "..." in result
        # Command should be truncated
        lines = result.split("\n")
        command_line = [line for line in lines if "[1]" in line][0]
        assert len(command_line) < len(long_command) + 20


class TestFormatHelpMessage:
    """Tests for format_help_message function."""

    def test_returns_non_empty_string(self) -> None:
        """Test that help message is not empty."""
        result = format_help_message()
        assert len(result) > 0

    def test_includes_system_commands(self) -> None:
        """Test that help message includes system commands."""
        result = format_help_message()

        assert "help" in result.lower()
        assert "exit" in result.lower()
        assert "vars" in result.lower()
        assert "save" in result.lower()
        assert "load" in result.lower()
        assert "clear" in result.lower()

    def test_includes_python_code_section(self) -> None:
        """Test that help includes Python code section."""
        result = format_help_message()
        assert "Python Code" in result or "python" in result.lower()

    def test_includes_examples(self) -> None:
        """Test that help includes usage examples."""
        result = format_help_message()
        assert "Example" in result or ">>>" in result

    def test_includes_security_information(self) -> None:
        """Test that help includes security information."""
        result = format_help_message()
        assert "Security" in result or "safe" in result.lower()
        assert "math" in result.lower()  # Example safe module
        assert "os" in result.lower() or "blocked" in result.lower()

    def test_multiline_format(self) -> None:
        """Test that help message is multiline."""
        result = format_help_message()
        assert "\n" in result
        assert len(result.split("\n")) > 10  # Should be substantial
