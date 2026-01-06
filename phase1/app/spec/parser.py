"""Parser for converting user input into specifications."""

import re
from typing import Optional

from core.models.spec_models import Operation, Specification


class ParseError(Exception):
    """Raised when input cannot be parsed into a valid specification."""
    pass


class SpecParser:
    """
    Parses natural language input into structured specifications.

    This is the SPEC layer - transforms intent into structure WITHOUT execution.
    """

    def parse(self, user_input: str) -> Specification:
        """
        Parse user input into a Specification.

        Args:
            user_input: Raw text from user

        Returns:
            Structured Specification

        Raises:
            ParseError: If input cannot be parsed
        """
        text = user_input.strip().lower()

        if not text:
            raise ParseError("Empty input")

        # Detect operation
        if text in ["exit", "quit", "q"]:
            return Specification(operation=Operation.EXIT)

        if text in ["list", "list tasks", "show tasks", "show all"]:
            return Specification(operation=Operation.LIST)

        # Parse ADD operation
        add_match = re.match(r'^(?:add|create|new)\s+(?:task:?\s*)?(.+)$', text)
        if add_match:
            task_title = add_match.group(1).strip()
            if not task_title:
                raise ParseError("Task title cannot be empty")
            return Specification(
                operation=Operation.ADD,
                task_title=task_title
            )

        # Parse COMPLETE operation
        complete_match = re.match(r'^(?:complete|done|finish)\s+(?:task\s+)?(\d+)$', text)
        if complete_match:
            task_id = int(complete_match.group(1))
            return Specification(
                operation=Operation.COMPLETE,
                task_id=task_id
            )

        # No pattern matched
        raise ParseError(
            f"Could not parse: '{user_input}'. "
            "Try: 'add task: <title>', 'list', 'complete <id>', 'exit'"
        )
