# Data Model: Spec-Driven Todo Console Application

**Feature**: 006-todo-console-app
**Date**: 2025-12-31
**Status**: Completed

## Overview

This document defines all data structures for the todo console application. All models use Python dataclasses for immutability and type safety.

---

## Core Entities

### 1. Task

Represents a single todo item in the system.

**Purpose**: Store task data with metadata for filtering and ordering.

**Attributes**:
```python
@dataclass(frozen=True)
class Task:
    id: int                    # Unique identifier (auto-assigned)
    title: str                 # Task description (user-provided)
    status: TaskStatus         # Current state (PENDING or COMPLETED)
    priority: Priority         # Importance level (HIGH, MEDIUM, LOW)
    created_at: datetime       # Creation timestamp (for ordering)
```

**Invariants**:
- `id` MUST be > 0
- `title` MUST be non-empty string (1-200 characters)
- `status` MUST be valid TaskStatus enum value
- `priority` MUST be valid Priority enum value
- `created_at` MUST be valid datetime

**State Transitions**:
```
PENDING → COMPLETED (via complete operation)
COMPLETED → PENDING (via update operation, if implemented)
```

**Example**:
```python
Task(
    id=1,
    title="Write documentation",
    status=TaskStatus.PENDING,
    priority=Priority.HIGH,
    created_at=datetime(2025, 12, 31, 10, 30, 0)
)
```

---

### 2. TaskStatus (Enum)

Represents the completion state of a task.

**Purpose**: Type-safe status tracking.

**Values**:
```python
class TaskStatus(Enum):
    PENDING = "pending"       # Task not yet completed
    COMPLETED = "completed"   # Task finished
```

**Usage**:
- Default status for new tasks: `PENDING`
- Changed to `COMPLETED` via complete operation
- Used for filtering in list operations

---

### 3. Priority (Enum)

Represents the importance level of a task.

**Purpose**: Type-safe priority classification.

**Values**:
```python
class Priority(Enum):
    HIGH = "high"             # Urgent or important
    MEDIUM = "medium"         # Normal priority (default)
    LOW = "low"               # Can be deferred
```

**Usage**:
- Default priority for new tasks: `MEDIUM`
- Can be specified during add operation
- Can be updated via update operation
- Used for sorting (HIGH > MEDIUM > LOW)

---

## Command Layer

### 4. OperationType (Enum)

Represents the type of operation to execute.

**Purpose**: Type-safe command classification.

**Values**:
```python
class OperationType(Enum):
    ADD = "add"               # Create new task
    LIST = "list"             # Display tasks
    COMPLETE = "complete"     # Mark task as done
    DELETE = "delete"         # Remove task
    UPDATE = "update"         # Modify task properties
    SEARCH = "search"         # Find tasks by keyword
    EXIT = "exit"             # Terminate program
```

**Mapping to User Commands**:
- "add task", "create task", "new task" → ADD
- "list tasks", "show tasks" → LIST
- "complete task", "finish task", "done" → COMPLETE
- "delete task", "remove task" → DELETE
- "update task", "change task" → UPDATE
- "search", "find" → SEARCH
- "exit", "quit", "q" → EXIT

---

### 5. Command

Represents a parsed user command ready for execution.

**Purpose**: Structured representation of user intent.

**Attributes**:
```python
@dataclass(frozen=True)
class Command:
    operation: OperationType      # What to do
    task_id: Optional[int]        # Which task (if applicable)
    params: Dict[str, Any]        # Operation-specific parameters
```

**Parameter Patterns by Operation**:

**ADD**:
```python
params = {
    "title": str,              # Required: task description
    "priority": Priority       # Optional: defaults to MEDIUM
}
```

**LIST**:
```python
params = {
    "filter": Optional[str]    # Optional: "pending", "completed", or None (all)
}
```

**COMPLETE**:
```python
params = {}                    # No additional params (task_id is sufficient)
```

**DELETE**:
```python
params = {}                    # No additional params (task_id is sufficient)
```

**UPDATE**:
```python
params = {
    "title": Optional[str],    # New title (if updating title)
    "priority": Optional[Priority]  # New priority (if updating priority)
}
# At least one param must be present
```

**SEARCH**:
```python
params = {
    "query": str               # Required: search keyword
}
```

**EXIT**:
```python
params = {}                    # No params
```

**Examples**:
```python
# Add task with default priority
Command(
    operation=OperationType.ADD,
    task_id=None,
    params={"title": "Write tests", "priority": Priority.MEDIUM}
)

# Complete specific task
Command(
    operation=OperationType.COMPLETE,
    task_id=5,
    params={}
)

# List pending tasks only
Command(
    operation=OperationType.LIST,
    task_id=None,
    params={"filter": "pending"}
)
```

---

### 6. CommandResult

Represents the outcome of executing a command.

**Purpose**: Standardized success/error reporting.

**Attributes**:
```python
@dataclass(frozen=True)
class CommandResult:
    success: bool              # True if operation succeeded
    message: str               # User-facing feedback
    data: Optional[Any]        # Optional result data (for list/search)
```

**Success Patterns**:
```python
# Successful add
CommandResult(
    success=True,
    message="Task #1 created: 'Write documentation'",
    data=None
)

# Successful list (returning tasks)
CommandResult(
    success=True,
    message="Found 3 tasks",
    data=[task1, task2, task3]
)
```

**Error Patterns**:
```python
# Task not found
CommandResult(
    success=False,
    message="Task #999 not found. Use 'list' to see all tasks.",
    data=None
)

# Invalid command format
CommandResult(
    success=False,
    message="Could not parse command. Try 'add task: <title>' or 'help'.",
    data=None
)
```

---

## Error Types

### 7. ParseError

Raised when user input cannot be parsed into a valid Command.

**Purpose**: Distinguish parsing failures from execution failures.

**Attributes**:
```python
class ParseError(Exception):
    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
```

**Usage**:
```python
raise ParseError(
    message="Unrecognized command",
    suggestion="Try: add task: <title>, list tasks, complete task <id>"
)
```

---

### 8. ValidationError

Raised when command is valid but contains invalid data.

**Purpose**: Distinguish validation failures from parse/execution failures.

**Attributes**:
```python
class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
```

**Usage**:
```python
raise ValidationError("Task ID must be a positive integer")
```

---

## Data Flow

```
User Input (str)
    ↓
[InputParser]
    ↓
Command (validated structure)
    ↓
[TodoExecutor]
    ↓
CommandResult (success/error + message)
    ↓
[CLI] → Display to user
```

---

## Entity Relationships

```
TaskStore (1) ──── (N) Task
    │
    └─ manages tasks by ID

Command (1) ──── (0..1) Task
    │
    └─ references task by ID for COMPLETE, DELETE, UPDATE

CommandResult (1) ──── (0..N) Task
    │
    └─ may contain list of tasks for LIST, SEARCH operations
```

---

## Validation Rules

### Task Validation
- **title**: 1-200 characters, non-empty after stripping whitespace
- **id**: > 0 (auto-assigned by TaskStore)
- **status**: Must be `TaskStatus.PENDING` or `TaskStatus.COMPLETED`
- **priority**: Must be `Priority.HIGH`, `Priority.MEDIUM`, or `Priority.LOW`
- **created_at**: Must be valid datetime (auto-assigned)

### Command Validation
- **operation**: Must be valid `OperationType`
- **task_id**: If present, must be > 0
- **params**: Must contain required keys for operation type
  - ADD requires "title"
  - SEARCH requires "query"
  - UPDATE requires at least one of "title" or "priority"

### Input Validation
- Command string: 1-500 characters
- Empty input: Rejected with helpful message
- Whitespace-only: Treated as empty

---

## Storage Schema (In-Memory)

```python
class TaskStore:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}       # ID → Task mapping
        self._next_id: int = 1                  # Auto-increment counter
```

**Operations**:
- **add(task: Task) → int**: Assigns ID, stores task, returns ID
- **get(task_id: int) → Optional[Task]**: Retrieves task by ID
- **get_all() → List[Task]**: Returns all tasks
- **update(task_id: int, task: Task) → bool**: Replaces task
- **delete(task_id: int) → bool**: Removes task
- **filter_by_status(status: TaskStatus) → List[Task]**: Returns matching tasks
- **search(query: str) → List[Task]**: Returns tasks with query in title

**Invariants**:
- IDs are unique and never reused (even after deletion)
- `_next_id` always points to next available ID
- No gaps in ID sequence during session

---

## Type Safety

All models use Python type hints and are validated at construction:

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

# Enable runtime type checking in tests
@dataclass(frozen=True)
class Task:
    id: int
    title: str
    status: TaskStatus
    priority: Priority
    created_at: datetime

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError("Task ID must be positive")
        if not self.title or len(self.title) > 200:
            raise ValueError("Title must be 1-200 characters")
```

---

## Examples

### Complete Workflow Example

```python
# 1. User input
user_input = "add task: implement parser with priority high"

# 2. Parser creates Command
command = Command(
    operation=OperationType.ADD,
    task_id=None,
    params={
        "title": "implement parser",
        "priority": Priority.HIGH
    }
)

# 3. Executor creates Task
task = Task(
    id=1,  # assigned by TaskStore
    title="implement parser",
    status=TaskStatus.PENDING,
    priority=Priority.HIGH,
    created_at=datetime.now()
)

# 4. TaskStore saves task
store.add(task)

# 5. Executor returns result
result = CommandResult(
    success=True,
    message="Task #1 created: 'implement parser' (priority: HIGH)",
    data=None
)

# 6. CLI displays to user
print(result.message)
# Output: Task #1 created: 'implement parser' (priority: HIGH)
```

---

## Next Steps

1. Implement models in `src/task_model.py`
2. Implement storage in `src/task_store.py`
3. Use models in parser (`src/input_parser.py`)
4. Use models in executor (`src/todo_executor.py`)
5. Write unit tests for all models
