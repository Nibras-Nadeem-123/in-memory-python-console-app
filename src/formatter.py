"""Output and error message formatting."""

from typing import Any, Dict, List, Tuple


def format_error(exc: Exception, context: str = "") -> str:
    """Format exception as structured error message with 3 sections.

    Generates user-friendly error messages with:
    - Error Type: Exception name and Python error message
    - Description: Plain language explanation
    - Suggestion: Actionable steps to resolve

    Args:
        exc: Exception to format
        context: Optional context about where error occurred

    Returns:
        Formatted error message string with 3 sections
    """
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Build structured error message
    lines = [
        f"Error Type: {exc_type}",
        f"Description: {_get_error_description(exc)}",
        f"Suggestion: {_get_error_suggestion(exc)}",
    ]

    return "\n".join(lines)


def _get_error_description(exc: Exception) -> str:
    """Get plain language description for exception."""
    exc_type = type(exc).__name__
    exc_message = str(exc)

    descriptions = {
        "NameError": f"Variable or name '{_extract_name_from_error(exc_message)}' is not defined in the current session.",
        "SyntaxError": f"Invalid Python syntax - {exc_message}",
        "TypeError": f"Type mismatch in operation - {exc_message}",
        "ZeroDivisionError": "Division by zero is not allowed in mathematics.",
        "ImportError": f"{exc_message}",
        "ValueError": f"Invalid value provided - {exc_message}",
        "KeyError": f"Key not found - {exc_message}",
        "IndexError": f"Index out of range - {exc_message}",
        "AttributeError": f"Attribute does not exist - {exc_message}",
    }

    return descriptions.get(exc_type, f"{exc_type}: {exc_message}")


def _get_error_suggestion(exc: Exception) -> str:
    """Get actionable suggestion for resolving exception."""
    exc_type = type(exc).__name__

    suggestions = {
        "NameError": "Check variable spelling, or define it first. Use 'vars' to see all defined variables.",
        "SyntaxError": "Check for missing operands, unclosed brackets, or invalid Python syntax. Review the Python syntax rules.",
        "TypeError": "Ensure operands are compatible types. Convert types explicitly if needed (e.g., str(5) or int('5')).",
        "ZeroDivisionError": "Check your divisor value before performing division. Ensure denominator is not zero.",
        "ImportError": "If this is a security block, use only whitelisted modules. Type 'help' to see allowed modules.",
        "ValueError": "Verify that the value matches the expected format or range for the operation.",
        "KeyError": "Check that the key exists in the dictionary. Use 'in' operator to verify before accessing.",
        "IndexError": "Ensure the index is within valid range (0 to len-1 for lists). Check list length first.",
        "AttributeError": "Verify the object has the attribute. Use dir() or help() to see available attributes.",
    }

    return suggestions.get(exc_type, "Review the error message and check your code logic.")


def _extract_name_from_error(error_msg: str) -> str:
    """Extract variable name from NameError message."""
    # NameError messages typically: "name 'varname' is not defined"
    if "'" in error_msg:
        parts = error_msg.split("'")
        if len(parts) >= 2:
            return parts[1]
    return "unknown"


def format_variable_list(variables: List[Tuple[str, Any, Dict[str, Any]]]) -> str:
    """Format variables as readable table.

    Args:
        variables: List of (name, value, metadata) tuples

    Returns:
        Formatted string with table showing variables

    Example output:
        +--------+-------+---------+---------------------+---------------------+
        | Name   | Type  | Value   | Created             | Modified            |
        +--------+-------+---------+---------------------+---------------------+
        | x      | int   | 10      | 2025-12-27 10:00:00 | 2025-12-27 10:00:00 |
        +--------+-------+---------+---------------------+---------------------+
    """
    if not variables:
        return "No variables in session."

    # Calculate column widths
    name_width = max(len("Name"), max(len(v[0]) for v in variables))
    type_width = max(len("Type"), max(len(v[2]["type"]) for v in variables))
    value_width = 20  # Fixed width for value, will truncate if needed

    # Build header
    separator = f"+{'-' * (name_width + 2)}+{'-' * (type_width + 2)}+{'-' * (value_width + 2)}+{'-' * 21}+{'-' * 21}+"
    header = f"| {'Name':<{name_width}} | {'Type':<{type_width}} | {'Value':<{value_width}} | {'Created':<19} | {'Modified':<19} |"

    lines = [separator, header, separator]

    # Add variable rows
    for name, value, metadata in variables:
        value_str = _truncate_value(str(value), value_width)
        # Convert ISO format to space-separated format
        created = metadata["created"][:19].replace('T', ' ')
        modified = metadata["modified"][:19].replace('T', ' ')

        row = f"| {name:<{name_width}} | {metadata['type']:<{type_width}} | {value_str:<{value_width}} | {created:<19} | {modified:<19} |"
        lines.append(row)

    lines.append(separator)

    return "\n".join(lines)


def _truncate_value(value_str: str, max_length: int) -> str:
    """Truncate long value strings with ellipsis."""
    if len(value_str) <= max_length:
        return value_str
    return value_str[:max_length - 3] + "..."


def format_command_history(history: List[Dict[str, Any]], limit: int = 10) -> str:
    """Format command history as numbered list.

    Args:
        history: List of command history entries
        limit: Maximum number of commands to display

    Returns:
        Formatted string with command history
    """
    if not history:
        return "No command history."

    # Take last N commands
    recent = history[-limit:] if len(history) > limit else history

    lines = ["Command History:"]
    for entry in recent:
        cmd_id = entry.get("id", "?")
        command = entry.get("command", "")
        # Truncate long commands
        if len(command) > 60:
            command = command[:57] + "..."
        lines.append(f"  [{cmd_id}] {command}")

    if len(history) > limit:
        lines.append(f"  ... ({len(history) - limit} more commands)")

    return "\n".join(lines)


def format_help_message() -> str:
    """Generate help text with available commands.

    Returns:
        Multi-line help string with command documentation
    """
    help_text = """
Available Commands:
  help              Show this help message
  exit, quit        Exit the console
  vars              List all variables in current session
  clear             Clear all variables (with confirmation)
  save <filename>   Save session to JSON file
  load <filename>   Load session from JSON file
  history           Show command history

Python Code:
  Type any valid Python expression or statement to execute.
  Multi-line input is supported (functions, classes, loops).
  The console automatically detects incomplete statements.

Examples:
  >>> 2 + 2
  4
  >>> x = 10
  >>> def greet(name):
  ...     return f"Hello, {name}!"
  ...
  >>> greet("Alice")
  'Hello, Alice!'

Security:
  Safe modules: math, datetime, json, itertools, collections, re, random
  Blocked modules: os, sys, subprocess, socket (for security)

  Attempting to import blocked modules will display a security warning.

Tips:
  - Use 'vars' to inspect current session state
  - Use 'save' to preserve your work
  - Press Ctrl+C to interrupt long-running code
  - All errors are caught - the console never crashes
"""
    return help_text.strip()
