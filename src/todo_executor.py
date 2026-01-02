"""Command executor for the todo system.

Executes parsed Intents and formats results for output.
"""

from dataclasses import dataclass
from typing import Optional

from src.input_parser import InputParser, ParserError
from src.task_model import Intent, Task
from src.task_store import (
    AlreadyCompletedError,
    AmbiguousTaskError,
    NoHistoryError,
    TaskNotFoundError,
    TaskStore,
)


@dataclass
class ExecutionResult:
    """Result of executing a command.

    Attributes:
        success: Whether the command succeeded.
        message: User-facing message describing the result.
        data: Optional data to include in output.
    """
    success: bool
    message: str
    data: Optional[dict] = None


class TodoExecutor:
    """Executes parsed Intents against the TaskStore."""

    def __init__(self, store: TaskStore, parser: Optional[InputParser] = None) -> None:
        """Initialize the executor.

        Args:
            store: The TaskStore to operate on.
            parser: Optional InputParser (created if not provided).
        """
        self.store = store
        self.parser = parser or InputParser()

    def execute(self, raw_input: str) -> ExecutionResult:
        """Execute a user command.

        Args:
            raw_input: The raw user input string.

        Returns:
            An ExecutionResult with success status and message.
        """
        try:
            # Parse the input
            intent = self.parser.parse(raw_input)

            # Execute the appropriate action
            result = self._execute_intent(intent)

            return result

        except ParserError as e:
            return ExecutionResult(success=False, message=e.user_message())

    def _execute_intent(self, intent: Intent) -> ExecutionResult:
        """Execute a parsed Intent.

        Args:
            intent: The parsed Intent to execute.

        Returns:
            An ExecutionResult for the action.
        """
        if intent.action == "add":
            return self._add(intent)
        elif intent.action == "list":
            return self._list(intent)
        elif intent.action == "update":
            return self._update(intent)
        elif intent.action == "complete":
            return self._complete(intent)
        elif intent.action == "delete":
            return self._delete(intent)
        elif intent.action == "undo":
            return self._undo(intent)
        elif intent.action == "help":
            return self._help(intent)
        elif intent.action == "exit":
            return self._exit(intent)
        else:
            return ExecutionResult(
                success=False,
                message=f"Unknown action: {intent.action}"
            )

    def _add(self, intent: Intent) -> ExecutionResult:
        """Handle add command."""
        if not intent.new_title:
            return ExecutionResult(success=False, message="Please provide a task title")

        task = self.store.add_task(intent.new_title, intent.due_date)

        if task.due_date:
            return ExecutionResult(
                success=True,
                message=f"Added task '{task.title}' (due: {task.due_date})",
                data={"task": task}
            )
        return ExecutionResult(
            success=True,
            message=f"Added task '{task.title}'",
            data={"task": task}
        )

    def _list(self, intent: Intent) -> ExecutionResult:
        """Handle list command."""
        tasks = self.store.list_tasks()

        if not tasks:
            return ExecutionResult(
                success=True,
                message="No tasks found",
                data={"tasks": []}
            )

        # Format task list
        task_lines = []
        for task in tasks:
            status_marker = "[x]" if task.status == "completed" else "[ ]"
            due_str = f" (due: {task.due_date})" if task.due_date else ""
            task_lines.append(f"{status_marker} {task.title}{due_str}")

        message = "Your tasks:\n" + "\n".join(f"  {i+1}. {line}" for i, line in enumerate(task_lines))

        return ExecutionResult(
            success=True,
            message=message,
            data={"tasks": tasks}
        )

    def _update(self, intent: Intent) -> ExecutionResult:
        """Handle update command."""
        if not intent.target:
            return ExecutionResult(
                success=False,
                message="I didn't understand. Which task? Please specify the task title or ID."
            )

        try:
            task = self.store.find_task(intent.target)
        except TaskNotFoundError:
            return ExecutionResult(
                success=False,
                message=f"Task '{intent.target}' not found. Did you mean to create it?"
            )
        except AmbiguousTaskError as e:
            return ExecutionResult(
                success=False,
                message=str(e)
            )

        # Perform update
        updated = self.store.update_task(
            task.id,
            title=intent.new_title,
            due_date=intent.due_date
        )

        changes = []
        if intent.new_title:
            changes.append(f"title to '{intent.new_title}'")
        if intent.due_date:
            changes.append(f"due date to '{intent.due_date}'")

        return ExecutionResult(
            success=True,
            message=f"Updated task '{updated.title}' with {', '.join(changes)}",
            data={"task": updated}
        )

    def _complete(self, intent: Intent) -> ExecutionResult:
        """Handle complete command."""
        if not intent.target:
            return ExecutionResult(
                success=False,
                message="I didn't understand. Which task? Please specify the task title or ID."
            )

        try:
            task = self.store.find_task(intent.target)
        except TaskNotFoundError:
            return ExecutionResult(
                success=False,
                message=f"Task '{intent.target}' not found. Did you mean to create it?"
            )
        except AmbiguousTaskError as e:
            return ExecutionResult(
                success=False,
                message=str(e)
            )

        try:
            completed = self.store.complete_task(task.id)
            return ExecutionResult(
                success=True,
                message=f"Completed '{completed.title}'",
                data={"task": completed}
            )
        except AlreadyCompletedError:
            return ExecutionResult(
                success=False,
                message=f"Task '{task.title}' is already completed"
            )

    def _delete(self, intent: Intent) -> ExecutionResult:
        """Handle delete command."""
        if not intent.target:
            return ExecutionResult(
                success=False,
                message="I didn't understand. Which task? Please specify the task title or ID."
            )

        try:
            task = self.store.find_task(intent.target)
        except TaskNotFoundError:
            return ExecutionResult(
                success=False,
                message=f"Task '{intent.target}' not found. Did you mean to create it?"
            )
        except AmbiguousTaskError as e:
            return ExecutionResult(
                success=False,
                message=str(e)
            )

        deleted = self.store.delete_task(task.id)
        return ExecutionResult(
            success=True,
            message=f"Deleted '{deleted.title}'",
            data={"task": deleted}
        )

    def _undo(self, intent: Intent) -> ExecutionResult:
        """Handle undo command."""
        try:
            operation = self.store.undo()

            # Format message based on action
            action_verb = {
                "add": "Added",
                "update": "Updated",
                "complete": "Completed",
                "delete": "Deleted",
            }.get(operation.action, operation.action.capitalize())

            if operation.before_state:
                task_title = operation.before_state.title
            elif operation.task_id:
                task_title = f"task #{operation.task_id}"
            else:
                task_title = "task"

            return ExecutionResult(
                success=True,
                message=f"Undid: {action_verb} {task_title}",
                data={"operation": operation}
            )

        except NoHistoryError:
            return ExecutionResult(
                success=False,
                message="Nothing to undo"
            )

    def _help(self, intent: Intent) -> ExecutionResult:
        """Handle help command."""
        help_text = """Available commands:

  add <title> [by <date>]    - Create a new task
  list                       - Show all tasks
  complete <task>            - Mark a task as done
  update <task> to <title>   - Change task title
  delete <task>              - Remove a task
  undo                       - Reverse the last action
  help                       - Show this message
  exit                       - Quit the application

Examples:
  add Buy milk by tomorrow
  list
  complete Buy milk
  update Buy milk to Buy eggs
  delete Buy milk
  undo

Tip: You can reference tasks by title (e.g., 'complete Buy milk')
or by ID (e.g., 'complete task 1' or '#1')."""

        return ExecutionResult(success=True, message=help_text)

    def _exit(self, intent: Intent) -> ExecutionResult:
        """Handle exit command."""
        return ExecutionResult(success=True, message="Goodbye!")
