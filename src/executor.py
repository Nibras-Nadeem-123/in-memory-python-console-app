"""Code execution engine with error handling and state synchronization."""

import time
from dataclasses import dataclass
from types import CodeType
from typing import Any, Dict, Tuple

from src.formatter import format_error
from src.session_manager import SessionState, add_variable


@dataclass
class ExecutionResult:
    """Result of code execution.

    Attributes:
        status: "success" or "error"
        result: Return value or output (None for statements)
        error: Formatted error message if failed
        execution_time_ms: Time taken to execute in milliseconds
        variables_changed: Names of variables created/modified
    """
    status: str
    result: Any | None
    error: str | None
    execution_time_ms: float
    variables_changed: list[str]


def compile_code(code: str) -> Tuple[CodeType | None, str | None]:
    """Compile Python source code and validate syntax.

    Args:
        code: Python source code string

    Returns:
        Tuple of (compiled_code, error_message)
        - If success: (CodeType object, None)
        - If error: (None, formatted error string)
    """
    if not code.strip():
        # Empty code compiles to no-op
        code = "pass"

    try:
        compiled = compile(code, "<console>", "exec")
        return (compiled, None)
    except SyntaxError as e:
        error_msg = format_error(e)
        return (None, error_msg)
    except Exception as e:
        error_msg = format_error(e)
        return (None, error_msg)


def execute_code(code: str, context: Dict[str, Any]) -> ExecutionResult:
    """Execute Python code in the execution context.

    Args:
        code: Python source code to execute
        context: Execution environment with session_state, globals, locals

    Returns:
        ExecutionResult with status, result, error, timing, and changed variables
    """
    start_time = time.time()
    session_state: SessionState = context["session_state"]
    globals_dict: Dict[str, Any] = context.get("globals", {})
    locals_dict: Dict[str, Any] = context.get("locals", {})

    # Restore all variables from session_state to both locals and globals
    # Functions need to be in globals for recursion to work
    for name, (value, _metadata) in session_state.items():
        locals_dict[name] = value
        globals_dict[name] = value

    # Capture variables before execution
    vars_before = set(locals_dict.keys())

    try:
        # Try to compile as expression first (for interactive results)
        result = None
        try:
            compiled_expr = compile(code, "<console>", "eval")
            result = eval(compiled_expr, globals_dict, locals_dict)  # type: ignore
        except SyntaxError:
            # Not a simple expression, compile and execute as statement
            compiled, compile_error = compile_code(code)
            if compile_error:
                execution_time = (time.time() - start_time) * 1000
                return ExecutionResult(
                    status="error",
                    result=None,
                    error=compile_error,
                    execution_time_ms=execution_time,
                    variables_changed=[]
                )
            # Execute as statement
            exec(compiled, globals_dict, locals_dict)  # type: ignore

            # For compound statements like "x=1; expr", try to get last expression value
            # by checking if the code contains a semicolon and evaluating the last part
            if ';' in code:
                parts = code.split(';')
                last_part = parts[-1].strip()
                if last_part:
                    try:
                        result = eval(last_part, globals_dict, locals_dict)  # type: ignore
                    except:
                        pass

        # Sync locals to session state
        vars_after = set(locals_dict.keys())
        variables_changed = _sync_locals_to_session(
            locals_dict,
            session_state,
            vars_before,
            vars_after
        )

        execution_time = (time.time() - start_time) * 1000

        return ExecutionResult(
            status="success",
            result=result,
            error=None,
            execution_time_ms=execution_time,
            variables_changed=variables_changed
        )

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        error_msg = format_error(e)

        return ExecutionResult(
            status="error",
            result=None,
            error=error_msg,
            execution_time_ms=execution_time,
            variables_changed=[]
        )


def _sync_locals_to_session(
    locals_dict: Dict[str, Any],
    session_state: SessionState,
    vars_before: set[str],
    vars_after: set[str]
) -> list[str]:
    """Sync local variables to session state and return changed variable names.

    Args:
        locals_dict: Local namespace after execution
        session_state: Session state to update
        vars_before: Set of variable names before execution
        vars_after: Set of variable names after execution

    Returns:
        List of variable names that were created or modified
    """
    changed_vars = []

    # Find new or modified variables
    for name in vars_after:
        # Skip special variables
        if name.startswith("_"):
            continue

        value = locals_dict[name]

        # Skip modules and other non-serializable builtins
        if hasattr(value, "__module__") and not isinstance(value, (int, float, str, list, dict, tuple, set, bool, type(None))):
            # Still track functions and classes
            if callable(value) or isinstance(value, type):
                try:
                    add_variable(session_state, name, value)
                    changed_vars.append(name)
                except ValueError:
                    # Reserved name, skip
                    pass
            continue

        # Check if variable is new or value changed
        if name not in vars_before:
            # New variable
            try:
                add_variable(session_state, name, value)
                changed_vars.append(name)
            except ValueError:
                # Reserved name, skip
                pass
        else:
            # Existing variable - check if value changed
            if name in session_state:
                old_value, _ = session_state[name]
                if old_value != value:
                    try:
                        add_variable(session_state, name, value)
                        changed_vars.append(name)
                    except ValueError:
                        pass
            else:
                # Variable in locals but not in session state (add it)
                try:
                    add_variable(session_state, name, value)
                    changed_vars.append(name)
                except ValueError:
                    pass

    return changed_vars
