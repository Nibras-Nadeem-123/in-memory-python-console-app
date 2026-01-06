# src/todo_executor.py

import dataclasses
from datetime import datetime
from typing import Callable, Dict, Optional

from src.task_model import (
    Command,
    CommandResult,
    OperationType,
    Task,
    TaskStatus,
    ValidationError,
)
from src.task_store import TaskStore


class TodoExecutor:
    """Executes commands and manages business logic."""

    def __init__(self, store: TaskStore):
        """Initializes the executor with a TaskStore."""
        self._store = store
        self._operation_handlers: Dict[OperationType, Callable[[Command], CommandResult]] = {
            OperationType.ADD: self._handle_add,
            OperationType.LIST: self._handle_list,
            OperationType.COMPLETE: self._handle_complete,
            OperationType.DELETE: self._handle_delete,
            OperationType.UPDATE: self._handle_update,
            OperationType.SEARCH: self._handle_search,
            OperationType.HELP: self._handle_help,
        }

    def execute(self, command: Command) -> CommandResult:
        """
        Executes a command and returns the result.

        Args:
            command: The Command object to execute.

        Returns:
            A CommandResult object describing the outcome.
        """
        if command.operation == OperationType.EXIT:
            # EXIT is handled by the CLI loop, but we shouldn't error on it.
            return CommandResult(success=True, message="Exiting.")
            
        handler = self._operation_handlers.get(command.operation)
        if not handler:
            return CommandResult(success=False, message=f"No handler for operation {command.operation}")
        
        try:
            return handler(command)
        except ValidationError as e:
            return CommandResult(success=False, message=str(e))

    def _handle_add(self, command: Command) -> CommandResult:
        """Handles adding a new task."""
        title = command.params.get("title")
        priority = command.params.get("priority")
        
        # The ID is a placeholder; the store will assign the real one.
        new_task = Task(
            id=0,
            title=title,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=datetime.now()
        )
        
        task_id = self._store.add(new_task)
        return CommandResult(
            success=True,
            message=f"Task #{task_id} created: '{title}' (priority: {priority.value.upper()})"
        )

    def _handle_list(self, command: Command) -> CommandResult:
        """Handles listing tasks, with optional status filtering."""
        status_filter = command.params.get("status_filter")
        
        if status_filter == "pending":
            tasks = self._store.filter_by_status(TaskStatus.PENDING)
        elif status_filter == "completed":
            tasks = self._store.filter_by_status(TaskStatus.COMPLETED)
        else:
            tasks = self._store.get_all()
            
        return CommandResult(success=True, message="", data=tasks)

    def _handle_complete(self, command: Command) -> CommandResult:
        """Handles marking a task as completed."""
        task_id = command.task_id
        task = self._store.get(task_id)

        if not task:
            return CommandResult(success=False, message=f"Task #{task_id} not found.")

        if task.status == TaskStatus.COMPLETED:
            return CommandResult(success=False, message=f"Task #{task_id} is already completed.")

        updated_task = dataclasses.replace(task, status=TaskStatus.COMPLETED)
        self._store.update(task_id, updated_task)
        
        return CommandResult(success=True, message=f"Task #{task_id} marked as completed: '{task.title}'")

    def _handle_delete(self, command: Command) -> CommandResult:
        """Handles deleting a task."""
        task_id = command.task_id
        
        task = self._store.get(task_id) # Get task before deleting to return its title

        if not task:
            return CommandResult(success=False, message=f"Task #{task_id} not found.")

        if self._store.delete(task_id):
            return CommandResult(success=True, message=f"Task #{task_id} deleted: '{task.title}'")
        else:
            # This case should theoretically not be reached if task was found, but as a safeguard
            return CommandResult(success=False, message=f"Failed to delete task #{task_id}.")

    def _handle_update(self, command: Command) -> CommandResult:
        """Handles updating a task's properties (title, priority)."""
        task_id = command.task_id
        task = self._store.get(task_id)

        if not task:
            return CommandResult(success=False, message=f"Task #{task_id} not found.")

        updated_title = command.params.get("title")
        updated_priority = command.params.get("priority")
        
        changes = []
        new_task_data = {}

        if updated_title is not None and updated_title != task.title:
            new_task_data["title"] = updated_title
            changes.append("title changed to '" + updated_title + "'")
        
        if updated_priority is not None and updated_priority != task.priority:
            new_task_data["priority"] = updated_priority
            changes.append("priority changed to " + updated_priority.value.upper())

        if not new_task_data:
            return CommandResult(success=False, message=f"No changes specified for task #{task_id}.")

        updated_task = dataclasses.replace(task, **new_task_data)
        self._store.update(task_id, updated_task)
        
        return CommandResult(success=True, message=f"Task #{task_id} updated: {', '.join(changes)}")

    def _handle_search(self, command: Command) -> CommandResult:
        """Handles searching for tasks by keyword."""
        query = command.params.get("query")
        if not query:
            # This should be caught by the parser, but as a safeguard:
            return CommandResult(success=False, message="Search query cannot be empty.")
            
        tasks = self._store.search(query)
        return CommandResult(success=True, message=f"Found {len(tasks)} tasks matching '{query}'", data=tasks)

    def _handle_help(self, command: Command) -> CommandResult:
        """Handles the help command."""
        help_text = """
Available commands:
- add task: <title> [with priority <high|medium|low>]
- list tasks
- complete task <id>
- search <keyword>
- update task <id> title to <new_title>
- update task <id> priority to <high|medium|low>
- delete task <id>
- help
- exit / quit / q
"""
        # We can use the 'message' field for simple text data for now.
        return CommandResult(success=True, message=help_text.strip())