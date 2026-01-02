"""Natural language command parser.

Converts user input into structured Intent objects.
"""

import re
from typing import Optional

from src.task_model import Intent


class ParserError(Exception):
    """Base class for parsing errors."""

    def user_message(self) -> str:
        raise NotImplementedError()


class AmbiguousInputError(ParserError):
    """Raised when input is ambiguous or incomplete."""

    def user_message(self) -> str:
        return (
            "I didn't understand. Which task? "
            "Please specify the task title or ID."
        )


class UnknownCommandError(ParserError):
    """Raised when no command pattern matches."""

    def __init__(self, command: str) -> None:
        self.command = command
        super().__init__(f"Unknown command: {command}")

    def user_message(self) -> str:
        return f"Unknown command: '{self.command}'. Type 'help' for available commands."


class MissingTitleError(ParserError):
    """Raised when a title is required but not provided."""

    def user_message(self) -> str:
        return "Please provide a task title"


# Action patterns: action -> list of regex patterns (first match wins)
ACTION_PATTERNS: dict[str, list[str]] = {
    "add": [
        r"^add task (.+)$",
        r"^add (.+)$",
        r"^new task (.+)$",
        r"^create task (.+)$",
        r"^create (.+)$",
        r"^add task$",
    ],
    "list": [
        r"^list tasks?$",
        r"^show tasks?$",
        r"^list$",
        r"^show$",
        r"^tasks?$",
    ],
    "update": [
        r"^set due date for (.+) to (.+)$",
        r"^set due date of (.+) to (.+)$",
        r"^update (.+) to (.+)$",
        r"^change (.+) to (.+)$",
        r"^modify (.+) to (.+)$",
        r"^update (.+) to$",
        r"^change (.+) to$",
        r"^modify (.+) to$",
    ],
    "complete": [
        r"^complete (.+)$",
        r"^mark (.+) done$",
        r"^finish (.+)$",
        r"^done (.+)$",
        r"^mark (.+) as done$",
    ],
    "delete": [
        r"^delete (.+)$",
        r"^remove (.+)$",
        r"^drop (.+)$",
        r"^trash (.+)$",
    ],
    "undo": [
        r"^undo$",
        r"^undo last$",
        r"^undo that$",
    ],
    "help": [
        r"^help$",
        r"^show help$",
        r"^commands$",
        r"^help me$",
    ],
    "exit": [
        r"^exit$",
        r"^quit$",
        r"^bye$",
        r"^goodbye$",
    ],
}


def extract_due_date(text: str) -> tuple[str, Optional[str]]:
    """Extract due date from text.

    Looks for patterns like "by Friday", "by tomorrow", "due Jan 15".

    Args:
        text: The text to search.

    Returns:
        Tuple of (cleaned_text, due_date_or_None).
    """
    # Patterns for due date extraction
    due_patterns = [
        r"\s+by\s+(.+)$",
        r"\s+due\s+(.+)$",
        r"\s+due\s+date\s+(.+)$",
        r"\s+on\s+(.+)$",
    ]

    for pattern in due_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            due_date = match.group(1).strip()
            cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            return cleaned, due_date

    return text, None


class InputParser:
    """Parses natural language commands into Intent objects."""

    def parse(self, raw_input: str) -> Intent:
        """Parse user input into an Intent.

        Args:
            raw_input: The raw user input string.

        Returns:
            An Intent object representing the parsed command.

        Raises:
            ParserError: If the input cannot be parsed.
        """
        # Normalize input
        normalized = raw_input.strip()

        if not normalized:
            raise AmbiguousInputError()

        # Find matching action pattern
        for action, patterns in ACTION_PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, normalized, re.IGNORECASE)
                if match:
                    groups = match.groups()

                    if action == "add":
                        # Add: title is the first capture group
                        title = groups[0] if groups else ""
                        title, due_date = extract_due_date(title)
                        if not title or title.lower() == "task":
                            raise MissingTitleError()
                        return Intent(action=action, new_title=title, due_date=due_date)

                    elif action == "list":
                        # List: no parameters needed
                        return Intent(action=action)

                    elif action == "update":
                        # Update: target is first group, new_title is second
                        target = groups[0] if groups else ""
                        new_title = groups[1] if len(groups) > 1 else ""

                        # Handle "set due date for X to Y" specially
                        # Pattern: ^set due date for (.+) to (.+)$ captures:
                        # groups[0] = task (e.g., "Buy milk")
                        # groups[1] = due date (e.g., "tomorrow")
                        if normalized.lower().startswith("set due date"):
                            if not new_title:
                                raise MissingTitleError()
                            return Intent(
                                action=action,
                                target=target,
                                new_title=None,
                                due_date=new_title,
                            )

                        if not new_title:
                            raise MissingTitleError()
                        new_title, due_date = extract_due_date(new_title)
                        return Intent(
                            action=action,
                            target=target,
                            new_title=new_title or None,
                            due_date=due_date,
                        )

                    elif action in ("complete", "delete"):
                        # Complete/Delete: target is the first capture group
                        target = groups[0] if groups else ""
                        if not target:
                            raise AmbiguousInputError()
                        return Intent(action=action, target=target)

                    elif action == "undo":
                        # Undo: no parameters
                        return Intent(action=action)

                    elif action == "help":
                        # Help: no parameters
                        return Intent(action=action)

                    elif action == "exit":
                        # Exit: no parameters
                        return Intent(action=action)

        # No pattern matched
        raise UnknownCommandError(normalized)
