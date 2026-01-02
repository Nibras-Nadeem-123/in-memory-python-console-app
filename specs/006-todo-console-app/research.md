# Research: Spec-Driven Todo Console Application

**Feature**: 006-todo-console-app
**Date**: 2025-12-31
**Status**: Completed

## Overview

This document captures technical research and decisions for implementing a spec-driven todo console application with natural language command parsing.

---

## Decision 1: Language and Runtime

**Decision**: Python 3.11+ with standard library only

**Rationale**:
- Project already uses Python (existing Phase 1 implementation)
- Standard library includes powerful parsing tools (re, argparse concepts)
- No external dependencies needed for core functionality
- Excellent testing support with pytest
- Fast development iteration

**Alternatives Considered**:
- **Rust**: Too heavyweight for console app, steeper learning curve
- **JavaScript/Node**: Would require switching contexts from existing Python codebase
- **Go**: Good performance but overkill for in-memory operations

**Trade-offs**:
- ✅ Rapid development, rich standard library, excellent testing
- ⚠️ Slightly slower than compiled languages (not a concern for in-memory ops)

---

## Decision 2: Command Parsing Strategy

**Decision**: Pattern-based parsing with regex and keyword matching

**Rationale**:
- Aligns with Phase 1 constitution (no ML/AI APIs)
- Deterministic behavior (same input → same output)
- Transparent and debuggable
- Sufficient for common command patterns

**Parsing Approach**:
1. Normalize input (lowercase, strip whitespace)
2. Detect operation verb (add, list, complete, delete, update, search, exit)
3. Extract parameters using regex patterns
4. Validate extracted components
5. Build structured Command object

**Command Pattern Examples**:
```python
"add task: write documentation" → ADD(title="write documentation", priority=MEDIUM)
"complete task 5" → COMPLETE(task_id=5)
"list pending tasks" → LIST(filter=status:pending)
"search documentation" → SEARCH(query="documentation")
"update task 3 priority to high" → UPDATE(task_id=3, priority=HIGH)
```

**Alternatives Considered**:
- **Full NLP library (spaCy)**: Violates "no external APIs" constraint, overkill
- **GPT/LLM API**: Violates constitution, non-deterministic, requires internet
- **Grammar-based parser (ANTLR)**: Too complex for simple commands

**Trade-offs**:
- ✅ Fast, deterministic, transparent, no dependencies
- ⚠️ Limited to predefined patterns (can't handle completely novel commands)

---

## Decision 3: Architecture Pattern

**Decision**: Layered architecture with clear boundaries

**Layers**:
1. **CLI Layer** (`src/todo_cli.py`): Input/output, REPL loop
2. **Parser Layer** (`src/input_parser.py`): Text → Command transformation
3. **Executor Layer** (`src/todo_executor.py`): Command → Result execution
4. **Storage Layer** (`src/task_store.py`): In-memory task management
5. **Model Layer** (`src/task_model.py`): Data classes (Task, Command, Result)

**Rationale**:
- Mirrors Phase 1 architecture (API → Engine → SpecBuilder → Skills)
- Each layer has single responsibility
- Testable in isolation
- Clear boundaries prevent coupling

**Alternatives Considered**:
- **Monolithic single file**: Fast prototyping but unmaintainable
- **Event-driven**: Overkill for synchronous CLI operations
- **Plugin architecture**: Not needed for fixed set of operations

**Trade-offs**:
- ✅ Maintainable, testable, extensible
- ⚠️ More files to manage (acceptable for 5-6 modules)

---

## Decision 4: Data Structures

**Decision**: In-memory dictionary with integer keys

**Implementation**:
```python
class TaskStore:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
```

**Rationale**:
- O(1) lookup by ID
- Simple iteration for list/search operations
- Easy to test and reason about
- No serialization complexity

**Alternatives Considered**:
- **List with linear search**: O(n) lookup, slower for large task counts
- **SQLite in-memory**: Violates "standard library only" preference, overkill
- **Custom B-tree**: Unnecessary complexity

**Trade-offs**:
- ✅ Fast, simple, meets performance requirements
- ⚠️ Data lost on exit (acceptable per requirements)

---

## Decision 5: Error Handling Strategy

**Decision**: Explicit error types with user-friendly messages

**Error Categories**:
1. **ParseError**: Invalid command format
2. **ValidationError**: Valid format but invalid data (e.g., task ID doesn't exist)
3. **ExecutionError**: Unexpected errors during operation

**Error Response Format**:
```python
CommandResult(
    success=False,
    message="Task #5 not found. Use 'list' to see all tasks.",
    data=None
)
```

**Rationale**:
- Guides users to correct usage
- Distinguishes between user error and system error
- Provides actionable suggestions

**Alternatives Considered**:
- **Generic error messages**: Less helpful for users
- **Exception-based flow**: Breaks execution flow, harder to test
- **Silent failures**: Terrible UX

**Trade-offs**:
- ✅ Clear UX, easy to test, actionable feedback
- ⚠️ Requires maintaining error message catalog

---

## Decision 6: Testing Strategy

**Decision**: Pytest with three test levels

**Test Levels**:
1. **Unit Tests** (`tests/unit/`):
   - Test each module in isolation
   - Mock dependencies
   - Focus on edge cases

2. **Integration Tests** (`tests/integration/`):
   - Test layer interactions (parser → executor → store)
   - Use real dependencies, no mocks
   - Focus on workflows

3. **End-to-End Tests** (`tests/integration/test_todo_workflows.py`):
   - Test complete user scenarios from spec
   - Simulate CLI input/output
   - Verify state changes

**Coverage Target**: ≥ 80%

**Rationale**:
- Aligns with Phase 1 constitution requirements
- Ensures each layer works correctly
- Verifies layer boundaries
- Enables safe refactoring

**Alternatives Considered**:
- **Manual testing only**: Not repeatable, violates constitution
- **Integration tests only**: Misses edge cases in units
- **unittest instead of pytest**: Pytest has better fixture support

**Trade-offs**:
- ✅ Comprehensive coverage, safety for refactoring
- ⚠️ More test code to maintain (acceptable cost)

---

## Decision 7: Command Patterns

**Decision**: Support flexible natural language variations

**Supported Patterns**:

**Add Task**:
- `add task: <title>`
- `add task: <title> with priority <high|medium|low>`
- `create task: <title>`
- `new task: <title>`

**List Tasks**:
- `list tasks` (all tasks)
- `list all tasks`
- `list pending tasks`
- `list completed tasks`
- `show tasks`

**Complete Task**:
- `complete task <id>`
- `mark task <id> as complete`
- `finish task <id>`
- `done <id>`

**Delete Task**:
- `delete task <id>`
- `remove task <id>`

**Update Task**:
- `update task <id> title to <new_title>`
- `update task <id> priority to <high|medium|low>`
- `change task <id> priority to <high|medium|low>`

**Search Tasks**:
- `search <query>`
- `find <query>`

**Exit**:
- `exit`
- `quit`
- `q`

**Rationale**:
- Accommodates common user phrasings
- Reduces friction in command entry
- Balances flexibility with determinism

---

## Technical Decisions Summary

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python 3.11+ | Existing codebase, stdlib sufficiency |
| Parsing | Regex + patterns | Deterministic, transparent, no deps |
| Architecture | Layered (5 layers) | Testability, separation of concerns |
| Storage | Dict[int, Task] | O(1) lookup, simple, fast |
| Error Handling | Explicit types + messages | User guidance, actionable feedback |
| Testing | Pytest (3 levels) | Comprehensive coverage, constitution alignment |
| Command Patterns | Flexible NL variations | UX balance with determinism |

---

## Performance Considerations

**Expected Performance**:
- Parse command: < 1ms (regex matching)
- Execute operation: < 1ms (dict operations)
- List 1000 tasks: < 10ms (iteration + formatting)
- Search 1000 tasks: < 10ms (string matching)

**Total**: All operations complete in < 100ms (well under NFR-001 requirement)

---

## Open Questions

None. All technical decisions resolved.

---

## Next Steps

1. Create data-model.md with Task, Command, CommandResult definitions
2. Design component interfaces in plan.md
3. Generate tasks.md with implementation steps
4. Implement following spec-driven development process
