# Tasks: Spec-Driven Todo Console Application

**Input**: Design documents from `/specs/006-todo-console-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: Test tasks are included per TDD requirements from constitution. Write tests FIRST (Red-Green-Refactor cycle).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: `src/`, `tests/unit/`, `tests/integration/`
- [ ] T002 [P] Create `pyproject.toml` with Python 3.11+ requirement and pytest dependency
- [ ] T003 [P] Create `.gitignore` for Python (`__pycache__/`, `*.pyc`, `.pytest_cache/`)
- [ ] T004 [P] Create empty `__init__.py` files in `src/` and test directories
- [ ] T005 [P] Create `README.md` with project overview and setup instructions

**Checkpoint**: Basic project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Foundational Models

- [ ] T006 [P] Define enums in `src/task_model.py`: TaskStatus, Priority, OperationType
- [ ] T007 [P] Define Task dataclass in `src/task_model.py` with validation in `__post_init__`
- [ ] T008 [P] Define Command dataclass in `src/task_model.py`
- [ ] T009 [P] Define CommandResult dataclass in `src/task_model.py`
- [ ] T010 [P] Define ParseError and ValidationError exceptions in `src/task_model.py`

### Foundational Storage

- [ ] T011 Create TaskStore class in `src/task_store.py` with `__init__`, `_tasks` dict, `_next_id` counter
- [ ] T012 Implement TaskStore.add() method - assign ID, store task, return ID
- [ ] T013 Implement TaskStore.get() method - retrieve task by ID, return Optional[Task]
- [ ] T014 Implement TaskStore.get_all() method - return all tasks sorted by ID
- [ ] T015 Implement TaskStore.update() method - replace task at given ID, return success bool
- [ ] T016 Implement TaskStore.delete() method - remove task by ID, return success bool
- [ ] T017 Implement TaskStore.count() method - return total number of tasks

### Foundational Utilities

- [ ] T018 [P] Create `src/todo_utils.py` with format_task() function
- [ ] T019 [P] Implement format_task_list() function in `src/todo_utils.py`
- [ ] T020 [P] Implement validate_title() function in `src/todo_utils.py`
- [ ] T021 [P] Implement normalize_text() function in `src/todo_utils.py`

### Foundational Tests

- [ ] T022 [P] Write unit tests for Task model in `tests/unit/test_task_model.py` (valid data, invalid ID, invalid title, enum validation)
- [ ] T023 [P] Write unit tests for TaskStatus, Priority, OperationType enums in `tests/unit/test_task_model.py`
- [ ] T024 [P] Write unit tests for Command and CommandResult in `tests/unit/test_task_model.py`
- [ ] T025 [P] Write unit tests for TaskStore.add() in `tests/unit/test_task_store.py` (ID assignment, storage, sequence)
- [ ] T026 [P] Write unit tests for TaskStore.get() in `tests/unit/test_task_store.py` (found, not found)
- [ ] T027 [P] Write unit tests for TaskStore CRUD operations in `tests/unit/test_task_store.py` (update, delete, get_all)
- [ ] T028 [P] Write unit tests for utilities in `tests/unit/test_todo_utils.py`

**Checkpoint**: Foundation ready - all models, storage, and utilities tested and working

---

## Phase 3: User Story 1 - Basic Todo Operations (Priority: P1) 🎯 MVP

**Goal**: Users can add, list, and complete todos through natural language commands in a CLI

**Independent Test**: Run CLI, add 3 tasks, list them, complete one task, verify state changes

**Acceptance Criteria**:
1. User can add task with "add task: <title>"
2. User can add task with priority: "add task: <title> with priority high"
3. User can list all tasks with "list tasks"
4. User can complete task with "complete task <id>"

### Parser for User Story 1

- [ ] T029 [P] [US1] Create InputParser class in `src/input_parser.py` with parse() method stub
- [ ] T030 [P] [US1] Implement InputParser._detect_operation() to identify ADD, LIST, COMPLETE, EXIT operations
- [ ] T031 [P] [US1] Implement InputParser._extract_add_params() to extract title and priority from "add task" commands
- [ ] T032 [P] [US1] Implement InputParser._extract_task_id() to extract numeric ID from text
- [ ] T033 [US1] Wire up InputParser.parse() to route to operation-specific extractors and return Command

### Parser Tests for User Story 1

- [ ] T034 [P] [US1] Write test for parsing "add task: write documentation" in `tests/unit/test_input_parser.py`
- [ ] T035 [P] [US1] Write test for parsing "add task: X with priority high" in `tests/unit/test_input_parser.py`
- [ ] T036 [P] [US1] Write test for parsing "list tasks" in `tests/unit/test_input_parser.py`
- [ ] T037 [P] [US1] Write test for parsing "complete task 5" in `tests/unit/test_input_parser.py`
- [ ] T038 [P] [US1] Write test for parsing "exit" command in `tests/unit/test_input_parser.py`
- [ ] T039 [P] [US1] Write test for invalid command (raises ParseError) in `tests/unit/test_input_parser.py`
- [ ] T040 [P] [US1] Write test for empty input handling in `tests/unit/test_input_parser.py`

### Executor for User Story 1

- [ ] T041 [P] [US1] Create TodoExecutor class in `src/todo_executor.py` with __init__(store: TaskStore)
- [ ] T042 [P] [US1] Implement TodoExecutor.execute() to route commands to operation handlers
- [ ] T043 [P] [US1] Implement TodoExecutor._handle_add() to create Task and call store.add()
- [ ] T044 [P] [US1] Implement TodoExecutor._handle_list() to call store.get_all() and return CommandResult with data
- [ ] T045 [US1] Implement TodoExecutor._handle_complete() to get task, update status, call store.update()

### Executor Tests for User Story 1

- [ ] T046 [P] [US1] Write test for execute ADD command in `tests/unit/test_todo_executor.py` (verify task created)
- [ ] T047 [P] [US1] Write test for execute LIST command in `tests/unit/test_todo_executor.py` (verify tasks returned)
- [ ] T048 [P] [US1] Write test for execute COMPLETE command in `tests/unit/test_todo_executor.py` (found and not found cases)
- [ ] T049 [P] [US1] Write test for ADD with different priorities in `tests/unit/test_todo_executor.py`
- [ ] T050 [P] [US1] Write test for error handling (task not found) in `tests/unit/test_todo_executor.py`

### CLI for User Story 1

- [ ] T051 [US1] Create main() function in `src/todo_cli.py` with REPL loop
- [ ] T052 [US1] Implement display_welcome() in `src/todo_cli.py` with welcome message and instructions
- [ ] T053 [US1] Implement display_result() in `src/todo_cli.py` to format and print CommandResult
- [ ] T054 [US1] Wire up main() to create TaskStore, InputParser, TodoExecutor and run REPL
- [ ] T055 [US1] Add Ctrl+C signal handling for graceful exit in `src/todo_cli.py`
- [ ] T056 [US1] Add display_error() for error formatting with color (if terminal supports it)

### Integration Tests for User Story 1

- [ ] T057 [US1] Write integration test for complete workflow in `tests/integration/test_todo_workflows.py`: add 3 tasks → list → complete one → verify
- [ ] T058 [US1] Write integration test for add with priority in `tests/integration/test_todo_workflows.py`
- [ ] T059 [US1] Write integration test for empty list scenario in `tests/integration/test_todo_workflows.py`
- [ ] T060 [US1] Write integration test for spec-driven flow validation in `tests/integration/test_sdd_workflow.py`: parse (no side effects) → execute (state changes)

### Manual Testing for User Story 1

- [ ] T061 [US1] Manual test: Run CLI, add task, verify ID assignment and confirmation message
- [ ] T062 [US1] Manual test: Add 3 tasks with different priorities, list, verify display formatting
- [ ] T063 [US1] Manual test: Complete task, list again, verify status changed
- [ ] T064 [US1] Manual test: Try to complete non-existent task, verify error message

**Checkpoint**: MVP complete - users can add, list, and complete tasks through CLI

---

## Phase 4: User Story 2 - Task Filtering and Search (Priority: P2)

**Goal**: Users can filter tasks by status (pending/completed) and search by keyword

**Independent Test**: Create 10 tasks (5 pending, 5 completed), filter by status, search by keyword, verify correct subsets

**Acceptance Criteria**:
1. User can list pending tasks only with "list pending tasks"
2. User can list completed tasks only with "list completed tasks"
3. User can search by keyword with "search <query>"

### Storage Extensions for User Story 2

- [ ] T065 [P] [US2] Implement TaskStore.filter_by_status() in `src/task_store.py` - return List[Task] matching status
- [ ] T066 [P] [US2] Implement TaskStore.search() in `src/task_store.py` - case-insensitive title search
- [ ] T067 [P] [US2] Write unit tests for filter_by_status() in `tests/unit/test_task_store.py`
- [ ] T068 [P] [US2] Write unit tests for search() in `tests/unit/test_task_store.py` (matches, no matches, case insensitive)

### Parser Extensions for User Story 2

- [ ] T069 [P] [US2] Extend InputParser._detect_operation() to recognize SEARCH operation
- [ ] T070 [P] [US2] Implement InputParser._extract_search_query() to extract keyword from "search <query>"
- [ ] T071 [P] [US2] Extend InputParser._extract_list_params() to detect "pending" or "completed" filters
- [ ] T072 [P] [US2] Write test for parsing "list pending tasks" in `tests/unit/test_input_parser.py`
- [ ] T073 [P] [US2] Write test for parsing "list completed tasks" in `tests/unit/test_input_parser.py`
- [ ] T074 [P] [US2] Write test for parsing "search documentation" in `tests/unit/test_input_parser.py`

### Executor Extensions for User Story 2

- [ ] T075 [P] [US2] Implement TodoExecutor._handle_search() to call store.search() and return results
- [ ] T076 [US2] Update TodoExecutor._handle_list() to support filter parameter (pending/completed/all)
- [ ] T077 [P] [US2] Write test for execute LIST with pending filter in `tests/unit/test_todo_executor.py`
- [ ] T078 [P] [US2] Write test for execute LIST with completed filter in `tests/unit/test_todo_executor.py`
- [ ] T079 [P] [US2] Write test for execute SEARCH command in `tests/unit/test_todo_executor.py`

### Integration Tests for User Story 2

- [ ] T080 [US2] Write integration test in `tests/integration/test_todo_workflows.py`: create 10 tasks (5 pending, 5 completed) → filter by pending → verify count
- [ ] T081 [US2] Write integration test for search workflow in `tests/integration/test_todo_workflows.py`: create tasks with "documentation" and "code" → search "doc" → verify matches
- [ ] T082 [US2] Write integration test for search with no matches in `tests/integration/test_todo_workflows.py`

### Manual Testing for User Story 2

- [ ] T083 [US2] Manual test: Create 10 tasks, complete 5, list pending, verify only 5 shown
- [ ] T084 [US2] Manual test: Search for keyword, verify correct tasks returned
- [ ] T085 [US2] Manual test: Search with no matches, verify helpful message

**Checkpoint**: Filtering and search complete - users can find specific tasks easily

---

## Phase 5: User Story 3 - Task Deletion and Editing (Priority: P3)

**Goal**: Users can delete tasks and update task properties (title, priority) through natural language commands

**Independent Test**: Create tasks, delete one, update another's title and priority, verify state changes

**Acceptance Criteria**:
1. User can delete task with "delete task <id>"
2. User can update title with "update task <id> title to <new_title>"
3. User can update priority with "update task <id> priority to <high|medium|low>"

### Parser Extensions for User Story 3

- [ ] T086 [P] [US3] Extend InputParser._detect_operation() to recognize DELETE and UPDATE operations
- [ ] T087 [P] [US3] Implement InputParser._extract_update_params() to parse title and priority updates
- [ ] T088 [P] [US3] Write test for parsing "delete task 5" in `tests/unit/test_input_parser.py`
- [ ] T089 [P] [US3] Write test for parsing "update task 1 title to new title" in `tests/unit/test_input_parser.py`
- [ ] T090 [P] [US3] Write test for parsing "update task 3 priority to high" in `tests/unit/test_input_parser.py`
- [ ] T091 [P] [US3] Write test for parsing "change task 2 priority to low" in `tests/unit/test_input_parser.py`

### Executor Extensions for User Story 3

- [ ] T092 [P] [US3] Implement TodoExecutor._handle_delete() to call store.delete() and return result
- [ ] T093 [P] [US3] Implement TodoExecutor._handle_update() to get task, create updated Task, call store.update()
- [ ] T094 [P] [US3] Write test for execute DELETE command in `tests/unit/test_todo_executor.py` (found and not found)
- [ ] T095 [P] [US3] Write test for execute UPDATE title in `tests/unit/test_todo_executor.py`
- [ ] T096 [P] [US3] Write test for execute UPDATE priority in `tests/unit/test_todo_executor.py`
- [ ] T097 [P] [US3] Write test for UPDATE with invalid task ID in `tests/unit/test_todo_executor.py`

### Integration Tests for User Story 3

- [ ] T098 [US3] Write integration test in `tests/integration/test_todo_workflows.py`: create 3 tasks → delete task 2 → list → verify only 2 remain
- [ ] T099 [US3] Write integration test for update workflow in `tests/integration/test_todo_workflows.py`: create task → update title → update priority → verify changes
- [ ] T100 [US3] Write integration test for delete non-existent task in `tests/integration/test_todo_workflows.py`

### Manual Testing for User Story 3

- [ ] T101 [US3] Manual test: Create tasks, delete one, verify removal and confirmation
- [ ] T102 [US3] Manual test: Update task title, verify change persists
- [ ] T103 [US3] Manual test: Update task priority, verify change persists

**Checkpoint**: All user stories complete - full CRUD + search functionality working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve UX, error messages, documentation, and overall quality

### Error Handling Improvements

- [ ] T104 [P] Review all error messages for clarity and add suggestions (e.g., "Task #5 not found. Use 'list' to see all tasks.")
- [ ] T105 [P] Add comprehensive ParseError handling in CLI with helpful examples
- [ ] T106 [P] Test edge case: empty input (should be ignored gracefully)
- [ ] T107 [P] Test edge case: whitespace-only input (should be ignored gracefully)
- [ ] T108 [P] Test edge case: complete already completed task (should show warning, not error)

### Display Improvements

- [ ] T109 [P] Improve task list formatting with better alignment and symbols (☐ for pending, ☑ for completed)
- [ ] T110 [P] Add color output support (green for success, red for errors, yellow for warnings) if terminal supports it
- [ ] T111 [P] Add "No tasks found" message with helpful suggestion when list is empty
- [ ] T112 [P] Improve welcome message with quick start examples

### Command Variations

- [ ] T113 [P] Add "create task" as alias for "add task" in parser
- [ ] T114 [P] Add "new task" as alias for "add task" in parser
- [ ] T115 [P] Add "show tasks" as alias for "list tasks" in parser
- [ ] T116 [P] Add "done <id>" as alias for "complete task <id>" in parser
- [ ] T117 [P] Add "remove task" as alias for "delete task" in parser
- [ ] T118 [P] Add "find" as alias for "search" in parser
- [ ] T119 [P] Write tests for all command variations in `tests/unit/test_input_parser.py`

### Documentation

- [ ] T120 [P] Create `specs/006-todo-console-app/USAGE.md` with comprehensive usage examples
- [ ] T121 [P] Add troubleshooting section to README.md
- [ ] T122 [P] Document command patterns and variations in README.md
- [ ] T123 [P] Add architecture diagram to README.md showing 5-layer separation

### Performance & Quality

- [ ] T124 [P] Run pytest with coverage, verify ≥ 80% coverage
- [ ] T125 [P] Run mypy for type checking, fix any type errors
- [ ] T126 [P] Test with 1000 tasks, verify operations complete < 100ms
- [ ] T127 [P] Profile search operation with 1000 tasks, optimize if needed

### Final Validation

- [ ] T128 Run all unit tests and verify 100% pass rate
- [ ] T129 Run all integration tests and verify 100% pass rate
- [ ] T130 Manual end-to-end test of all user stories
- [ ] T131 Verify all acceptance criteria from spec.md are met

**Checkpoint**: Application polished and production-ready

---

## Implementation Strategy

### MVP First (Minimum Viable Product)
**Phase 3 (User Story 1) IS the MVP**. Implement and test this completely before moving to Phase 4 or 5.

**Why**: User Story 1 delivers immediate value (basic todo manager). If time is constrained, ship Phase 3 first.

### Incremental Delivery
Each user story phase is independently deployable:
- **After Phase 3**: Users can add, list, complete tasks (MVP)
- **After Phase 4**: Users can also filter and search (enhanced UX)
- **After Phase 5**: Users can also delete and update (full featured)

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**:
```bash
# Can run in parallel (different files):
- T006-T010 (all model definitions)
- T018-T021 (all utility functions)
- T022-T028 (all tests, different files)

# Must run sequentially:
- T011-T017 (TaskStore methods, same file, depend on T011)
```

**Within Phase 3 (User Story 1)**:
```bash
# Can run in parallel:
- T029-T033 (parser methods, different methods)
- T034-T040 (parser tests, different test files or functions)
- T041-T045 (executor methods, different methods)
- T046-T050 (executor tests, different test functions)

# Must run sequentially:
- T051-T056 (CLI functions, same file, integration)
- T057-T060 (integration tests, require full system working)
```

### TDD Workflow (Red-Green-Refactor)

For each component:
1. **Red**: Write test first (T022-T028, T034-T040, T046-T050, etc.)
2. **Green**: Implement minimum code to pass (T006-T021, T029-T045, etc.)
3. **Refactor**: Clean up implementation while keeping tests green

Example for Task model:
```
1. Write T022 (test Task with valid data) → FAILS ❌
2. Implement T007 (Task dataclass) → PASSES ✅
3. Write T022 (test Task with invalid ID) → FAILS ❌
4. Add validation to T007 → PASSES ✅
```

---

## Dependencies

### Phase Dependencies
- **Phase 2** must complete before **Phase 3, 4, 5** (foundational models required)
- **Phase 3** must complete before **Phase 6** (need working CLI for polish)
- **Phase 4** and **Phase 5** can be done in any order after Phase 3

### Task Dependencies (Within Phases)

**Phase 2**:
- T012-T017 depend on T011 (TaskStore class must exist)
- T022-T024 depend on T006-T010 (models must exist to test)
- T025-T027 depend on T011-T017 (storage must exist to test)

**Phase 3**:
- T029 must complete before T030-T033 (class must exist)
- T033 must complete before T029 (route to extractors)
- T041 must complete before T042-T045 (executor class must exist)
- T051-T056 depend on T041 (need executor to wire up)
- T057-T060 depend on T051-T056 (need working CLI)

---

## Acceptance Criteria Summary

### From spec.md User Stories

**User Story 1 (P1)**:
- [x] Add task with title
- [x] Add task with priority
- [x] List all tasks
- [x] Complete task by ID
- [x] Unique ID assignment
- [x] Clear confirmation messages

**User Story 2 (P2)**:
- [x] List pending tasks
- [x] List completed tasks
- [x] Search by keyword
- [x] Accurate results

**User Story 3 (P3)**:
- [x] Delete task by ID
- [x] Update task title
- [x] Update task priority
- [x] Immediate state reflection

### From Requirements

- [x] FR-001: Accept CLI text commands
- [x] FR-002: Parse natural language → structured specs
- [x] FR-003: Support add, list, complete, delete, update, search
- [x] FR-004: In-memory storage
- [x] FR-005: Validate before execution
- [x] FR-006: Clear success feedback
- [x] FR-007: Helpful error messages
- [x] FR-008: Unique ID assignment
- [x] FR-009: Priority support (HIGH, MEDIUM, LOW)
- [x] FR-010: Filter by status
- [x] NFR-001: Operations < 100ms
- [x] NFR-002: Support 1000+ tasks
- [x] NFR-005: Testable without interaction

### From Architecture

- [x] Clear spec-execution boundary (Parser → Command → Executor)
- [x] All layers testable in isolation
- [x] No layer violations
- [x] Type safety (mypy passes)
- [x] Test coverage ≥ 80%

---

## Estimated Timeline

- **Phase 1 (Setup)**: 1 hour (5 tasks)
- **Phase 2 (Foundation)**: 4-6 hours (23 tasks)
- **Phase 3 (User Story 1 - MVP)**: 6-8 hours (33 tasks)
- **Phase 4 (User Story 2)**: 3-4 hours (21 tasks)
- **Phase 5 (User Story 3)**: 3-4 hours (18 tasks)
- **Phase 6 (Polish)**: 3-4 hours (27 tasks)

**Total**: 20-27 hours for complete implementation

**MVP Only** (Phases 1-3): 11-15 hours

---

## Success Metrics

- [ ] All 131 tasks completed and checked off
- [ ] All tests passing (unit + integration)
- [ ] Test coverage ≥ 80%
- [ ] mypy type checking passes with no errors
- [ ] All user stories independently testable
- [ ] All acceptance criteria met
- [ ] Performance requirements satisfied (< 100ms operations)
- [ ] Manual testing successful for all scenarios

---

## Next Steps

1. **Start with Phase 1**: Set up project structure (T001-T005)
2. **Complete Phase 2**: Build foundation (T006-T028) - CRITICAL before user stories
3. **Implement MVP**: Complete Phase 3 (User Story 1, T029-T064)
4. **Test MVP**: Verify independently functional
5. **Extend**: Add Phase 4 and 5 as time permits
6. **Polish**: Complete Phase 6 for production quality

---

**Task Generation Complete**: 131 tasks across 6 phases, organized by user story for independent implementation and testing.

**Ready for implementation**: Run `/sp.implement` or begin with Phase 1 Setup tasks.
