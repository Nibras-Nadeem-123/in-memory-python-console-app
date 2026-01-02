# Feature Specification: Spec-Driven Todo System

**Feature Branch**: `001-todo-system`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Create a Spec-Driven Todo system accepting natural language commands for managing tasks in memory."

## User Scenarios & Testing

### User Story 1 - Add Tasks (Priority: P1)

As a user, I want to add tasks using natural language so that I can quickly capture thoughts without learning command syntax.

**Why this priority**: Adding tasks is the fundamental operation - without it, the todo system has no purpose. P1 because every user journey starts here.

**Independent Test**: Can be fully tested by running a single command "add a task to buy milk" and verifying a task with title "buy milk" is created in pending status.

**Acceptance Scenarios**:

1. **Given** no tasks exist, **When** user enters "add a task to buy milk tomorrow", **Then** a new task with title "buy milk" and due date "tomorrow" is created with status "pending"
2. **Given** no tasks exist, **When** user enters "add a task finish report", **Then** a new task with title "finish report" and no due date is created with status "pending"
3. **Given** tasks exist, **When** user adds another task, **Then** the new task receives a unique incremental ID

---

### User Story 2 - List Tasks (Priority: P1)

As a user, I want to see all my tasks so that I can review what needs to be done.

**Why this priority**: Visibility into task state is essential for task management. P1 because users need to see what they have.

**Independent Test**: Can be fully tested by adding 3 tasks and running "list tasks" to verify all 3 appear with correct IDs and statuses.

**Acceptance Scenarios**:

1. **Given** no tasks exist, **When** user requests task list, **Then** system displays "No tasks found" message
2. **Given** 3 pending tasks exist, **When** user lists tasks, **Then** all 3 tasks are displayed with ID, title, status, and due date (if set)
3. **Given** mixed pending and completed tasks exist, **When** user lists tasks, **Then** all tasks are shown with their respective statuses

---

### User Story 3 - Complete Tasks (Priority: P1)

As a user, I want to mark tasks as complete so that I can track my progress.

**Why this priority**: Completion is the primary mechanism for progress tracking. P1 because it completes the core workflow: add → complete.

**Independent Test**: Can be fully tested by adding a task, completing it by ID, and verifying status changes to "completed".

**Acceptance Scenarios**:

1. **Given** task with ID 1 exists with "pending" status, **When** user enters "complete task 1", **Then** task 1 status changes to "completed"
2. **Given** task with ID 1 exists with "completed" status, **When** user attempts to complete it again, **Then** system displays "Task 1 is already completed"
3. **Given** no task with ID 99 exists, **When** user attempts to complete task 99, **Then** system displays "Task 99 not found"

---

### User Story 4 - Update Tasks (Priority: P2)

As a user, I want to modify task details so that I can correct mistakes or refine my plans.

**Why this priority**: Updates are common but not essential for MVP. P2 because users can delete and re-add tasks if needed.

**Independent Test**: Can be fully tested by adding a task, updating its title, and verifying the new title is displayed.

**Acceptance Scenarios**:

1. **Given** task with ID 1 has title "buy milk", **When** user enters "update task 1 to buy eggs", **Then** task 1 title changes to "buy eggs"
2. **Given** task with ID 1 has no due date, **When** user adds a due date, **Then** task 1 due date is set
3. **Given** task with ID 99 does not exist, **When** user attempts update, **Then** system displays "Task 99 not found"

---

### User Story 5 - Delete Tasks (Priority: P2)

As a user, I want to remove tasks so that I can keep my list clean and relevant.

**Why this priority**: Deletion is important for list management but users can work around it. P2 because completed tasks could be filtered instead.

**Independent Test**: Can be fully tested by adding 2 tasks, deleting one, and verifying only the remaining task appears in list.

**Acceptance Scenarios**:

1. **Given** task with ID 1 exists, **When** user enters "delete task 1", **Then** task 1 is removed from the task list
2. **Given** tasks with IDs 1, 2, 3 exist, **When** user deletes task 2, **Then** tasks 1 and 3 remain with their original IDs
3. **Given** no task with ID 99 exists, **When** user attempts deletion, **Then** system displays "Task 99 not found"

---

### User Story 6 - Natural Language Understanding (Priority: P2)

As a user, I want to use flexible phrasing so that I can express intent naturally without memorizing commands.

**Why this priority**: Natural language is a key differentiator but the system can function with exact commands. P2 because structured commands work without this.

**Independent Test**: Can be fully tested by trying multiple phrasings ("complete task 1", "mark task 1 done", "finish task 1") and verifying all produce the same result.

**Acceptance Scenarios**:

1. **Given** task 1 exists pending, **When** user enters "complete task 1" OR "mark task 1 done" OR "finish task 1", **Then** task 1 is marked completed
2. **Given** no tasks exist, **When** user enters unclear input, **Then** system asks for clarification
3. **Given** user enters a valid action with invalid ID, **Then** system provides helpful error with valid IDs listed

---

### Edge Cases

- **Ambiguous input**: What happens when input is unclear (e.g., "update task" without specifying which or what)?
  - System prompts for clarification: "Which task do you want to update? Please specify the task title or ID."
- **Empty input**: What happens when user presses enter with no text?
  - System displays "Please enter a command. Type 'help' for available commands."
- **Duplicate task titles**: Can two tasks have the same title?
  - Yes, tasks are identified by internal ID. Users reference by title substring or ID.
- **ID reassignment**: What happens to IDs when tasks are deleted?
  - Internal IDs remain stable (never reused) for history tracking. Users reference by title.
- **Special characters in title**: How are special characters handled?
  - Titles are preserved as-is. No sanitization required for display in CLI.
- **Due date parsing**: How are due dates interpreted?
  - System parses natural language dates: "tomorrow", "today", "next Friday", or explicit dates.
- **Session termination**: What happens to tasks when the app closes?
  - Tasks remain in memory. Optional persistence via export command.
- **Case sensitivity**: Are commands case-sensitive?
  - Commands are case-insensitive. Task titles preserve original casing.
- **Completed task editing**: Can completed tasks be modified?
  - Yes, completed tasks are fully editable (title, due date, status). Users can uncomplete to edit.
- **Undo support**: Can users reverse actions?
  - Yes, system tracks operation history and supports "undo" for the last operation.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept natural language commands via stdin
- **FR-002**: System MUST parse commands into structured intent with action type and parameters
- **FR-003**: System MUST support actions: add, list, update, complete, delete, undo, help, exit
- **FR-004**: System MUST maintain an in-memory task list with unique internal IDs
- **FR-005**: Users MUST reference tasks by title substring or ID (ID is internal, not user-facing)
- **FR-006**: Each task MUST have: id (int), title (str), status (pending/completed), optional due_date (str), created_at (datetime)
- **FR-007**: System MUST prompt for clarification when input is ambiguous
- **FR-008**: System MUST suggest task creation when user references non-existent task
- **FR-009**: Completed tasks MUST be fully editable (title, due_date, status)
- **FR-010**: System MUST track operation history and support undo for last operation
- **FR-011**: System MUST provide clear textual feedback for every command
- **FR-012**: System MUST display human-readable errors with actionable guidance
- **FR-013**: System MUST be deterministic: same input produces same output and state
- **FR-014**: System MUST have modular architecture with separation of parsing, state, and execution
- **FR-015**: System MUST not execute arbitrary code or eval user input

### Key Entities

- **Task**: Represents a todo item with:
  - `id`: Unique integer identifier (internal, never reused)
  - `title`: String description of the task
  - `status`: Enum: "pending" or "completed"
  - `due_date`: Optional string for deadline/reminder
  - `created_at`: Timestamp of task creation
- **Intent**: Structured representation of parsed user command with:
  - `action`: One of add, list, update, complete, delete, undo
  - `target`: Task reference (title substring match or internal ID)
  - `title`: String (for add/update actions)
  - `due_date`: String (for add/update actions)
- **State**: In-memory container with:
  - `tasks`: Dictionary mapping id → Task
  - `next_id`: Integer for next task ID assignment
  - `history`: List of (operation, reverse_operation) tuples for undo
- **Operation**: Immutable record of an action with:
  - `action`: The action type
  - `target_id`: The task ID affected
  - `before_state`: Snapshot of task state before operation
  - `timestamp`: When the operation occurred

### Non-Functional Requirements

- **NFR-001**: Command response time MUST be under 100ms for simple operations
- **NFR-002**: Application MUST start in under 1 second
- **NFR-003**: Memory footprint MUST stay under 50MB for idle state
- **NFR-004**: System MUST handle up to 10,000 tasks without degradation
- **NFR-005**: Code MUST be modular with clear separation of concerns
- **NFR-006**: All core modules MUST have 80%+ test coverage
- **NFR-007**: All input MUST be validated before processing
- **NFR-008**: No use of eval() or exec() on user input

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can add a task and see it appear in the list within 1 second of starting the application
- **SC-002**: 100% of supported commands execute without errors under normal conditions
- **SC-003**: All error messages are actionable (tell user what went wrong and how to fix it)
- **SC-004**: System state is deterministic - running the same commands produces identical results
- **SC-005**: Architecture supports adding new actions without modifying core state management

## Command Reference

| Action | Example Commands | Parameters |
|--------|------------------|------------|
| add | "add task buy milk", "add task finish report by Friday" | title, optional due_date |
| list | "list tasks", "show tasks", "list" | none |
| update | "update buy milk to buy eggs", "set due date for finish report to tomorrow" | target (title), new_title and/or due_date |
| complete | "complete buy milk", "mark buy milk done", "finish buy milk" | target (title or ID) |
| delete | "delete buy milk", "remove buy milk" | target (title or ID) |
| undo | "undo", "undo last" | none |
| help | "help", "show help" | none |
| exit | "exit", "quit", "bye" | none |

**Task Reference Formats:**
- By title: "buy milk" (matches first task with title containing "buy milk")
- By ID: "task 1" or "#1" (internal reference for disambiguation)

## Technical Notes

### Module Structure (recommended)

```
src/
  __init__.py
  models/
    __init__.py
    task.py          # Task dataclass
    intent.py        # Intent parsing result
  state/
    __init__.py
    store.py         # In-memory task state
  parser/
    __init__.py
    command_parser.py  # Natural language to Intent
  executor/
    __init__.py
    command_executor.py  # Intent to action
  main.py           # CLI entry point
```

### Intent Parsing Strategy

1. Tokenize input into words
2. Match action keywords to supported actions
3. Extract parameters based on action type
4. Return structured Intent or error

### Error Taxonomy

| Error Type | Message Template | User Action |
|------------|------------------|-------------|
| AMBIGUOUS_INPUT | "I didn't understand. Which task? Please specify the task title or ID." | Clarify target |
| TASK_NOT_FOUND | "Task '{target}' not found. Did you mean to create it?" | Verify name or create |
| ALREADY_COMPLETED | "Task '{title}' is already completed" | Select different task |
| INVALID_COMMAND | "Unknown command: '{cmd}'. Type 'help' for available commands" | Review help, retry |
| MISSING_TITLE | "Please provide a task title" | Add title to command |
| NO_HISTORY | "Nothing to undo" | No previous operations |
| AMBIGUOUS_MATCH | "Multiple tasks match '{target}': {matches}. Please be more specific." | Narrow search |
