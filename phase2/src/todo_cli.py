# src/todo_cli.py

from src.input_parser import InputParser
from src.todo_executor import TodoExecutor
from src.task_store import TaskStore
from src.task_model import Command, CommandResult, OperationType, ParseError
from src.todo_utils import format_task_list

# Attempt to import rich, fall back to basic print if not available
try:
    from rich.console import Console
    from rich.text import Text
    console = Console()
except ImportError:
    console = None

def display_welcome():
    """Prints a welcome message and basic instructions."""
    welcome_banner = """
╔══════════════════════════════════════════════╗
║   Spec-Driven Todo Console Application      ║
╚══════════════════════════════════════════════╝
"""
    instructions = """
Type commands in natural language.
Examples: 'add task: write docs', 'list tasks', 'complete task 1'
Type 'help' for more examples, 'exit' to quit.
"""
    if console:
        console.print(Text(welcome_banner, style="bold green"))
        console.print(Text(instructions, style="yellow"))
    else:
        print(welcome_banner)
        print(instructions)

def display_error(message: str, suggestion: str = None):
    """Formats and prints an error message."""
    if console:
        console.print(Text(f"✗ Error: {message}", style="bold red"))
        if suggestion:
            console.print(Text(f"  Suggestion: {suggestion}", style="yellow"))
    else:
        print(f"✗ Error: {message}")
        if suggestion:
            print(f"  Suggestion: {suggestion}")

def display_result(command: Command, result: CommandResult):
    """
    Formats and prints the result of a command.
    """
    if not result.success:
        display_error(result.message, result.suggestion if isinstance(result, ParseError) else None)
        return
        
    if result.message:
        # For simple success messages or help text
        if command.operation == OperationType.HELP: # Use command.operation directly
             if console:
                 console.print(Text(result.message, style="cyan"))
             else:
                 print(result.message)
        else:
             if console:
                 console.print(Text(f"✓ {result.message}", style="green"))
             else:
                 print(f"✓ {result.message}")

    if result.data:
        # For list/search results
        if console:
            console.print(Text(format_task_list(result.data), style="blue")) # You can choose a different color here
        else:
            print(format_task_list(result.data))

def main():
    """Main entry point for the CLI - runs the REPL loop."""
    store = TaskStore()
    parser = InputParser()
    executor = TodoExecutor(store)

    display_welcome()

    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue

            try:
                command = parser.parse(text)
            except ParseError as e:
                display_error(e.message, e.suggestion)
                continue
            
            if command.operation == OperationType.EXIT:
                if console:
                    console.print(Text("Goodbye!", style="green"))
                else:
                    print("Goodbye!")
                break

            result = executor.execute(command)
            # Pass the command object directly
            display_result(command, result) 

        except KeyboardInterrupt:
            if console:
                console.print(Text("\nGoodbye!", style="green"))
            else:
                print("\nGoodbye!")
            break
        except Exception as e:
            # Catch any other unexpected errors
            display_error(f"An unexpected system error occurred: {e}")

if __name__ == "__main__":
    main()
