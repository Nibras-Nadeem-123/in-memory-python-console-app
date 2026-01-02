"""In-memory task storage with undo support.

Provides TaskStore class for managing task state and operation history.
"""

from typing import Optional

from src.task_model import Operation, Task


class TaskNotFoundError(Exception):
    """Raised when a task reference cannot be found."""

    def __init__(self, target: str) -> None:
        self.target = target
        super().__init__(f"Task '{target}' not found")


class AmbiguousTaskError(Exception):
    """Raised when multiple tasks match a reference."""

    def __init__(self, target: str, matches: list[str]) -> None:
        self.target = target
        self.matches = matches
        super().__init__(
            f"Multiple tasks match '{target}': {', '.join(matches)}. Please be more specific."
        )


class AlreadyCompletedError(Exception):
    """Raised when attempting to complete an already completed task."""

    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__(f"Task '{title}' is already completed")


class NoHistoryError(Exception):
    """Raised when undo is called with no history."""

    def __init__(self) -> None:
        super().__init__("Nothing to undo")


class TaskStore:
    """Manages in-memory task state with undo support.

    Attributes:
        tasks: Dictionary mapping task ID to Task.
        history: List of operations for undo support.
    """

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
        self._history: list[Operation] = []

    @property
    def tasks(self) -> dict[int, Task]:
        """Return all tasks as a dictionary."""
        return self._tasks.copy()

    @property
    def history(self) -> list[Operation]:
        """Return operation history as a read-only copy."""
        return self._history.copy()

    def add_task(self, title: str, due_date: Optional[str] = None) -> Task:
        """Create a new task with the given title and optional due date.

        Args:
            title: The task description.
            due_date: Optional natural language due date.

        Returns:
            The created Task.
        """
        task = Task(id=self._next_id, title=title, due_date=due_date)
        self._tasks[self._next_id] = task
        self._next_id += 1

        # Record operation for undo
        operation = Operation(action="add", task_id=task.id, before_state=None)
        self._history.append(operation)

        return task

    def list_tasks(self) -> list[Task]:
        """Return all tasks sorted by ID.

        Returns:
            List of Tasks ordered by ID.
        """
        return [self._tasks[tid] for tid in sorted(self._tasks.keys())]

    def find_task(self, reference: str) -> Task:
        """Find a task by title substring or ID.

        Args:
            reference: Task title substring or "task X" / "#X" format.

        Returns:
            The matching Task.

        Raises:
            TaskNotFoundError: If no task matches.
            AmbiguousTaskError: If multiple tasks match.
        """
        # Try ID-based reference first
        if reference.startswith("task ") or reference.startswith("#"):
            try:
                id_str = reference.split()[-1] if reference.startswith("task ") else reference[1:]
                task_id = int(id_str)
                if task_id in self._tasks:
                    return self._tasks[task_id]
            except ValueError:
                pass  # Not a valid ID, try title search

        # Search by title substring
        matches: list[tuple[int, Task]] = []
        for tid, task in self._tasks.items():
            if reference.lower() in task.title.lower():
                matches.append((tid, task))

        if not matches:
            raise TaskNotFoundError(reference)

        if len(matches) > 1:
            # Multiple matches - return ambiguous with titles
            titles = [task.title for _, task in matches]
            raise AmbiguousTaskError(reference, titles)

        return matches[0][1]

    def update_task(
        self, task_id: int, title: Optional[str] = None, due_date: Optional[str] = None
    ) -> Task:
        """Update a task's title and/or due date.

        Args:
            task_id: The ID of the task to update.
            title: New title (None to keep existing).
            due_date: New due date (None to keep existing).

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If task_id doesn't exist.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(str(task_id))

        task = self._tasks[task_id]
        before_state = Task(
            id=task.id,
            title=task.title,
            status=task.status,
            due_date=task.due_date,
            created_at=task.created_at,
        )

        if title is not None:
            task.title = title
        if due_date is not None:
            task.due_date = due_date

        # Record operation for undo
        operation = Operation(action="update", task_id=task_id, before_state=before_state)
        self._history.append(operation)

        return task

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed.

        Args:
            task_id: The ID of the task to complete.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If task_id doesn't exist.
            AlreadyCompletedError: If task is already completed.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(str(task_id))

        task = self._tasks[task_id]

        if task.status == "completed":
            raise AlreadyCompletedError(task.title)

        before_state = Task(
            id=task.id,
            title=task.title,
            status=task.status,
            due_date=task.due_date,
            created_at=task.created_at,
        )

        task.status = "completed"

        # Record operation for undo
        operation = Operation(action="complete", task_id=task_id, before_state=before_state)
        self._history.append(operation)

        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            The deleted Task.

        Raises:
            TaskNotFoundError: If task_id doesn't exist.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(str(task_id))

        task = self._tasks[task_id]
        before_state = Task(
            id=task.id,
            title=task.title,
            status=task.status,
            due_date=task.due_date,
            created_at=task.created_at,
        )

        del self._tasks[task_id]

        # Record operation for undo
        operation = Operation(action="delete", task_id=task_id, before_state=before_state)
        self._history.append(operation)

        return task

    def undo(self) -> Operation:
        """Undo the last operation.

        Returns:
            The Operation that was undone.

        Raises:
            NoHistoryError: If there's nothing to undo.
        """
        if not self._history:
            raise NoHistoryError()

        operation = self._history.pop()

        if operation.action == "add":
            # Remove the added task
            if operation.task_id is not None and operation.task_id in self._tasks:
                del self._tasks[operation.task_id]

        elif operation.action in ("update", "complete"):
            # Restore the previous state
            if operation.task_id is not None and operation.before_state is not None:
                self._tasks[operation.task_id] = operation.before_state

        elif operation.action == "delete":
            # Restore the deleted task
            if operation.before_state is not None:
                self._tasks[operation.before_state.id] = operation.before_state

        return operation
