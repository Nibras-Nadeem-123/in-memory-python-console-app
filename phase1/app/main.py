#!/usr/bin/env python3
"""
Phase 1: Console-based Spec-Driven Todo Application

Entry point for the application.

Usage:
    python phase1/app/main.py

Architecture:
    Input → [SpecParser: SPEC LAYER] → Specification
          ↓
    Specification → [Engine: EXECUTION LAYER] → State Changes
          ↓
    Output ← [ConsoleUI] ← Results
"""

import sys
from pathlib import Path

# Add parent directory to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.context import AppContext
from app.engine import Engine
from app.spec.parser import ParseError
from app.utils.console import ConsoleUI


def main():
    """Main entry point - runs the REPL loop."""
    # Initialize application
    context = AppContext()
    engine = Engine(context)
    ui = ConsoleUI()

    # Show welcome
    ui.print_welcome()

    # REPL loop
    while True:
        try:
            # Read user input
            user_input = ui.read_input()

            if not user_input:
                continue

            # SPEC PHASE: Parse input → Specification (no side effects)
            spec = context.parser.parse(user_input)

            # EXECUTION PHASE: Execute specification → State changes
            should_continue = engine.execute_specification(spec)

            if not should_continue:
                print("\nGoodbye!")
                break

        except ParseError as e:
            ui.print_error(str(e))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()
