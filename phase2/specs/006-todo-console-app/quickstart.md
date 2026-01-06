# Quickstart: Spec-Driven Todo Console Application

**Feature**: 006-todo-console-app
**Date**: 2025-12-31

## Overview

This is a console-based todo manager that accepts natural language commands. All data is stored in memory (resets when you exit).

---

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Setup

```bash
# Clone repository (if needed)
cd in-memory-python-console-app

# Install dependencies (testing only)
pip install pytest pytest-cov

# Verify Python version
python --version  # Should be 3.11+
```

---

## Running the Application

```bash
# From repository root
python -m src.todo_cli

# Or if executable
./src/todo_cli.py
```

**Expected Output**:
```
╔══════════════════════════════════════════════╗
║   Spec-Driven Todo Console Application      ║
╚══════════════════════════════════════════════╝

Type commands in natural language.
Examples: 'add task: write docs', 'list tasks', 'complete task 1'
Type 'help' for more examples, 'exit' to quit.

>
```

---

## Basic Commands

### Add a Task

```bash
> add task: write documentation
✓ Task #1 created: 'write documentation' (priority: MEDIUM)

> add task: review pull requests with priority high
✓ Task #2 created: 'review pull requests' (priority: HIGH)
```

**Variations**:
- `create task: <title>`
- `new task: <title>`
- `add task: <title> with priority <high|medium|low>`

---

### List Tasks

```bash
> list tasks
Found 2 tasks:

[1] ☐ write documentation (MEDIUM) - 2025-12-31 10:30
[2] ☐ review pull requests (HIGH) - 2025-12-31 10:31
```

**Variations**:
- `list all tasks` (shows all)
- `list pending tasks` (shows only incomplete)
- `list completed tasks` (shows only finished)
- `show tasks`

---

### Complete a Task

```bash
> complete task 1
✓ Task #1 marked as completed: 'write documentation'

> list tasks
Found 2 tasks:

[1] ☑ write documentation (MEDIUM) - 2025-12-31 10:30 [COMPLETED]
[2] ☐ review pull requests (HIGH) - 2025-12-31 10:31
```

**Variations**:
- `mark task <id> as complete`
- `finish task <id>`
- `done <id>`

---

### Delete a Task

```bash
> delete task 1
✓ Task #1 deleted: 'write documentation'

> list tasks
Found 1 task:

[2] ☐ review pull requests (HIGH) - 2025-12-31 10:31
```

**Variations**:
- `remove task <id>`

---

### Update a Task

```bash
> update task 2 title to code review
✓ Task #2 updated: title changed to 'code review'

> change task 2 priority to low
✓ Task #2 updated: priority changed to LOW
```

**Variations**:
- `update task <id> title to <new_title>`
- `update task <id> priority to <high|medium|low>`
- `change task <id> priority to <high|medium|low>`

---

### Search Tasks

```bash
> search documentation
Found 1 task matching 'documentation':

[1] ☐ write documentation (MEDIUM) - 2025-12-31 10:30
```

**Variations**:
- `find <keyword>`

---

### Exit

```bash
> exit
Goodbye!
```

**Variations**:
- `quit`
- `q`
- Press `Ctrl+C`

---

## Complete Example Session

```bash
$ python -m src.todo_cli

> add task: implement parser
✓ Task #1 created: 'implement parser' (priority: MEDIUM)

> add task: write tests with priority high
✓ Task #2 created: 'write tests' (priority: HIGH)

> add task: update documentation with priority low
✓ Task #3 created: 'update documentation' (priority: LOW)

> list tasks
Found 3 tasks:

[1] ☐ implement parser (MEDIUM) - 2025-12-31 10:00
[2] ☐ write tests (HIGH) - 2025-12-31 10:01
[3] ☐ update documentation (LOW) - 2025-12-31 10:02

> complete task 1
✓ Task #1 marked as completed: 'implement parser'

> list pending tasks
Found 2 pending tasks:

[2] ☐ write tests (HIGH) - 2025-12-31 10:01
[3] ☐ update documentation (LOW) - 2025-12-31 10:02

> search tests
Found 1 task matching 'tests':

[2] ☐ write tests (HIGH) - 2025-12-31 10:01

> update task 3 priority to high
✓ Task #3 updated: priority changed to HIGH

> list tasks
Found 3 tasks:

[1] ☑ implement parser (MEDIUM) - 2025-12-31 10:00 [COMPLETED]
[2] ☐ write tests (HIGH) - 2025-12-31 10:01
[3] ☐ update documentation (HIGH) - 2025-12-31 10:02

> delete task 1
✓ Task #1 deleted: 'implement parser'

> list tasks
Found 2 tasks:

[2] ☐ write tests (HIGH) - 2025-12-31 10:01
[3] ☐ update documentation (HIGH) - 2025-12-31 10:02

> exit
Goodbye!
```

---

## Common Error Messages

### Task Not Found

```bash
> complete task 999
✗ Task #999 not found. Use 'list' to see all tasks.
```

### Invalid Command

```bash
> do something random
✗ Could not parse command.
  Try: add task: <title>, list tasks, complete task <id>
```

### Empty Input

```bash
>
(command ignored, prompt returns)
```

### Missing Required Information

```bash
> add task:
✗ Task title cannot be empty.
```

---

## Command Reference

| Operation | Example | Variations |
|-----------|---------|------------|
| **Add** | `add task: write docs` | `create task:`, `new task:` |
| **Add with priority** | `add task: review code with priority high` | Priority: `high`, `medium`, `low` |
| **List all** | `list tasks` | `list all tasks`, `show tasks` |
| **List filtered** | `list pending tasks` | `list completed tasks` |
| **Complete** | `complete task 1` | `mark task 1 as complete`, `finish task 1`, `done 1` |
| **Delete** | `delete task 1` | `remove task 1` |
| **Update title** | `update task 1 title to new title` | |
| **Update priority** | `update task 1 priority to high` | `change task 1 priority to high` |
| **Search** | `search keyword` | `find keyword` |
| **Exit** | `exit` | `quit`, `q`, `Ctrl+C` |

---

## Tips and Tricks

### 1. Natural Language Flexibility
The parser understands many variations. If one doesn't work, try rephrasing:
```bash
# All equivalent:
> add task: write tests
> create task: write tests
> new task: write tests
```

### 2. Task IDs
Tasks are assigned sequential IDs starting from 1. IDs are never reused, even after deletion:
```bash
> add task: first
✓ Task #1 created

> add task: second
✓ Task #2 created

> delete task 1

> add task: third
✓ Task #3 created  # Not #1!
```

### 3. Priority Defaults
If you don't specify priority, it defaults to MEDIUM:
```bash
> add task: something
# Creates task with priority: MEDIUM
```

### 4. Case Insensitive
Commands are case-insensitive:
```bash
> ADD TASK: WRITE DOCS
✓ Task #1 created: 'write docs'

> LIST TASKS
Found 1 task: ...
```

### 5. In-Memory Only
**Important**: All data is lost when you exit. This is by design (Phase 1 requirement).
```bash
> add task: important thing
> exit

$ python -m src.todo_cli
> list tasks
No tasks found.  # Data reset!
```

---

## Troubleshooting

### Problem: "Command not found"
**Symptom**: Shell says `python: command not found`
**Solution**: Try `python3` instead:
```bash
python3 -m src.todo_cli
```

### Problem: "ModuleNotFoundError: No module named 'src'"
**Symptom**: Python can't find the `src` module
**Solution**: Run from repository root:
```bash
cd /path/to/in-memory-python-console-app
python -m src.todo_cli
```

### Problem: Parser doesn't understand command
**Symptom**: "Could not parse command" error
**Solution**: Check command format. Use one of the exact patterns:
- `add task: <title>`
- `list tasks`
- `complete task <number>`
- etc.

### Problem: Task ID not found
**Symptom**: "Task #X not found"
**Solution**: Use `list tasks` to see valid task IDs

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_input_parser.py

# Run specific test
pytest tests/unit/test_input_parser.py::test_parse_add_command
```

**Expected Output**:
```
========================= test session starts ==========================
collected 45 items

tests/unit/test_task_model.py ........                          [ 17%]
tests/unit/test_task_store.py ...........                       [ 42%]
tests/unit/test_input_parser.py ..........                      [ 64%]
tests/unit/test_todo_executor.py ............                   [ 91%]
tests/integration/test_todo_workflows.py ....                   [100%]

========================== 45 passed in 0.52s ==========================
```

---

## Architecture Overview

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ text command
       ↓
┌─────────────┐
│     CLI     │ (todo_cli.py)
└──────┬──────┘
       │ raw string
       ↓
┌─────────────┐
│   Parser    │ (input_parser.py) → Command (spec)
└──────┬──────┘
       │ Command object
       ↓
┌─────────────┐
│  Executor   │ (todo_executor.py) → CommandResult (execution)
└──────┬──────┘
       │ read/write
       ↓
┌─────────────┐
│   Storage   │ (task_store.py) → In-memory dict
└─────────────┘
```

**Key Concept**: Commands are **specified** (parsed) before **execution** (action). This separation enables:
- Testing each layer independently
- Clear error boundaries
- Transparent behavior

---

## Next Steps

1. **Explore the code**: Start with `src/task_model.py` to see data structures
2. **Read the plan**: See `plan.md` for detailed architecture
3. **Run tests**: Verify everything works with `pytest`
4. **Extend**: Add new command patterns in `input_parser.py`

---

## Support

- **Spec**: See `spec.md` for requirements and user stories
- **Architecture**: See `plan.md` for component details
- **Data Model**: See `data-model.md` for entity definitions
- **Research**: See `research.md` for technical decisions

---

**Status**: ✅ Ready to use once implemented!
