"""Main entry point with Phase 2 intelligence.

This is the enhanced CLI that supports both:
- Phase 1: Direct deterministic command execution
- Phase 2: AI-powered reasoning and planning
"""
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.todo_cli import TodoCLI as Phase1CLI
from src.intelligence.phase2.cli import Phase2CLI


class IntegratedCLI:
    """Integrated CLI with Phase 1 and Phase 2 support."""

    WELCOME_MESSAGE = """
╔══════════════════════════════════════════════════════════╗
║              Spec-Driven Todo - Phase 2 Enabled           ║
║                                                              ║
║  A natural language todo system with AI-powered reasoning  ║
╚════════════════════════════════════════════════════════╝

Modes:
  - Phase 2 (AI Mode): High-level intent with automatic planning
  - Phase 1 (Direct Mode): Deterministic command execution

Type 'help' for available commands or 'phase2'/'phase1' to switch.
"""

    def __init__(self):
        """Initialize integrated CLI with both Phase 1 and Phase 2."""
        # Phase 1 components
        from src.task_store import TaskStore
        from src.input_parser import InputParser
        from src.todo_executor import TodoExecutor

        store = TaskStore()
        parser = InputParser()
        executor = TodoExecutor(store, parser)

        # Initialize both CLIs
        self.phase1_cli = Phase1CLI(store=store, executor=executor, parser=parser)
        self.phase2_cli = Phase2CLI(phase1_executor=executor)

        # Default to Phase 2
        self.use_phase2 = True
        self.running = False

    def run(self):
        """Run integrated REPL loop."""
        self.running = True
        print(self.WELCOME_MESSAGE)
        print()

        while self.running:
            try:
                # Prompt for input
                mode_indicator = "[AI]" if self.use_phase2 else "[Direct]"
                raw_input = input(f"{mode_indicator} > ").strip()

                if not raw_input:
                    continue

                # Check for mode toggle
                if raw_input.lower() in ["phase1", "direct"]:
                    self.use_phase2 = False
                    print("Switched to Phase 1 Direct Mode")
                    continue
                elif raw_input.lower() in ["phase2", "ai", "intelligent"]:
                    self.use_phase2 = True
                    print("Switched to Phase 2 AI Mode")
                    continue

                # Route to appropriate processor
                if self.use_phase2:
                    result = self.phase2_cli.execute_single(raw_input, use_phase2=True)
                else:
                    # Use Phase 1 directly
                    result = self.phase1_cli.execute(raw_input)

                # Display result
                print(result)
                print()

                # Check for exit
                if self._should_exit(raw_input, result):
                    break

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

            except EOFError:
                print("\nGoodbye!")
                break

            except Exception as e:
                print(f"An error occurred: {e}")
                print("Type 'help' for available commands.")

    def _should_exit(self, user_input: str, result: str) -> bool:
        """Check if should exit application."""
        return user_input.lower() in ["exit", "quit", "bye"] or \
               "Goodbye" in result or "Exiting" in result


def main():
    """Entry point for integrated application."""
    cli = IntegratedCLI()
    cli.run()


if __name__ == "__main__":
    main()
