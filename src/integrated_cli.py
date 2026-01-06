"""Integrated CLI with Phase 1 and Phase 2 support.

Simple entry point that demonstrates Phase 2 capabilities
while maintaining Phase 1 deterministic execution.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def main():
    """Run integrated CLI with Phase 1 and Phase 2 support."""
    print("=" * 60)
    print("        Spec-Driven Todo - Phase 2 Enabled")
    print(" ")
    print("  A natural language todo system with AI-powered reasoning")
    print("=" * 60)
    print()

    # Import Phase 1 components
    from src.task_store import TaskStore
    from src.input_parser import InputParser
    from src.todo_executor import TodoExecutor

    # Initialize Phase 1
    store = TaskStore()
    parser = InputParser()
    executor = TodoExecutor(store, parser)

    # Import Phase 2
    from src.intelligence.phase2.workflow_manager import Phase2WorkflowManager

    # Initialize Phase 2
    workflow = Phase2WorkflowManager(phase1_executor=executor)

    print("Mode Selection:")
    print("  [1] Phase 2 AI Mode - High-level intent with planning")
    print("  [2] Phase 1 Direct Mode - Deterministic commands")
    print("  [3] Integrated Mode - Both with toggle")
    print()

    # Default to Phase 2
    mode = "3"  # Default to integrated

    try:
        choice = input("Select mode (1/2/3) [default: 3]: ").strip() or mode
        mode = choice
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return

    if mode == "1":
        # Phase 2 only
        print("\n=== Starting Phase 2 AI Mode ===\n")
        run_phase2_only(workflow)

    elif mode == "2":
        # Phase 1 only
        print("\n=== Starting Phase 1 Direct Mode ===\n")
        run_phase1_only(store, executor)

    else:
        # Integrated mode
        print("\n=== Starting Integrated Mode ===\n")
        run_integrated_mode(workflow, executor)


def run_phase2_only(workflow):
    """Run Phase 2 only mode."""
    while True:
        try:
            user_input = input("[AI] > ").strip()

            if not user_input:
                continue

            # Check for simple commands
            lower_input = user_input.lower()
            if lower_input == "help":
                print_phase2_help()
                continue
            elif lower_input in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            # Process through Phase 2
            result = workflow.process_intent(
                user_input=user_input,
                existing_context=None,
                auto_approve=True
            )

            # Display result
            print_result(result)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def run_phase1_only(store, executor):
    """Run Phase 1 only mode."""
    while True:
        try:
            user_input = input("[Direct] > ").strip()

            if not user_input:
                continue

            # Check for simple commands
            lower_input = user_input.lower()
            if lower_input == "help":
                print_phase1_help()
                continue
            elif lower_input in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            # Process through Phase 1
            result = executor.execute(user_input)

            # Display result
            print(result.message)

            # Show tasks if available
            if result.success and result.data and "tasks" in result.data:
                tasks = result.data["tasks"]
                if tasks:
                    print("\n--- Tasks ---")
                    for task in tasks:
                        status_icon = "X" if task.status == "COMPLETED" else "O"
                        print(f"  {task.id}. [{status_icon}] {task.title}")
                        if task.priority != "MEDIUM":
                            print(f"      [{task.priority}]")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def run_integrated_mode(workflow, executor):
    """Run integrated mode with toggle."""
    use_phase2 = True  # Default to Phase 2

    while True:
        try:
            mode_indicator = "[AI]" if use_phase2 else "[Direct]"
            user_input = input(f"{mode_indicator} > ").strip()

            if not user_input:
                continue

            # Check for mode toggle
            lower_input = user_input.lower()
            if lower_input in ["phase1", "direct"]:
                use_phase2 = False
                print("Switched to Phase 1 Direct Mode")
                continue
            elif lower_input in ["phase2", "ai", "intelligent"]:
                use_phase2 = True
                print("Switched to Phase 2 AI Mode")
                continue
            elif lower_input == "help":
                print_integrated_help()
                continue
            elif lower_input in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            # Process based on mode
            if use_phase2:
                result = workflow.process_intent(
                    user_input=user_input,
                    existing_context=None,
                    auto_approve=True
                )
                print_result(result)
            else:
                result = executor.execute(user_input)
                print(result.message)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def print_result(result):
    """Print Phase 2 result."""
    status = result.get("status", "unknown")

    if status == "needs_clarification":
        print("\nI need clarification to proceed:")
        clarifications = result.get("clarifications", [])
        for c in clarifications[:1]:  # Show first one
            print(f"  {c.question}")
        print("\nType your answer to continue.")

    elif status == "planning_failed":
        error = result.get("error", "Unknown error")
        print(f"\nPlanning failed: {error}")
        print("Please rephrase your request or try a simpler one.")

    elif status == "plan_rejected":
        print("\nPlan was rejected")
        print("Please provide feedback or try a different request.")

    elif status == "completed":
        message = result.get("message", "Processing complete")
        print(f"\n{message}")

        # Show additional details
        if "execution_result" in result:
            exec_result = result["execution_result"]
            if exec_result:
                print(f"\nCompleted {exec_result.steps_completed}/{exec_result.steps_total} steps")
                if exec_result.tasks_added > 0:
                    print(f"Tasks added: {exec_result.tasks_added}")
                if exec_result.tasks_completed > 0:
                    print(f"Tasks completed: {exec_result.tasks_completed}")

    elif status == "error":
        error = result.get("error", "Unknown error")
        print(f"\nError: {error}")

    else:
        print(f"\nUnknown status: {status}")


def print_phase2_help():
    """Print Phase 2 help."""
    print("""
=== Phase 2 AI Commands ===

High-Level Intent:
  - "organize my tasks for today"
  - "help me prioritize my work"
  - "create tasks for project X"
  - "plan my day"

System Commands:
  - "help": Show this help
  - "exit": Exit application

Note: Phase 2 uses AI reasoning to understand your intent
and automatically generate plans to execute using Phase 1 commands.
""")


def print_phase1_help():
    """Print Phase 1 help."""
    print("""
=== Phase 1 Direct Commands ===

Task Management:
  - "add task: write documentation"
  - "add task: meeting prep with priority high"
  - "list tasks"
  - "list pending tasks"
  - "list completed tasks"
  - "complete task 1"
  - "delete task 1"
  - "update task 1 title to new title"
  - "update task 1 priority to high"
  - "search documentation"

System Commands:
  - "help": Show this help
  - "exit": Exit application
""")


def print_integrated_help():
    """Print integrated help."""
    print("""
=== Integrated Commands ===

Mode Toggle:
  - "phase1" or "direct": Switch to Phase 1 Direct Mode
  - "phase2" or "ai": Switch to Phase 2 AI Mode

Phase 2 AI Commands:
  - "organize my tasks for today"
  - "help me prioritize my work"

Phase 1 Direct Commands:
  - "add task: write documentation"
  - "list tasks"
  - "complete task 1"

System Commands:
  - "help": Show this help
  - "exit": Exit application
""")


if __name__ == "__main__":
    main()
