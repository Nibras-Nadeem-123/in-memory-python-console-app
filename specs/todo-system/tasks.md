# Tasks: Spec-Driven Todo System

**Input**: Design documents from `specs/todo-system/`
**Prerequisites**: spec.md (required), plan.md (required), checklist.md (reference)

**Tests**: ALL TESTS must be written FIRST, ensure they FAIL, then implement

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `src/` directory with `__init__.py`
- [ ] T002 Create `tests/unit/` directory with `__init__.py`
- [ ] T003 Create `tests/integration/` directory with `__init__.py`
- [ ] T004 [P] Create `requirements.txt` with `pytest>=7.0.0`
- [ ] T005 [P] Create `pyproject.toml` with project config and pytest settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational

> Write these tests FIRST, ensure they FAIL before implementation

- [ ] T006 [P] [FOUNDATION] Test Task dataclass creation in `tests/unit/test_task_model.py`
- [ ] T007 [P] [FOUNDATION] Test Intent dataclass in `tests/unit/test_task_model.py`
- [ ] T008 [P] [FOUNDATION] Test Operation dataclass in `tests/unit/test_task_model.py`
- [ ] T009 [P] [FOUNDATION] Test TaskStore initialization in `tests/unit/test_task_store.py`
- [ ] T010 [P] [FOUNDATION] Test InputParser initialization in `tests/unit/test_input_parser.py`

### Implementation for Foundational

#### Data Models (Task, Intent, Operation)

- [ ] T011 [P] [FOUNDATION] Create `src/task_model.py` with Task dataclass
  - Fields: id (int), title (str), status (str), due_date (Optional[str]), created_at (datetime)
  - Validation: status must be "pending" or "completed"
- [ ] T012 [P] [FOUNDATION] Create `src/task_model.py` with Intent dataclass
  - Fields: action (str), target (Optional[str]), new_title (Optional[str]), due_date (Optional[str])
- [ ] T013 [P] [FOUNDATION] Create `src/task_model.py` with Operation dataclass
  - Fields: action (str), task_id (Optional[int]), before_state (Optional[Task]), timestamp (datetime)

#### State Management (TaskStore)

- [ ] T014 [FOUNDATION] Create `src/task_store.py` with TaskStore class
  - `__init__`: `_tasks` (dict), `_next_id` (int=1), `_history` (list)
  - `add_task(title, due_date)` → returns Task, records Operation
  - `list_tasks()` → returns list[Task] sorted by ID
  - `find_task(reference)` → returns Optional[Task], raises AmbiguousTaskError on multiple matches
- [ ] T015 [FOUNDATION] Add `update_task(task_id, title, due_date)` to TaskStore
  - Records Operation with before_state snapshot
- [ ] T016 [FOUNDATION] Add `complete_task(task_id)` to TaskStore
  - Records Operation with before_state snapshot
- [ ] T017 [FOUNDATION] Add `delete_task(task_id)` to TaskStore
  - Records Operation with before_state snapshot, removes from dict
- [ ] T018 [FOUNDATION] Add `undo()` to TaskStore
  - Reverses last Operation, returns undone Operation or None

#### Error Classes

- [ ] T019 [P] [FOUNDATION] Create `src/exceptions.py` with error classes
  - `ParserError` (base), `AmbiguousInputError`, `UnknownCommandError`, `MissingTitleError`
  - `TaskNotFoundError`, `AmbiguousTaskError`, `AlreadyCompletedError`, `NoHistoryError`
  - Each has `user_message()` method returning str

#### Input Parser

- [ ] T020 [FOUNDATION] Create `src/input_parser.py` with InputParser class
  - `parse(raw_input: str) -> Intent | ParserError`
  - ACTION_PATTERNS dict mapping actions to regex patterns
  - Due date extraction helper

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks using natural language

**Independent Test**: Run "add task Buy milk" → verify task with title "Buy milk" created

### Tests for US1 (Write FIRST, Ensure FAIL)

- [ ] T021 [P] [US1] Test add command parsing in `tests/unit/test_input_parser.py`
  - "add task Buy milk" → Intent(action="add", new_title="Buy milk")
  - "add Buy milk by tomorrow" → Intent(action="add", new_title="Buy milk", due_date="tomorrow")
- [ ] T022 [US1] Test TaskStore.add_task in `tests/unit/test_task_store.py`
  - Creates task with unique ID
  - Status defaults to "pending"
  - Created_at is set
- [ ] T023 [US1] Test add workflow in `tests/integration/test_workflows.py`
  - "add task Buy milk" → list shows task with correct title

### Implementation for US1

- [ ] T024 [P] [US1] Implement add pattern matching in InputParser
  - Match: r"add task (.+)", r"add (.+)", r"new task (.+)", r"create task (.+)"
  - Extract due date if " by " present in title
- [ ] T025 [US1] Implement _add method in Executor (depends on T014, T020)
  - Validate title present
  - Call store.add_task()
  - Return success message with task ID

**Checkpoint**: Add task works, list shows task, MVP functional

---

## Phase 4: User Story 2 - List Tasks (Priority: P1)

**Goal**: Users can see all their tasks

**Independent Test**: Add 3 tasks, run "list" → verify all 3 appear with IDs, titles, statuses, due dates

### Tests for US2 (Write FIRST, Ensure FAIL)

- [ ] T026 [P] [US2] Test list command parsing in `tests/unit/test_input_parser.py`
  - "list tasks", "show tasks", "list" → Intent(action="list")
- [ ] T027 [US2] Test TaskStore.list_tasks in `tests/unit/test_task_store.py`
  - Returns tasks sorted by ID
  - Empty store returns empty list
- [ ] T028 [US2] Test list output formatting in `tests/integration/test_workflows.py`
  - Add 2 tasks, list → formatted table with ID, title, status, due

### Implementation for US2

- [ ] T029 [P] [US2] Implement list pattern matching in InputParser
- [ ] T030 [US2] Implement _list method in Executor
  - Get tasks from store.list_tasks()
  - Format as table or "No tasks found" message

**Checkpoint**: List tasks works correctly, empty state handled

---

## Phase 5: User Story 3 - Complete Tasks (Priority: P1)

**Goal**: Users can mark tasks as done

**Independent Test**: Add task, "complete Buy milk" → verify status changes to "completed"

### Tests for US3 (Write FIRST, Ensure FAIL)

- [ ] T031 [P] [US3] Test complete command parsing in `tests/unit/test_input_parser.py`
  - "complete Buy milk", "mark Buy milk done", "finish Buy milk" → Intent(action="complete")
- [ ] T032 [US3] Test TaskStore.find_task by title in `tests/unit/test_task_store.py`
  - Exact title match returns task
  - Partial match returns first match
  - No match returns None
  - Multiple matches raises AmbiguousTaskError
- [ ] T033 [US3] Test TaskStore.complete_task in `tests/unit/test_task_store.py`
  - Status changes to "completed"
  - Raises AlreadyCompletedError if already done
- [ ] T034 [US3] Test complete workflow in `tests/integration/test_workflows.py`
  - Add task, complete, list → shows "completed"

### Implementation for US3

- [ ] T035 [P] [US3] Implement complete/update/delete pattern matching in InputParser
  - complete: r"complete (.+)", r"mark (.+) done", r"finish (.+)"
  - update: r"update (.+) to (.+)", r"change (.+) to (.+)"
  - delete: r"delete (.+)", r"remove (.+)"
- [ ] T036 [US3] Implement _complete method in Executor
  - Find task by reference
  - Call store.complete_task()
  - Return success message

**Checkpoint**: Complete task works, status updates correctly

---

## Phase 6: User Story 4 - Update Tasks (Priority: P2)

**Goal**: Users can modify task title or due date

**Independent Test**: Add task, "update Buy milk to Buy eggs" → verify title changed

### Tests for US4 (Write FIRST, Ensure FAIL)

- [ ] T037 [P] [US4] Test update command parsing in `tests/unit/test_input_parser.py`
  - "update Buy milk to Buy eggs" → Intent(action="update", target="Buy milk", new_title="Buy eggs")
  - "set due date for Buy milk to tomorrow" → extracts due_date
- [ ] T038 [US4] Test TaskStore.update_task in `tests/unit/test_task_store.py`
  - Title update works
  - Due date update works
  - Both update together
- [ ] T039 [US4] Test update workflow in `tests/integration/test_workflows.py`
  - Add task, update title, list → new title shown

### Implementation for US4

- [ ] T040 [US4] Implement update parsing with title/date extraction
- [ ] T041 [US4] Implement _update method in Executor
  - Find task by target
  - Call store.update_task()
  - Return success message

**Checkpoint**: Update task works for title and due date

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Users can remove tasks

**Independent Test**: Add 2 tasks, delete one, list → only one remains

### Tests for US5 (Write FIRST, Ensure FAIL)

- [ ] T042 [P] [US5] Test delete command parsing in `tests/unit/test_input_parser.py`
  - "delete Buy milk", "remove Buy milk" → Intent(action="delete")
- [ ] T043 [US5] Test TaskStore.delete_task in `tests/unit/test_task_store.py`
  - Task removed from dict
  - Operation recorded for undo
- [ ] T044 [US5] Test delete workflow in `tests/integration/test_workflows.py`
  - Add 2 tasks, delete one, list → only one shown

### Implementation for US5

- [ ] T045 [US5] Implement delete parsing
- [ ] T046 [US5] Implement _delete method in Executor
  - Find task by target
  - Call store.delete_task()
  - Return success message

**Checkpoint**: Delete task works, list updates correctly

---

## Phase 8: User Story 6 - Natural Language Understanding (Priority: P2)

**Goal**: Flexible command phrasing supported

**Independent Test**: "complete task 1", "mark task 1 done", "finish task 1" all mark task 1 complete

### Tests for US6 (Write FIRST, Ensure FAIL)

- [ ] T047 [P] [US6] Test all phrasing variants in `tests/unit/test_input_parser.py`
  - Verify each action supports multiple regex patterns
  - Verify due date extraction works in various positions
- [ ] T048 [US6] Test ambiguous input handling in `tests/unit/test_input_parser.py`
  - "update task" without target → raises AmbiguousInputError
  - Error message prompts for clarification
- [ ] T049 [US6] Test task not found error in `tests/integration/test_workflows.py`
  - "complete NonExistent" → "Task 'NonExistent' not found. Did you mean to create it?"

### Implementation for US6

- [ ] T050 [US6] Add all remaining action patterns to ACTION_PATTERNS
- [ ] T051 [US6] Implement due date extraction helper
- [ ] T052 [US6] Implement error message formatting in Executor

**Checkpoint**: All command variations work, errors are helpful

---

## Phase 9: User Story 7 - Undo (Priority: P2)

**Goal**: Users can reverse the last operation

**Independent Test**: Add task, complete it, undo → task status back to pending

### Tests for US7 (Write FIRST, Ensure FAIL)

- [ ] T053 [P] [US7] Test TaskStore.undo for add in `tests/unit/test_task_store.py`
  - Add task, undo → task removed
- [ ] T054 [P] [US7] Test TaskStore.undo for complete in `tests/unit/test_task_store.py`
  - Complete task, undo → status back to pending
- [ ] T055 [P] [US7] Test TaskStore.undo for update in `tests/unit/test_task_store.py`
  - Update task, undo → original title/date restored
- [ ] T056 [P] [US7] Test TaskStore.undo for delete in `tests/unit/test_task_store.py`
  - Delete task, undo → task restored
- [ ] T057 [US7] Test undo workflow in `tests/integration/test_workflows.py`
  - Add → Complete → Undo → List → shows "pending"

### Implementation for US7

- [ ] T058 [P] [US7] Add undo pattern to InputParser
  - "undo", "undo last" → Intent(action="undo")
- [ ] T059 [US7] Implement _undo method in Executor
  - Call store.undo()
  - Return message describing what was undone
  - Handle NoHistoryError ("Nothing to undo")

**Checkpoint**: Undo works for all operation types

---

## Phase 10: Help and Exit (Priority: P1)

**Goal**: Users can get help and exit cleanly

### Tests for Help/Exit (Write FIRST, Ensure FAIL)

- [ ] T060 [P] [HELP] Test help command parsing in `tests/unit/test_input_parser.py`
  - "help", "show help" → Intent(action="help")
- [ ] T061 [P] [HELP] Test exit command parsing in `tests/unit/test_input_parser.py`
  - "exit", "quit", "bye" → Intent(action="exit")
- [ ] T062 [HELP] Test help output in `tests/integration/test_workflows.py`
  - "help" → shows all commands with examples

### Implementation for Help/Exit

- [ ] T063 [P] [HELP] Add help/exit patterns to InputParser
- [ ] T064 [HELP] Implement _help method in Executor
  - Returns formatted help text with all commands and examples
- [ ] T065 [HELP] Implement _exit method in Executor
  - Returns farewell message

---

## Phase 11: CLI Integration

**Goal**: REPL loop and main entry point

### Tests for CLI (Write FIRST, Ensure FAIL)

- [ ] T066 [P] [CLI] Test empty input handling in `tests/unit/test_cli.py`
- [ ] T067 [P] [CLI] Test Ctrl+C handling (manual test)
- [ ] T068 [CLI] Test complete REPL workflow in `tests/integration/test_workflows.py`
  - Simulate: add → list → complete → list → undo → list

### Implementation for CLI

- [ ] T069 [CLI] Create `src/cli.py` with main() function
  - Entry point: `python -m src` or `python src/cli.py`
- [ ] T070 [CLI] Create CLI class with REPL loop
  - Print welcome message
  - Read from stdin with " > " prompt
  - Handle empty input gracefully
  - Handle Ctrl+C with "Goodbye!"
  - Call parser.parse() → executor.execute()
  - Print result message
  - Exit on "exit" action

---

## Phase 12: Utility Functions

- [ ] T071 [P] Create `src/utils.py` with date parsing helpers
  - Detect "by [date]" patterns
  - Return due_date string as-is (no parsing required per spec)
- [ ] T072 [P] Create `src/output.py` with output formatting
  - Format task list as table
  - Format success/error messages consistently

---

## Phase 13: Integration Tests (All Workflows)

**Run after all phases complete**

- [ ] T073 [INTEG] Test add → list workflow
- [ ] T074 [INTEG] Test add → complete → list workflow
- [ ] T075 [INTEG] Test add → update → list workflow
- [ ] T076 [INTEG] Test add → delete → list workflow
- [ ] T077 [INTEG] Test add → complete → undo → list workflow
- [ ] T078 [INTEG] Test error handling (not found, already completed)
- [ ] T079 [INTEG] Test multiple tasks with same title (disambiguation)

---

## Phase 14: Code Quality & Polish

- [ ] T080 [P] Run linting (ruff or flake8) on all Python files
- [ ] T081 [P] Run type checking (mypy) on all Python files
- [ ] T082 [P] Verify ≥80% test coverage with `pytest --cov`
- [ ] T083 Review checklist.md and verify all items pass
- [ ] T084 [P] Add module docstrings to all files
- [ ] T085 [P] Add type hints where missing

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|------------|--------|
| Phase 1: Setup | None | - |
| Phase 2: Foundational | Phase 1 | All user stories |
| Phase 3-10: User Stories | Phase 2 | - |
| Phase 11: CLI | Phases 3-10 | Integration tests |
| Phase 12: Utils | Phase 2 | - |
| Phase 13: Integration | All above | - |
| Phase 14: Polish | All above | - |

### User Story Dependencies

| Story | Depends On | Can Test Independently |
|-------|------------|------------------------|
| US1: Add | Foundational | Yes - after add tests pass |
| US2: List | Foundational | Yes - after list tests pass |
| US3: Complete | Foundational | Yes - but needs add for full test |
| US4: Update | Foundational | Yes - needs add |
| US5: Delete | Foundational | Yes - needs add |
| US6: NL Understanding | Foundational | Yes - needs add for full test |
| US7: Undo | Foundational | Yes - needs add/complete |

### Parallel Opportunities

- All T00x [P] tasks marked with [P] can run in parallel
- Once Foundational is done, all user story phases can proceed in parallel
- Models (T011-T013) can be done in parallel
- Test files for same module can be done in parallel

---

## Implementation Strategy: Red-Green-Refactor

### For Each Task with Tests:

1. **Red**: Write test, verify it FAILS
2. **Green**: Write minimal code to make test pass
3. **Refactor**: Clean up, ensure <50 line functions, add docstrings
4. **Commit**: Save progress

### Example Workflow:

```bash
# 1. Write test for Task dataclass
pytest tests/unit/test_task_model.py -v  # Should FAIL

# 2. Implement Task dataclass
python -c "from src.task_model import Task; t = Task(...)"  # Should work

# 3. Run test again
pytest tests/unit/test_task_model.py -v  # Should PASS

# 4. Refactor and verify coverage
pytest tests/unit/test_task_model.py --cov=src.task_model --cov-report=term-missing
```

---

## File Summary

| Phase | Files Created |
|-------|---------------|
| Setup | `requirements.txt`, `pyproject.toml` |
| Foundational | `src/task_model.py`, `src/task_store.py`, `src/exceptions.py`, `src/input_parser.py` |
| US1-7 | `src/executor.py` (all actions) |
| CLI | `src/cli.py`, `src/utils.py`, `src/output.py` |
| Tests | `tests/unit/test_*.py`, `tests/integration/test_workflows.py` |

---

## Quick Start

```bash
# Phase 1-2: Foundation
pytest tests/unit/test_task_model.py -v     # T006-T008
pytest tests/unit/test_task_store.py -v     # T009, T014-T018
pytest tests/unit/test_input_parser.py -v   # T010, T020

# Phase 3: Add
pytest tests/unit/test_input_parser.py -v -k "add"   # T021
pytest tests/unit/test_task_store.py -v -k "add"     # T022
pytest tests/integration/test_workflows.py -v        # T023

# Phase 11: CLI
pytest tests/integration/test_workflows.py -v        # T068
```
