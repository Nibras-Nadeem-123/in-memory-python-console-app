# src/input_parser.py

import re
from typing import Any, Dict, Optional

from src.task_model import Command, OperationType, Priority, ParseError
from src.todo_utils import normalize_text

class InputParser:
    """Transforms raw text input into structured Command objects."""

    def __init__(self):
        # Defines keywords for each operation type for detection.
        self.operation_keywords = {
            OperationType.ADD: ["add", "create", "new"],
            OperationType.LIST: ["list", "show"],
            OperationType.COMPLETE: ["complete", "done", "finish"],
            OperationType.DELETE: ["delete", "remove"],
            OperationType.UPDATE: ["update", "change"],
            OperationType.SEARCH: ["search", "find"],
            OperationType.EXIT: ["exit", "quit", "q"],
            OperationType.HELP: ["help"],
        }

    def parse(self, text: str) -> Command:
        """
        Parses the input text to determine the operation and its parameters.

        Args:
            text: The raw user input.

        Returns:
            A Command object representing the user's intent.

        Raises:
            ParseError: If the command is not recognized or is malformed.
        """
        normalized = normalize_text(text)
        if not normalized:
            raise ParseError("Input cannot be empty.")

        operation = self._detect_operation(normalized)

        task_id = None
        params = {}

        if operation in [OperationType.COMPLETE, OperationType.DELETE, OperationType.UPDATE]:
            task_id = self._extract_task_id(normalized)
            if task_id is None:
                raise ParseError(f"Missing task ID for '{operation.value}' operation.")

        if operation == OperationType.ADD:
            params = self._extract_add_params(normalized)
        elif operation == OperationType.LIST:
            params = self._extract_list_params(normalized)
        elif operation == OperationType.SEARCH:
            params = self._extract_search_query(normalized)
        elif operation == OperationType.UPDATE:
            params = self._extract_update_params(normalized)

        return Command(operation=operation, task_id=task_id, params=params)

    def _detect_operation(self, normalized_text: str) -> OperationType:
        """
        Detects the operation type from the start of the command.
        """
        for op, keywords in self.operation_keywords.items():
            for keyword in keywords:
                if normalized_text.startswith(keyword):
                    return op
        raise ParseError(
            "Unrecognized command.",
            suggestion="Try 'add', 'list', 'complete', or 'help'."
        )

    def _extract_task_id(self, normalized_text: str) -> Optional[int]:
        """
        Extracts a numeric task ID from the text.
        """
        match = re.search(r'\d+', normalized_text)
        if match:
            return int(match.group(0))
        return None

    def _extract_add_params(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts title and optional priority for an 'add' command.
        """
        # Regex to capture the title and an optional priority
        # Example: "add task: my new task with priority high"
        match = re.search(r':(.*?)(?:with priority\s+(high|medium|low))?$', normalized_text)
        
        if not match:
            # Fallback for simpler "add my new task" format
            parts = normalized_text.split(maxsplit=1)
            if len(parts) > 1:
                title = parts[1].strip()
            else:
                 raise ParseError("Task title cannot be empty for 'add' operation.")
        else:
            title = match.group(1).strip()

        if not title:
            raise ParseError("Task title cannot be empty for 'add' operation.")

        # Default priority is MEDIUM
        priority = Priority.MEDIUM
        if match and match.group(2):
            try:
                priority = Priority(match.group(2))
            except ValueError:
                raise ParseError(f"Invalid priority '{match.group(2)}'. Use 'high', 'medium', or 'low'.")
        
        return {"title": title, "priority": priority}

    def _extract_list_params(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts optional filter for a 'list' command.
        """
        if "pending" in normalized_text:
            return {"status_filter": "pending"}
        if "completed" in normalized_text:
            return {"status_filter": "completed"}
        return {}

    def _extract_search_query(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts the query from a 'search' command.
        """
        # Assuming the format "search <query>" or "find <query>"
        parts = normalized_text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            raise ParseError("Search query cannot be empty.")
        return {"query": parts[1].strip()}

    def _extract_update_params(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts update parameters (title or priority) for an 'update' command.
        Examples:
            "update task 1 title to new title"
            "update task 3 priority to high"
        """
        params = {}
        
        # Regex for title update: "title to <new_title>"
        title_match = re.search(r'title to\s+(.*)$', normalized_text)
        if title_match:
            new_title = title_match.group(1).strip()
            if not new_title:
                raise ParseError("New title cannot be empty for update operation.")
            params["title"] = new_title
            
        # Regex for priority update: "priority to <high|medium|low>"
        priority_match = re.search(r'priority to\s+(high|medium|low)$', normalized_text)
        if priority_match:
            try:
                params["priority"] = Priority(priority_match.group(1))
            except ValueError:
                raise ParseError(f"Invalid priority '{priority_match.group(1)}'. Use 'high', 'medium', or 'low'.")
        
        if not params:
            raise ParseError("No update parameters (title or priority) specified.")
            
        return params