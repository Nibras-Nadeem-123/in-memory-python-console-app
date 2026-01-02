"""CLI interface for the todo system.

Provides a REPL loop for user interaction.
"""

import sys
from typing import Optional

from src.input_parser import InputParser
from src.task_store import TaskStore
from src.todo_executor import ExecutionResult, TodoExecutor

WELCOME_MESSAGE = """Welcome to Spec-Driven Todo!

A natural language todo list that understands you.
Type 'help' for available commands."""


class TodoCLI:
    """Interactive CLI for the todo system."""

    def __init__(
        self,
        store: Optional[TaskStore] = None,
        executor: Optional[TodoExecutor] = None,
        parser: Optional[InputParser] = None
    ) -> None:
        """Initialize the CLI.

        Args:
            store: Optional pre-configured TaskStore.
            executor: Optional pre-configured TodoExecutor.
            parser: Optional pre-configured InputParser.
        """
        self.store = store or TaskStore()
        self.parser = parser or InputParser()
        self.executor = executor or TodoExecutor(self.store, self.parser)
        self.running = False

    def run(self) -> None:
        """Run the main REPL loop."""
        self.running = True
        print(WELCOME_MESSAGE)
        print()

        while self.running:
            try:
                raw_input = input("> ").strip()

                if not raw_input:
                    print("Please enter a command. Type 'help' for available commands.")
                    continue

                result = self.executor.execute(raw_input)

                # Print the result message
                print(result.message)

                # Check if we should exit
                if result.success and result.message == "Goodbye!":
                    break

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

            except EOFError:
                print("\nGoodbye!")
                break

            except Exception as e:
                # Unexpected error - show friendly message
                print(f"An error occurred: {e}")
                print("Type 'help' for available commands.")

    def execute(self, raw_input: str) -> ExecutionResult:
        """Execute a single command (for testing).

        Args:
            raw_input: The command to execute.

        Returns:
            The ExecutionResult.
        """
        return self.executor.execute(raw_input)


def main() -> None:
    """Entry point for the todo application."""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()
