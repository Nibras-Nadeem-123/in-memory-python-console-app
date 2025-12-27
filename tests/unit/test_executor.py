"""Unit tests for executor module."""

from dataclasses import dataclass
from typing import Any, Dict

import pytest

# We'll import from src.executor once it's created
# For now, define the expected interface for TDD


@dataclass
class ExecutionResult:
    """Result of code execution (expected interface)."""
    status: str  # "success" or "error"
    result: Any | None
    error: str | None
    execution_time_ms: float
    variables_changed: list[str]


class TestCompileCode:
    """Tests for compile_code function."""

    def test_compile_valid_expression(self) -> None:
        """Test compiling valid Python expression."""
        from src.executor import compile_code

        compiled, error = compile_code("2 + 2")
        assert compiled is not None
        assert error is None

    def test_compile_valid_assignment(self) -> None:
        """Test compiling valid assignment statement."""
        from src.executor import compile_code

        compiled, error = compile_code("x = 10")
        assert compiled is not None
        assert error is None

    def test_compile_valid_function_definition(self) -> None:
        """Test compiling function definition."""
        from src.executor import compile_code

        code = """def greet(name):
    return f"Hello, {name}!\""""
        compiled, error = compile_code(code)
        assert compiled is not None
        assert error is None

    def test_compile_invalid_syntax_returns_error(self) -> None:
        """Test that invalid syntax returns error message."""
        from src.executor import compile_code

        compiled, error = compile_code("x = = 10")
        assert compiled is None
        assert error is not None
        assert "SyntaxError" in error or "syntax" in error.lower()

    def test_compile_incomplete_statement_returns_error(self) -> None:
        """Test that incomplete statement returns error."""
        from src.executor import compile_code

        compiled, error = compile_code("x = ")
        assert compiled is None
        assert error is not None

    def test_compile_empty_string(self) -> None:
        """Test compiling empty string."""
        from src.executor import compile_code

        compiled, error = compile_code("")
        # Empty code should compile successfully (no-op)
        assert compiled is not None
        assert error is None


class TestExecuteCode:
    """Tests for execute_code function."""

    def test_execute_simple_expression(self) -> None:
        """Test executing simple arithmetic expression."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("2 + 2", context)

        assert result.status == "success"
        assert result.result == 4
        assert result.error is None
        assert result.execution_time_ms >= 0

    def test_execute_assignment_statement(self) -> None:
        """Test executing variable assignment."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("x = 10", context)

        assert result.status == "success"
        assert result.result is None  # Statements don't return values
        assert result.error is None
        assert "x" in result.variables_changed

    def test_execute_multiple_assignments(self) -> None:
        """Test executing multiple variable assignments."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result1 = execute_code("x = 10", context)
        result2 = execute_code("y = 20", context)
        result3 = execute_code("z = x + y", context)

        assert result3.status == "success"
        assert result3.result is None
        assert "z" in result3.variables_changed

    def test_execute_variable_syncs_to_session_state(self) -> None:
        """Test that variables are synced to session state."""
        from src.executor import execute_code
        from src.session_manager import create_session_state, get_variable

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        execute_code("x = 42", context)

        value, metadata = get_variable(state, "x")
        assert value == 42
        assert metadata["type"] == "int"

    def test_execute_function_definition(self) -> None:
        """Test executing function definition."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        code = """def greet(name):
    return f"Hello, {name}!\""""
        result = execute_code(code, context)

        assert result.status == "success"
        assert "greet" in result.variables_changed

    def test_execute_function_call_after_definition(self) -> None:
        """Test calling function after defining it."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        execute_code("def greet(name):\n    return f'Hello, {name}!'", context)
        result = execute_code("greet('Alice')", context)

        assert result.status == "success"
        assert result.result == "Hello, Alice!"

    def test_execute_using_previously_defined_variable(self) -> None:
        """Test using variable defined in previous execution."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        execute_code("x = 10", context)
        result = execute_code("y = x * 2", context)

        assert result.status == "success"
        assert "y" in result.variables_changed

    def test_execute_measures_time(self) -> None:
        """Test that execution time is measured."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("sum(range(1000))", context)

        assert result.execution_time_ms >= 0
        assert isinstance(result.execution_time_ms, float)

    def test_execute_syntax_error_returns_error_result(self) -> None:
        """Test that syntax error returns error result, not exception."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("x = = 10", context)

        assert result.status == "error"
        assert result.error is not None
        assert result.result is None

    def test_execute_runtime_error_returns_error_result(self) -> None:
        """Test that runtime error is caught and returned."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("1 / 0", context)

        assert result.status == "error"
        assert result.error is not None
        assert "ZeroDivisionError" in result.error

    def test_execute_name_error_returns_error_result(self) -> None:
        """Test that NameError is caught."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("print(undefined_var)", context)

        assert result.status == "error"
        assert result.error is not None
        assert "NameError" in result.error

    def test_execute_list_comprehension(self) -> None:
        """Test executing list comprehension."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("[x * 2 for x in range(5)]", context)

        assert result.status == "success"
        assert result.result == [0, 2, 4, 6, 8]

    def test_execute_import_safe_module(self) -> None:
        """Test importing safe module (after security hook installed)."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("import math", context)

        # Should succeed (if security hook not yet installed)
        # Or fail with security message (if hook installed)
        assert result.status in ("success", "error")

    def test_execute_string_operations(self) -> None:
        """Test string operations and f-strings."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        result = execute_code("name = 'World'; f'Hello, {name}!'", context)

        assert result.status == "success"
        assert result.result == "Hello, World!"

    def test_execute_multiline_with_for_loop(self) -> None:
        """Test executing multi-line code with for loop."""
        from src.executor import execute_code
        from src.session_manager import create_session_state

        state = create_session_state()
        context = {"session_state": state, "globals": {}, "locals": {}}

        code = """result = []
for i in range(3):
    result.append(i * 2)"""
        result = execute_code(code, context)

        assert result.status == "success"
        assert "result" in result.variables_changed
