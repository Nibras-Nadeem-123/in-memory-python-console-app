<!--
Sync Impact Report:
- Version change: none → 1.0.0
- Initial constitution creation for in-memory Python console app
- Principles defined: 7 core principles covering memory management, simplicity, security, modularity, testing, user safety, and observability
- Added sections: Runtime Constraints, Development Workflow, Governance
- Templates requiring updates:
  ✅ Constitution created (this file)
  ⚠ Review plan-template.md for constitution alignment (pending)
  ⚠ Review spec-template.md for constitution alignment (pending)
  ⚠ Review tasks-template.md for constitution alignment (pending)
- Follow-up TODOs: None (all placeholders filled)
-->

# In-Memory Python Console App Constitution

## Core Principles

### I. Memory-First Architecture

The application MUST operate entirely in memory during runtime. All data structures, state, and computation MUST use in-memory storage (dictionaries, lists, objects) unless optional persistence is explicitly requested by the user.

**Rationale**: In-memory operation ensures maximum performance, simplicity, and portability. The console app must be lightweight and fast, with no mandatory external dependencies for storage.

**Non-negotiable rules**:
- No persistent database connections required for core functionality
- Session state preserved in memory structures (e.g., Python dicts, dataclasses)
- Optional persistence (file export, JSON dumps) MUST be clearly separated from core logic
- Memory cleanup and garbage collection considerations documented for long-running sessions

### II. Simplicity and Clarity

Code MUST be simple, readable, and self-documenting. Functions MUST be small, focused, and have clear single responsibilities. Complex operations MUST be decomposed into well-named functions.

**Rationale**: Console applications benefit from maintainability and rapid iteration. Clear code reduces cognitive load and enables confident modifications.

**Non-negotiable rules**:
- Functions limited to 50 lines of code (excluding docstrings)
- Descriptive names for functions, variables, and classes (no single-letter names except loop iterators)
- Type hints required for all function signatures (Python 3.9+ syntax)
- Docstrings required for all public functions and classes (Google or NumPy style)

### III. Security and Safe Evaluation

User input MUST be validated and sanitized. Code evaluation (e.g., `eval()`, `exec()`) MUST be sandboxed or avoided entirely. Untrusted input MUST NOT be executed directly.

**Rationale**: Console applications often accept arbitrary user commands. Unsafe evaluation creates security vulnerabilities (code injection, system compromise). Safe alternatives MUST be prioritized.

**Non-negotiable rules**:
- NO use of `eval()` or `exec()` on raw user input without sandboxing
- Command parsing via explicit command registry or pattern matching
- Input validation with whitelists/allowed patterns before processing
- Error messages MUST NOT leak sensitive information (file paths, system details)
- Secrets (API keys, tokens) MUST be loaded from environment variables or `.env` files, NEVER hardcoded

### IV. Modular Design

Application logic MUST be organized into independent, testable modules. Core functionality (parsing, execution, state management) MUST be separated from UI/display concerns.

**Rationale**: Modularity enables unit testing, reusability, and independent evolution of components. Console apps often grow from simple prototypes to complex systems.

**Non-negotiable rules**:
- Separation of concerns: command parsing, execution logic, state management, display output as distinct modules
- Each module MUST have a clear interface (public functions/classes with contracts)
- Circular dependencies prohibited
- Business logic MUST NOT depend on display/formatting code

### V. Test-Driven Development (TDD)

Tests MUST be written before implementation for all non-trivial functionality. The Red-Green-Refactor cycle MUST be followed.

**Rationale**: TDD ensures correctness, provides living documentation, and reduces regressions. Console apps with complex command logic require robust testing.

**Non-negotiable rules**:
- Tests written → User approved → Tests fail → Implementation → Tests pass
- Minimum 80% code coverage for core modules (parsing, execution, state)
- Unit tests for pure functions (stateless logic)
- Integration tests for command workflows (input → processing → output)
- Edge cases and error paths MUST have explicit tests

### VI. User Experience and Error Handling

The console interface MUST provide clear, helpful feedback. Errors MUST be human-readable with actionable guidance. Commands MUST support help/documentation.

**Rationale**: Console apps live or die by usability. Cryptic errors frustrate users and create support burden.

**Non-negotiable rules**:
- All commands MUST have `--help` or equivalent documentation
- Error messages MUST state what went wrong and suggest fixes (e.g., "Unknown command 'foo'. Did you mean 'bar'? Type 'help' for available commands.")
- Command output MUST be clean and readable (structured tables, JSON formatting where appropriate)
- Confirmation prompts for destructive operations (clear state, exit with unsaved changes)

### VII. Observability and Debugging

Application state MUST be inspectable. Logging MUST be structured and configurable. Debug mode MUST provide visibility into execution flow.

**Rationale**: In-memory apps can be opaque without proper instrumentation. Observability enables rapid debugging and user support.

**Non-negotiable rules**:
- Structured logging with configurable levels (DEBUG, INFO, WARNING, ERROR)
- State inspection command (e.g., `show state`, `inspect`) for debugging
- Execution traces available in debug mode (command history, state changes)
- Performance metrics for long-running operations (execution time, memory usage)

## Runtime Constraints

### Python Version and Dependencies

- **Target Python Version**: Python 3.9+ (for modern type hints and standard library features)
- **Dependency Policy**: Minimize external dependencies. Standard library preferred. Third-party libraries MUST be justified (e.g., `prompt_toolkit` for rich CLI UX, `click` for command parsing).
- **Virtual Environment**: MUST use `venv` or equivalent for dependency isolation
- **Dependency Documentation**: `requirements.txt` or `pyproject.toml` MUST list all dependencies with version pins

### Performance Standards

- **Startup Time**: Application MUST start in under 1 second for typical use cases
- **Command Response Time**: Interactive commands MUST respond in under 100ms for simple operations
- **Memory Footprint**: Base memory usage MUST stay under 50MB for idle state
- **Session Limits**: Application MUST handle sessions with up to 10,000 in-memory objects without degradation

### Optional Persistence

- **Format**: JSON or Pickle for session state export/import (user choice)
- **Location**: User-specified file paths or default `~/.app-name/sessions/`
- **Atomicity**: File writes MUST be atomic (write to temp, rename on success)
- **Backward Compatibility**: Exported formats MUST be versioned; breaking changes MUST be migrated

## Development Workflow

### Code Review and Quality Gates

- All changes MUST pass linting (`ruff`, `pylint`, or `flake8`) and type checking (`mypy`)
- All tests MUST pass before merge
- Code review required for changes to core modules (state management, command execution)
- Security-sensitive code (input validation, persistence) MUST have dedicated review focus

### Version Control

- Feature branches for all non-trivial changes (naming: `###-feature-name`)
- Commit messages MUST be descriptive (conventional commits style preferred: `feat:`, `fix:`, `docs:`, `refactor:`)
- Pull requests MUST reference related specs/tasks from `specs/` directory

### Testing Strategy

- Unit tests in `tests/unit/` for pure functions and isolated modules
- Integration tests in `tests/integration/` for command workflows
- Run tests with `pytest` (or equivalent) before commits
- Continuous integration (CI) MUST run full test suite on all branches

## Governance

### Amendment Process

This constitution supersedes all other development practices. Amendments require:

1. Documented justification (why the change, what problem it solves)
2. Review by project stakeholders
3. Migration plan for existing code if principles change
4. Version bump according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes (removing/redefining core rules)
   - **MINOR**: New principles added or material expansions to existing guidance
   - **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance

- All pull requests and code reviews MUST verify compliance with these principles
- Violations MUST be justified in writing and approved (documented in `Complexity Tracking` section of plan.md)
- Complexity MUST be justified: if a simpler approach exists, it MUST be used

### AI Agent's Role

The AI agent assisting with development MUST:

- Prioritize these principles in all code generation and suggestions
- Flag potential violations and suggest compliant alternatives
- Generate tests before implementations (TDD enforcement)
- Validate security considerations (input handling, evaluation safety)
- Create Prompt History Records (PHRs) for development sessions
- Suggest Architectural Decision Records (ADRs) for significant design choices
- Use MCP tools and CLI commands for verification (not internal knowledge)
- Ask clarifying questions when requirements are ambiguous (Human as Tool strategy)

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
