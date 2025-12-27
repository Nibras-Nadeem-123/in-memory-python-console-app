"""Input parsing for Python code and system commands."""

import ast
from typing import List, Tuple


def is_complete_statement(code: str) -> bool:
    """Check if Python code is syntactically complete.

    Uses AST parsing to detect incomplete syntax (unclosed brackets,
    unfinished blocks, multi-line strings).

    Args:
        code: Python source code string

    Returns:
        True if code is complete and can be executed,
        False if more input is needed

    Examples:
        >>> is_complete_statement("x = 10")
        True
        >>> is_complete_statement("def foo():")
        False
        >>> is_complete_statement("[1, 2,")
        False
    """
    if not code.strip():
        return True  # Empty input is "complete"

    # Try to compile with 'exec' mode
    try:
        compile(code, '<stdin>', 'exec')
        # Successfully compiled - check if it's an incomplete block
        # Incomplete blocks end with ':' and have no body
        lines = code.rstrip().split('\n')
        if lines:
            last_line = lines[-1].rstrip()
            # Check if last line ends with ':' indicating incomplete block
            if last_line.endswith(':'):
                return False
        return True
    except SyntaxError as e:
        # Check if error indicates incomplete input
        error_msg = str(e).lower()

        # Specific patterns that indicate incomplete code
        incomplete_patterns = [
            'unexpected eof',
            'eof while',
            'incomplete',
            'expected',
            'unterminated',
            'was never closed'
        ]

        if any(pattern in error_msg for pattern in incomplete_patterns):
            return False

        # Check for unclosed brackets/parens/braces by counting
        open_brackets = code.count('[') - code.count(']')
        open_parens = code.count('(') - code.count(')')
        open_braces = code.count('{') - code.count('}')

        if open_brackets > 0 or open_parens > 0 or open_braces > 0:
            return False

        # Other syntax errors mean code is malformed but "complete" (user made a mistake)
        return True
    except Exception:
        # Other exceptions - treat as complete
        return True


def detect_system_command(line: str) -> Tuple[str | None, List[str]]:
    """Parse system commands from input line.

    System commands are special console commands (help, exit, vars, etc.)
    that are not Python code.

    Args:
        line: User input line

    Returns:
        Tuple of (command_name, arguments) if system command detected,
        or (None, []) if line is Python code

    Examples:
        >>> detect_system_command("help")
        ('help', [])
        >>> detect_system_command("save session.json")
        ('save', ['session.json'])
        >>> detect_system_command("x = 10")
        (None, [])
    """
    line = line.strip()

    if not line:
        return (None, [])

    # List of system commands
    system_commands = {
        "help", "exit", "quit",
        "vars", "clear",
        "save", "load",
        "history"
    }

    parts = line.split()
    command = parts[0].lower()

    if command in system_commands:
        args = parts[1:] if len(parts) > 1 else []
        return (command, args)

    return (None, [])
