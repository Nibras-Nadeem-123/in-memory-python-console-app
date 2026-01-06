# Spec-Driven Todo Console Application

This is a console-based todo manager that accepts natural language commands. All data is stored in memory and is reset when the application exits.

This project is an implementation of a spec-driven development process. The application parses natural language commands into structured specifications before executing operations.

## Features

- **Natural Language Commands**: Add, list, complete, delete, update, and search for tasks using intuitive text commands.
- **In-Memory Storage**: All tasks are stored in memory for the duration of the session.
- **Spec-Driven Architecture**: Demonstrates a clear separation between parsing user intent and executing actions.
- **TDD**: Developed using a test-driven approach.

## Requirements

- Python 3.11 or higher

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd in-memory-python-console-app
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install development dependencies**:
    The application itself has no external dependencies, but `pytest` is required for running tests.
    ```bash
    pip install -e .[dev]
    ```

## How to Run

To start the interactive console, run the following command from the root of the project:

```bash
python -m src.todo_cli
```

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

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User (Terminal)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ text commands (stdin)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (REPL)                        │
│  • Read input                                               │
│  • Display results                                          │
│  • Handle exit                                              │
└────────────────────────┬────────────────────────────────────┘
                         │ raw string
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Parser Layer (Intent)                     │
│  • Normalize input                                          │
│  • Extract operation type                                   │
│  • Extract parameters                                       │
│  • Build Command object                                     │
└────────────────────────┬────────────────────────────────────┘
                         │ Command (structured)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  Executor Layer (Action)                    │
│  • Validate command                                         │
│  • Route to operation handler                               │
│  • Interact with storage                                    │
│  • Build CommandResult                                      │
└────────────────────────┬────────────────────────────────────┘
                         │ read/write operations
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer (State)                     │
│  • Maintain task dictionary                                 │
│  • Assign IDs                                               │
│  • CRUD operations                                          │
│  • Filter/search                                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Concept**: Commands are **specified** (parsed) before **execution** (action). This separation enables:
- Testing each layer independently
- Clear error boundaries
- Transparent behavior