"""Phase 2 CLI Interface.

Integrates Phase 2 intelligence with console interface.
Maintains user interaction and workflow orchestration.
"""
from typing import Optional

from .workflow_manager import Phase2WorkflowManager
from .data_models import Phase2Context


class Phase2CLI:
    """CLI interface for Phase 2 intelligence system.

    Provides interactive command processing with:
    - Intent parsing and clarification
    - Plan generation and review
    - Plan execution with Phase 1 integration
    - State tracking and history
    """

    WELCOME_MESSAGE = """Welcome to Phase 2 Intelligent Todo System!

This system uses AI-powered reasoning to transform high-level
intent into executable plans.

Examples:
  - "organize my tasks for today"
  - "help me prioritize my work"
  - "create tasks for project X"

You can also use direct Phase 1 commands:
  - "add task: write documentation"
  - "list tasks"
  - "complete task 1"
"""

    def __init__(self, phase1_executor=None):
        """Initialize Phase 2 CLI.

        Args:
            phase1_executor: Phase 1 TodoExecutor for plan execution.
        """
        self.workflow_manager = Phase2WorkflowManager(phase1_executor)
        self.running = False
        self.use_phase2 = True  # Toggle between Phase 1 and Phase 2

    def run(self):
        """Run main REPL loop for Phase 2."""
        self.running = True
        print(self.WELCOME_MESSAGE)
        print()

        while self.running:
            try:
                # Prompt for input
                mode_indicator = "[AI]" if self.use_phase2 else "[Phase 1]"
                raw_input = input(f"{mode_indicator} > ").strip()

                if not raw_input:
                    continue

                # Check for mode toggle
                if raw_input.lower() in ["phase1", "direct"]:
                    self.use_phase2 = False
                    print("Switched to Phase 1 direct mode")
                    continue
                elif raw_input.lower() in ["phase2", "ai", "intelligent"]:
                    self.use_phase2 = True
                    print("Switched to Phase 2 AI mode")
                    continue

                # Process input
                if self.use_phase2:
                    result = self._process_phase2_input(raw_input)
                else:
                    result = self._process_phase1_input(raw_input)

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
                print("Please try again or type 'help' for assistance.")

    def _process_phase2_input(self, user_input: str) -> str:
        """Process user input through Phase 2 intelligence pipeline.

        Args:
            user_input: Raw user command.

        Returns:
            Formatted result message.
        """
        # Check for simple commands
        lower_input = user_input.lower()

        if lower_input == "help":
            return self._get_help()
        elif lower_input == "status":
            return self._get_status()
        elif lower_input == "reset":
            self.workflow_manager.reset_workflow()
            return "Workflow reset. Ready for new intent."
        elif lower_input in ["exit", "quit", "bye"]:
            return "Exiting..."

        # Process through Phase 2 pipeline
        result = self.workflow_manager.process_intent(
            user_input=user_input,
            existing_context=None,
            auto_approve=True  # Auto-approve for testing
        )

        # Handle different result states
        if result["status"] == "needs_clarification":
            return self._handle_clarification_needed(result)
        elif result["status"] == "planning_failed":
            error_msg = result.get("error", "Unknown error")
            return f"Planning failed: {error_msg}\n" \
                   f"Please rephrase your request or try a simpler one."
        elif result["status"] == "plan_rejected":
            feedback = result.get("review_result", {}).get("user_feedback", "No feedback")
            return f"Plan was rejected: {feedback}\n" \
                   f"Please provide feedback or try a different request."
        elif result["status"] == "completed":
            return self._format_completion_result(result)
        elif result["status"] == "error":
            error_msg = result.get("error", "Unknown error")
            return f"Error: {error_msg}"
        else:
            return f"Unknown status: {result['status']}"

    def _process_phase1_input(self, user_input: str) -> str:
        """Process user input through Phase 1 direct execution.

        Args:
            user_input: Raw user command.

        Returns:
            Formatted result message.
        """
        # Use Phase 1 executor directly
        try:
            result = self.workflow_manager.executor.phase1_executor.execute(user_input)

            # Format result message
            message = result.message

            # Show data if available
            if result.success and result.data:
                if "tasks" in result.data:
                    tasks = result.data["tasks"]
                    if not tasks:
                        message += "\nNo tasks found."
                    else:
                        message += "\n"
                        for task in tasks:
                            status_icon = "☑" if task.status == "COMPLETED" else "☐"
                            message += f"\n  {task.id}. [{status_icon}] {task.title}"
                            if task.priority != "MEDIUM":
                                message += f" [{task.priority}]"

            return message

        except Exception as e:
            return f"Error executing command: {e}"

    def _handle_clarification_needed(self, result: dict) -> str:
        """Handle clarification request from workflow.

        Args:
            result: Processing result with clarifications.

        Returns:
            Message asking for clarification.
        """
        clarifications = result.get("clarifications", [])

        if not clarifications:
            return "Intent requires clarification but no questions generated."

        # Get first unanswered clarification
        for clarification in clarifications:
            if not clarification.response:
                return (
                    f"\nI need clarification to proceed:\n"
                    f"  {clarification.question}\n\n"
                    f"Type your answer to continue."
                )

        return "Clarifications already provided. Continuing..."

    def _format_completion_result(self, result: dict) -> str:
        """Format completed execution result for display.

        Args:
            result: Processing result with execution data.

        Returns:
            Formatted completion message.
        """
        message = result.get("message", "Processing complete")

        # Add additional details if available
        if "intent" in result:
            intent = result["intent"]
            if intent:
                message += f"\n\nIntent type: {intent.type.value}"
                if intent.parameters:
                    message += f"\nParameters extracted: {list(intent.parameters.keys())}"

        if "execution_result" in result:
            exec_result = result["execution_result"]
            if exec_result and exec_result.errors:
                message += f"\n\nWarnings: {len(exec_result.errors)} errors encountered"

        return message

    def _get_help(self) -> str:
        """Get help message for Phase 2 commands."""
        return """
=== Phase 2 Commands ===

AI Commands (Phase 2):
  - "organize my tasks for today"
  - "help me prioritize my work"
  - "create tasks for project X"
  - "plan my day"

Direct Commands (Phase 1):
  - "add task: write documentation"
  - "add task: meeting prep with priority high"
  - "list tasks"
  - "list pending tasks"
  - "complete task 1"
  - "delete task 1"
  - "update task 1 title to new title"
  - "search documentation"

System Commands:
  - "phase1" or "direct": Switch to Phase 1 direct mode
  - "phase2" or "ai": Switch to Phase 2 AI mode
  - "status": Show current workflow state
  - "reset": Reset current workflow
  - "help": Show this help
  - "exit" or "quit": Exit the application
"""

    def _get_status(self) -> str:
        """Get current workflow status."""
        state = self.workflow_manager.get_workflow_state()

        if state["status"] == "not_initialized":
            return "No active workflow. Ready for new input."

        lines = [
            "=== Workflow Status ===",
            f"Execution ID: {state['execution_id']}",
            f"Current State: {state['workflow_state']}",
            "",
            "Artifacts:",
            f"  - Intent: {'Yes' if state['has_intent'] else 'No'}",
            f"  - Specification: {'Yes' if state['has_specification'] else 'No'}",
            f"  - Plan: {'Yes' if state['has_plan'] else 'No'}",
            f"  - Execution Results: {'Yes' if state['has_execution_results'] else 'No'}",
            "",
            f"Clarifications Pending: {state['clarifications_pending']}",
            f"Reasoning Steps: {state['reasoning_steps']}"
        ]

        return "\n".join(lines)

    def _should_exit(self, user_input: str, result: str) -> bool:
        """Check if should exit application."""
        return user_input.lower() in ["exit", "quit", "bye"] or \
               "Goodbye" in result or "Exiting" in result

    def execute_single(self, user_input: str, use_phase2: bool = True) -> str:
        """Execute a single command (for testing).

        Args:
            user_input: The command to execute.
            use_phase2: Whether to use Phase 2 intelligence.

        Returns:
            The execution result message.
        """
        if use_phase2:
            return self._process_phase2_input(user_input)
        else:
            return self._process_phase1_input(user_input)


def main():
    """Entry point for Phase 2 application."""
    import sys
    import os

    # Add parent directories to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, parent_dir)

    from src.todo_executor import TodoExecutor
    from src.task_store import TaskStore
    from src.input_parser import InputParser

    # Create Phase 1 components
    store = TaskStore()
    parser = InputParser()
    executor = TodoExecutor(store, parser)

    # Run Phase 2 CLI with Phase 1 executor
    cli = Phase2CLI(phase1_executor=executor)
    cli.run()


if __name__ == "__main__":
    main()
