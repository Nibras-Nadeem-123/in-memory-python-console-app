"""
Main entry point for the Intelligence Framework.

This module provides example usage and demonstrates the full capability
of the intelligence system, from goal input to outcome.

Example:
    python -m src.intelligence.main
"""
from __future__ import annotations

import os
import sys
from typing import Any

from src.intelligence.context import ExecutionContext
from src.intelligence.engine import IntelligenceEngine, Goal
from src.intelligence.runtime import RuntimeEngine, ExecutionPlan, Action, Outcome
from src.intelligence.skills import (
    Skill,
    SkillRegistry,
    SYSTEM_SKILL_REGISTRY,
)


# =============================================================================
# Example Skills
# =============================================================================

class EchoSkill(Skill):
    """A simple skill that echoes its input."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echoes the input message back"

    def execute(self, context: ExecutionContext, **kwargs: Any) -> str:
        message = kwargs.get("message", "")
        context.add_event("skill_start", {"skill": self.name, "message": message})
        context.state["last_echo"] = message
        context.add_event("skill_success", {"skill": self.name})
        return message


class ReadFileSkill(Skill):
    """A skill to read the content of a file."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads and returns the contents of a file"

    def execute(self, context: ExecutionContext, **kwargs: Any) -> str:
        file_path = kwargs.get("file_path")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("`file_path` string argument is required.")

        context.add_event("skill_start", {"skill": self.name, "path": file_path})

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            context.add_event("skill_success", {"skill": self.name, "char_count": len(content)})
            context.state["last_file_content"] = content
            return content
        except FileNotFoundError:
            error = f"File not found: {file_path}"
            context.add_event("skill_failure", {"skill": self.name, "error": error})
            raise FileNotFoundError(error)


class SummarizeTextSkill(Skill):
    """A skill to summarize text (simplified implementation)."""

    @property
    def name(self) -> str:
        return "summarize_text"

    @property
    def description(self) -> str:
        return "Creates a summary of the input text"

    def execute(self, context: ExecutionContext, **kwargs: Any) -> str:
        text = kwargs.get("text")
        if not text or not isinstance(text, str):
            # Try to get text from context state
            text = context.state.get("last_file_content")
            if not text or not isinstance(text, str):
                raise ValueError(
                    "`text` argument or 'last_file_content' in state is required."
                )

        context.add_event("skill_start", {"skill": self.name, "input_length": len(text)})

        # Simple summarization: take first 3 lines
        lines = text.strip().splitlines()
        summary = "\n".join(lines[:3])

        context.add_event("skill_success", {"skill": self.name, "summary_length": len(summary)})
        context.state["last_summary"] = summary
        return summary


# =============================================================================
# Setup Functions
# =============================================================================

def setup_skills(registry: SkillRegistry | None = None) -> SkillRegistry:
    """
    Register all example skills with a registry.

    Args:
        registry: Optional registry to use (creates new if not provided)

    Returns:
        The registry with skills registered
    """
    if registry is None:
        registry = SkillRegistry()

    registry.register(EchoSkill())
    registry.register(ReadFileSkill())
    registry.register(SummarizeTextSkill())

    return registry


def create_engine(registry: SkillRegistry | None = None) -> IntelligenceEngine:
    """
    Create a fully configured intelligence engine.

    Args:
        registry: Optional skill registry (creates new with example skills if not provided)

    Returns:
        Configured IntelligenceEngine
    """
    if registry is None:
        registry = setup_skills()

    return IntelligenceEngine(registry)


# =============================================================================
# Example Workflows
# =============================================================================

def example_basic_workflow() -> None:
    """Demonstrate basic workflow: process a simple goal."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Goal Processing")
    print("=" * 60)

    # Setup
    registry = setup_skills()
    engine = IntelligenceEngine(registry)

    # Process a goal
    goal = "summarize the readme file"
    print(f"\nGoal: {goal}")

    # Create a dummy README for the example
    readme_content = """# Intelligence Framework

A reusable, spec-driven intelligence framework for AI-driven development.

## Features
- Context and memory management
- Skill-based execution
- Intent parsing and planning
- Modular agent framework
"""

    # Write temporary README
    with open("README.md", "w") as f:
        f.write(readme_content)

    try:
        # Process the goal
        outcome = engine.process(goal)

        # Display results
        print(f"\nStatus: {outcome.status.value}")
        print(f"Steps Executed: {outcome.steps_executed}")
        print(f"Execution Time: {outcome.execution_time_ms:.2f}ms")

        if outcome.success:
            print(f"\nResult:\n{outcome.result}")
        else:
            print(f"\nError: {outcome.error}")

        # Show history
        if outcome.context:
            print("\nExecution History:")
            for event in outcome.context.history[:5]:  # First 5 events
                print(f"  [{event.type}] {event.details}")

    finally:
        # Cleanup
        if os.path.exists("README.md"):
            os.remove("README.md")


def example_manual_plan() -> None:
    """Demonstrate manual plan creation and execution."""
    print("\n" + "=" * 60)
    print("Example 2: Manual Plan Execution")
    print("=" * 60)

    # Setup
    registry = setup_skills()
    runtime = RuntimeEngine(registry)

    # Create a manual plan
    plan = ExecutionPlan(
        actions=[
            Action(skill="echo", args={"message": "Hello, World!"}),
            Action(skill="echo", args={"message": "This is step 2"}),
        ],
        metadata={"example": "manual_plan"},
    )

    print(f"\nPlan: {len(plan)} actions")
    for i, action in enumerate(plan.actions):
        print(f"  {i + 1}. {action.skill}({action.args})")

    # Execute
    outcome = runtime.execute_plan(plan, goal={"description": "echo example"})

    # Display results
    print(f"\nStatus: {outcome.status.value}")
    print(f"Final Result: {outcome.result}")

    if outcome.context:
        print(f"State: {outcome.context.state}")


def example_context_persistence() -> None:
    """Demonstrate context save and load."""
    print("\n" + "=" * 60)
    print("Example 3: Context Persistence")
    print("=" * 60)

    # Create a context with some state
    context = ExecutionContext.create(goal={"description": "test persistence"})
    context.state["data"] = {"key": "value", "count": 42}
    context.add_event("custom_event", {"info": "some data"})
    context.status = "success"

    print(f"\nOriginal Context ID: {context.execution_id}")
    print(f"Original State: {context.state}")

    # Save to file
    save_path = "/tmp/test_context.json"
    context.save(save_path)
    print(f"\nSaved to: {save_path}")

    # Load from file
    loaded = ExecutionContext.load(save_path)
    print(f"\nLoaded Context ID: {loaded.execution_id}")
    print(f"Loaded State: {loaded.state}")
    print(f"History Events: {len(loaded.history)}")

    # Cleanup
    if os.path.exists(save_path):
        os.remove(save_path)


def example_error_handling() -> None:
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)

    # Setup
    registry = setup_skills()
    engine = IntelligenceEngine(registry)

    # Try to read a non-existent file
    goal = "read the nonexistent_file.txt"
    print(f"\nGoal: {goal}")

    outcome = engine.process(goal)

    print(f"\nStatus: {outcome.status.value}")
    if outcome.error:
        print(f"Error: {outcome.error}")

    if outcome.context:
        # Show failure events
        failure_events = [e for e in outcome.context.history if "failure" in e.type]
        print(f"\nFailure Events: {len(failure_events)}")
        for event in failure_events:
            print(f"  [{event.type}] {event.details}")


def run_all_examples() -> None:
    """Run all example workflows."""
    print("\n" + "#" * 60)
    print("# Intelligence Framework - Example Usage")
    print("#" * 60)

    example_basic_workflow()
    example_manual_plan()
    example_context_persistence()
    example_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point with SDD CLI integration."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="intelligence",
        description="Intelligence Framework with Spec-Driven Development"
    )

    parser.add_argument(
        "--sdd", "-s",
        action="store_true",
        help="Use SDD CLI mode"
    )

    parser.add_argument(
        "--examples", "-e",
        action="store_true",
        help="Run example workflows"
    )

    args = parser.parse_args()

    if args.sdd:
        # Use SDD CLI
        from .sdd import cli
        sys.argv[0] = "sdd"  # Mock program name
        cli.main()
    elif args.examples:
        # Run examples
        run_all_examples()
    else:
        # Default to examples
        run_all_examples()


if __name__ == "__main__":
    main()
