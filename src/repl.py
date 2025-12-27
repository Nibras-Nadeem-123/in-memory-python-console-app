"""Main REPL loop with multi-line support and command routing."""

import sys
from typing import Any, Dict

from src.executor import execute_code
from src.formatter import format_help_message, format_variable_list
from src.parser import detect_system_command, is_complete_statement
from src.session_manager import clear_session, list_variables


def repl_loop(context: Dict[str, Any]) -> None:
    """Main REPL loop with multi-line support.

    Implements state machine for SINGLE_LINE vs MULTI_LINE modes.
    Handles input, execution, output, and errors.

    Args:
        context: Execution environment with session_state, globals, locals

    Note:
        Never returns normally - exits via system command or exception
    """
    # State machine: SINGLE_LINE or MULTI_LINE
    mode = "SINGLE_LINE"
    buffer = []

    print("Welcome to Python Console v1.0!")
    print("Type 'help' for available commands, 'exit' to quit.")
    print()

    while True:
        try:
            # Display appropriate prompt
            if mode == "SINGLE_LINE":
                prompt = ">>> "
            else:
                prompt = "... "

            # Get input
            try:
                line = input(prompt)
            except EOFError:
                # Ctrl+D pressed
                print("\nGoodbye!")
                sys.exit(0)

            # Check for system command (only in SINGLE_LINE mode)
            if mode == "SINGLE_LINE":
                command, args = detect_system_command(line)
                if command:
                    output = process_system_command(command, args, context)
                    if output == "EXIT":
                        print("Goodbye!")
                        sys.exit(0)
                    else:
                        if output:
                            print(output)
                        continue

            # Handle Python code
            if mode == "SINGLE_LINE":
                # Check if statement is complete
                if is_complete_statement(line):
                    # Execute immediately
                    result = execute_code(line, context)
                    _display_result(result)
                else:
                    # Start multi-line mode
                    mode = "MULTI_LINE"
                    buffer = [line]
            else:
                # Multi-line mode
                buffer.append(line)

                # Check if empty line (end of multi-line input)
                if line.strip() == "":
                    # Try to execute buffer
                    code = "\n".join(buffer)
                    if code.strip():
                        result = execute_code(code, context)
                        _display_result(result)

                    # Reset to single-line mode
                    mode = "SINGLE_LINE"
                    buffer = []
                else:
                    # Check if buffer is now complete
                    code = "\n".join(buffer)
                    if is_complete_statement(code):
                        # Keep accumulating - might need more lines
                        pass

        except KeyboardInterrupt:
            # Ctrl+C pressed
            print("\nKeyboardInterrupt")
            # Reset state
            mode = "SINGLE_LINE"
            buffer = []
            continue

        except Exception as e:
            # Unexpected error in REPL itself
            print(f"REPL Error: {e}")
            mode = "SINGLE_LINE"
            buffer = []
            continue


def process_system_command(
    command: str,
    args: list[str],
    context: Dict[str, Any]
) -> str:
    """Execute system commands.

    Args:
        command: Command name (help, exit, vars, etc.)
        args: Command arguments
        context: Execution environment

    Returns:
        Output string or "EXIT" to terminate REPL
    """
    if command in ("exit", "quit"):
        return "EXIT"

    elif command == "help":
        return format_help_message()

    elif command == "vars":
        state = context["session_state"]
        vars_list = list_variables(state)
        return format_variable_list(vars_list)

    elif command == "clear":
        state = context["session_state"]
        count = len(state)
        if count == 0:
            return "No variables to clear."

        # Confirmation prompt
        response = input(f"Warning: This will delete all {count} variables. Continue? (y/n): ")
        if response.lower() in ("y", "yes"):
            cleared = clear_session(state)
            return f"Cleared {cleared} variables."
        else:
            return "Clear cancelled."

    elif command == "save":
        if not args:
            return "Error: save requires a filename. Usage: save <filename>"
        return f"Save command not yet implemented. Would save to: {args[0]}"

    elif command == "load":
        if not args:
            return "Error: load requires a filename. Usage: load <filename>"
        return f"Load command not yet implemented. Would load from: {args[0]}"

    elif command == "history":
        return "Command history not yet implemented."

    else:
        return f"Unknown command: {command}. Type 'help' for available commands."


def _display_result(result: Any) -> None:
    """Display execution result.

    Args:
        result: ExecutionResult from execute_code
    """
    if result.status == "error":
        # Display error message
        print(result.error)
    elif result.result is not None:
        # Display result for expressions
        print(result.result)
    # For successful statements with no result, display nothing
