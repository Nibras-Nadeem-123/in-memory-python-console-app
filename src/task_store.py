# src/task_store.py

import dataclasses
from typing import Dict, List, Optional

from src.task_model import Task, TaskStatus

class TaskStore:
    """Manages in-memory task collection."""

    def __init__(self):
        """Initializes the TaskStore with an empty task dictionary and a starting ID."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> int:
        """
        Adds a task to the store, assigning a new unique ID.

        Args:
            task: The Task object to add. The ID of this object is ignored.

        Returns:
            The newly assigned unique ID for the task.
        """
        new_id = self._next_id
        # Create a new task instance with the new ID, respecting immutability
        new_task = dataclasses.replace(task, id=new_id)
        self._tasks[new_id] = new_task
        self._next_id += 1
        return new_id

    def get(self, task_id: int) -> Optional[Task]:
        """
        Retrieves a task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object if found, otherwise None.
        """
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        """
        Returns all tasks, sorted by their ID.

        Returns:
            A list of all Task objects.
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(self, task_id: int, updated_task: Task) -> bool:
        """
        Updates an existing task.

        Args:
            task_id: The ID of the task to update.
            updated_task: The new Task object to replace the old one.

        Returns:
            True if the update was successful, False if the task was not found.
        """
        if task_id not in self._tasks:
            return False
        # Ensure the ID in the updated task object is correct
        if task_id != updated_task.id:
            updated_task = dataclasses.replace(updated_task, id=task_id)
        self._tasks[task_id] = updated_task
        return True

    def delete(self, task_id: int) -> bool:
        """
        Deletes a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the deletion was successful, False if the task was not found.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def count(self) -> int:
        """
        Returns the total number of tasks in the store.

        Returns:
            The number of tasks.
        """
        return len(self._tasks)

    def filter_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Returns tasks matching a specific status, sorted by ID.

        Args:
            status: The TaskStatus to filter by.

        Returns:
            A list of matching Task objects.
        """
        filtered_tasks = [task for task in self._tasks.values() if task.status == status]
        return sorted(filtered_tasks, key=lambda t: t.id)

    def search(self, query: str) -> List[Task]:
        """
        Returns tasks with a title containing the search query (case-insensitive).

        Args:
            query: The string to search for in task titles.

        Returns:
            A list of matching Task objects, sorted by ID.
        """
        query_lower = query.lower()
        searched_tasks = [
            task for task in self._tasks.values() if query_lower in task.title.lower()
        ]
        return sorted(searched_tasks, key=lambda t: t.id)