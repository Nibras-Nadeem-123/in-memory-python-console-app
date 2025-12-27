"""Integration tests for REPL workflow."""

from io import StringIO
from typing import Any, Dict

import pytest

from src.executor import execute_code
from src.parser import detect_system_command, is_complete_statement
from src.session_manager import create_session_state, list_variables


class TestSingleLinePythonExecution:
    """Integration tests for single-line Python code execution."""

    def test_execute_simple_expression_end_to_end(self) -> None:
        """Test complete flow: parse → execute → display result."""
        code = "2 + 2"

        # Parse
        assert is_complete_statement(code) is True
        command, args = detect_system_command(code)
        assert command is None  # Not a system command

        # Execute
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}
        result = execute_code(code, context)

        # Verify
        assert result.status == "success"
        assert result.result == 4

    def test_execute_variable_assignment_and_retrieval(self) -> None:
        """Test assigning variable and using it in next command."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Assign
        result1 = execute_code("x = 10", context)
        assert result1.status == "success"
        assert "x" in result1.variables_changed

        # Use
        result2 = execute_code("y = x * 2", context)
        assert result2.status == "success"
        assert "y" in result2.variables_changed

        # Verify both in session
        vars_list = list_variables(state)
        var_names = [v[0] for v in vars_list]
        assert "x" in var_names
        assert "y" in var_names

    def test_execute_multiple_commands_in_sequence(self) -> None:
        """Test executing sequence of commands."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        commands = [
            "a = 5",
            "b = 10",
            "c = a + b",
            "d = c * 2",
        ]

        for cmd in commands:
            result = execute_code(cmd, context)
            assert result.status == "success"

        # Verify all variables
        vars_list = list_variables(state)
        assert len(vars_list) == 4

    def test_execute_expression_with_print(self) -> None:
        """Test executing print statement."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("print('Hello, World!')", context)
        assert result.status == "success"


class TestMultiLinePythonExecution:
    """Integration tests for multi-line Python code execution."""

    def test_detect_incomplete_function_definition(self) -> None:
        """Test that incomplete function is detected."""
        code = "def greet(name):"
        assert is_complete_statement(code) is False

    def test_detect_complete_function_definition(self) -> None:
        """Test that complete function is detected."""
        code = """def greet(name):
    return f"Hello, {name}!\""""
        assert is_complete_statement(code) is True

    def test_execute_function_definition_end_to_end(self) -> None:
        """Test defining and calling a function."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Define function
        func_code = """def greet(name):
    return f"Hello, {name}!\""""
        result1 = execute_code(func_code, context)
        assert result1.status == "success"
        assert "greet" in result1.variables_changed

        # Call function
        result2 = execute_code("greet('Alice')", context)
        assert result2.status == "success"
        assert result2.result == "Hello, Alice!"

    def test_execute_for_loop(self) -> None:
        """Test executing for loop."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        code = """result = []
for i in range(3):
    result.append(i * 2)"""

        result = execute_code(code, context)
        assert result.status == "success"
        assert "result" in result.variables_changed

        # Verify result variable
        vars_list = list_variables(state)
        result_var = [v for v in vars_list if v[0] == "result"][0]
        assert result_var[1] == [0, 2, 4]

    def test_execute_class_definition(self) -> None:
        """Test defining a class."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        code = """class Person:
    def __init__(self, name):
        self.name = name"""

        result = execute_code(code, context)
        assert result.status == "success"
        assert "Person" in result.variables_changed


class TestSystemCommands:
    """Integration tests for system commands."""

    def test_detect_help_command(self) -> None:
        """Test detecting help command."""
        command, args = detect_system_command("help")
        assert command == "help"
        assert args == []

    def test_detect_exit_command(self) -> None:
        """Test detecting exit command."""
        command, args = detect_system_command("exit")
        assert command == "exit"
        assert args == []

    def test_detect_vars_command(self) -> None:
        """Test detecting vars command."""
        command, args = detect_system_command("vars")
        assert command == "vars"
        assert args == []

    def test_detect_save_command_with_filename(self) -> None:
        """Test detecting save command with arguments."""
        command, args = detect_system_command("save session.json")
        assert command == "save"
        assert args == ["session.json"]

    def test_vars_command_displays_all_variables(self) -> None:
        """Test that vars command shows all session variables."""
        from src.formatter import format_variable_list

        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Add some variables
        execute_code("x = 10", context)
        execute_code("name = 'Alice'", context)

        # Format variables
        vars_list = list_variables(state)
        output = format_variable_list(vars_list)

        assert "x" in output
        assert "name" in output
        assert "10" in output
        assert "Alice" in output

    def test_help_command_shows_available_commands(self) -> None:
        """Test that help command shows command list."""
        from src.formatter import format_help_message

        help_text = format_help_message()

        assert "help" in help_text.lower()
        assert "exit" in help_text.lower()
        assert "vars" in help_text.lower()
        assert len(help_text) > 100  # Substantial help text


class TestErrorHandling:
    """Integration tests for error handling in workflow."""

    def test_syntax_error_does_not_crash(self) -> None:
        """Test that syntax error is caught gracefully."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("x = = 10", context)

        assert result.status == "error"
        assert result.error is not None
        assert "SyntaxError" in result.error

    def test_runtime_error_does_not_crash(self) -> None:
        """Test that runtime error is caught gracefully."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("1 / 0", context)

        assert result.status == "error"
        assert "ZeroDivisionError" in result.error

    def test_name_error_provides_helpful_message(self) -> None:
        """Test that NameError provides helpful message."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("print(undefined_var)", context)

        assert result.status == "error"
        assert "NameError" in result.error
        assert "vars" in result.error.lower()  # Suggestion to use vars command

    def test_continue_execution_after_error(self) -> None:
        """Test that execution continues after an error."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Cause error
        result1 = execute_code("1 / 0", context)
        assert result1.status == "error"

        # Continue with valid code
        result2 = execute_code("x = 42", context)
        assert result2.status == "success"
        assert "x" in result2.variables_changed


class TestCompleteUserJourney:
    """End-to-end integration tests for complete user workflows."""

    def test_calculator_workflow(self) -> None:
        """Test using console as calculator."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Define pi
        result1 = execute_code("pi = 3.14159", context)
        assert result1.status == "success"

        # Calculate area
        result2 = execute_code("radius = 5", context)
        assert result2.status == "success"

        result3 = execute_code("area = pi * radius ** 2", context)
        assert result3.status == "success"

        # Check result
        vars_list = list_variables(state)
        area_var = [v for v in vars_list if v[0] == "area"][0]
        assert area_var[1] > 78  # Approximately correct

    def test_function_development_workflow(self) -> None:
        """Test developing and testing a function."""
        state = create_session_state()
        context: Dict[str, Any] = {"session_state": state, "globals": {}, "locals": {}}

        # Define function
        func_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""

        result1 = execute_code(func_code, context)
        assert result1.status == "success"

        # Test function
        result2 = execute_code("fibonacci(5)", context)
        assert result2.status == "success"
        assert result2.result == 5  # 5th Fibonacci number

        result3 = execute_code("fibonacci(10)", context)
        assert result3.status == "success"
        assert result3.result == 55  # 10th Fibonacci number
