# In-Memory Python Console App

An interactive Python console application that executes Python code in memory with safe sandboxing, session state management, and optional persistence.

## Features

- 🚀 **Interactive Python Execution**: Execute expressions, statements, and multi-line code (functions, classes, loops)
- 🔒 **Security Sandboxing**: Custom import hooks block dangerous modules (os, sys, subprocess, socket)
- 💾 **In-Memory Session State**: All variables stored in memory with metadata (type, timestamps)
- 📊 **State Inspection**: View all session variables with formatted table output
- 💿 **Optional Persistence**: Save/load sessions to JSON files
- 🛡️ **Error Handling**: Structured error messages with actionable suggestions (never crashes)
- 📝 **Command History**: Track and recall previously executed commands
- 🐛 **Debug Mode**: Execution traces and detailed logging

## Requirements

- Python 3.9 or higher
- No external dependencies (uses Python standard library only)
- Optional: `prompt-toolkit` and `rich` for enhanced UX

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd in-memory-python-console-app
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Install UX enhancements**:
   ```bash
   pip install -r requirements-optional.txt
   ```

## Usage

### Starting the Console

```bash
python -m src.main
```

Or with options:
```bash
python -m src.main --log-level DEBUG
python -m src.main --load-session my_session.json
```

### Basic Usage Examples

**Execute Python expressions**:
```python
>>> 2 + 2
4

>>> "Hello, " + "World!"
'Hello, World!'
```

**Define variables**:
```python
>>> x = 10
>>> y = 20
>>> z = x + y
>>> z
30
```

**Multi-line code** (auto-detected):
```python
>>> def greet(name):
...     return f"Hello, {name}!"
...
>>> greet("Alice")
'Hello, Alice!'
```

### System Commands

- `help` - Show available commands
- `vars` - List all variables in session
- `save <filename>` - Save session to JSON file
- `load <filename>` - Load session from JSON file
- `clear` - Clear all variables (with confirmation)
- `exit` or `quit` - Exit console

### Security

**Safe modules** (whitelisted):
- math, datetime, json, itertools, collections, re, random, string, decimal, fractions

**Blocked modules** (for security):
- os, sys, subprocess, socket, shutil, pathlib (file system access)
- Network and process manipulation modules

Attempting to import blocked modules displays a security warning and prevents execution.

### Error Handling

All errors display structured messages:

```python
>>> import os
Error Type: ImportError (Security Block)
Description: Module 'os' is blocked for security reasons.
Suggestion: This console blocks system access modules. Use safe alternatives.

>>> 1 / 0
Error Type: ZeroDivisionError
Description: Division by zero is not allowed.
Suggestion: Check your divisor value before performing division.
```

The console **never crashes** - it catches all exceptions and continues running.

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_parser.py

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Format code
ruff format src/ tests/
```

### Project Structure

```
src/
├── __init__.py
├── main.py                 # Entry point, CLI argument parsing
├── repl.py                 # Main REPL loop
├── executor.py             # Code execution engine
├── session_manager.py      # Session state management
├── security.py             # Import hook sandboxing
├── persistence.py          # JSON save/load
├── formatter.py            # Output and error formatting
├── parser.py               # AST-based syntax detection
└── config.py               # Configuration and logging

tests/
├── unit/                   # Unit tests for individual modules
├── integration/            # Integration tests for workflows
└── fixtures/               # Test data and sample sessions
```

## Architecture

### Spec-Driven Development (SDD) System

The project includes a reusable intelligence framework with a Spec-Driven Development (SDD) system for transforming natural language intent into structured implementation artifacts.

#### SDD Pipeline Stages

1. **Intent Parsing**: Classifies user intent (CLARIFY, SPECIFY, PLAN, GUIDE) and extracts metadata
2. **Specification Generation**: Creates formal spec.md documents from intent using template-based generation
3. **Planning**: Breaks requirements into actionable tasks with dependencies and effort estimates
4. **Execution Guidance**: Provides code scaffolding, best practices, and implementation order

#### SDD CLI Commands

```bash
# Parse natural language into intent
python -m src.intelligence.main --sdd parse "I want to create a user authentication system"

# Generate specification
python -m src.intelligence.main --sdd spec "create a user authentication system with login and registration"

# Generate implementation plan
python -m src.intelligence.main --sdd plan spec.md

# Generate execution guide
python -m src.intelligence.main --sdd guide plan.md

# Execute full pipeline
python -m src.intelligence.main --sdd pipeline "create a REST API for todo management"

# List registered agents and skills
python -m src.intelligence.main --sdd list --verbose
```

#### SDD Components

- **Agents**: IntentAgent, SpecAgent, PlanAgent, GuideAgent
- **Skills**: IntentParsingSkill, AmbiguityDetectionSkill, RequirementExtractionSkill, TaskBreakdownSkill, DependencyResolutionSkill, CodeScaffoldingSkill, BestPracticesSkill
- **Engine**: SDDEngine with WorkflowManager for multi-stage orchestration
- **Data Models**: Intent, Spec, Plan, Task, Artifact, Decision, IntentType
- **Context**: SDDContext with artifact management and history tracking

### Core Principles (from Constitution)

1. **Reusable Intelligence Framework**: The primary goal is to build a framework for reusable intelligence, not a single-purpose application. All components, from skills to agents, MUST be designed for broad applicability and reusability over one-off logic.
2. **Intelligence-First Design**: Prioritize reasoning, planning, and adaptability over raw execution. The system MUST understand "why" a task is being performed before executing "how," clearly separating the planning/reasoning layer from the execution layer.
3. **Domain-Agnostic & Modular Architecture**: The framework's core design and concepts MUST be language-agnostic and contain no hardcoded, domain-specific logic. The architecture MUST be composed of clear, modular, and composable components (e.g., skills, agents, tools) with well-defined interfaces.
4. **Skill-Based Functionality**: All functional capabilities MUST be developed as discrete, independently testable "skills." Skills are the fundamental, reusable building blocks of all system functionality, not monolithic features.
5. **Safety and Introspectability**: The framework MUST enforce safe execution environments and provide deep introspectability. The system's state, reasoning process, and execution history must be transparent, auditable, and easy to debug.
6. **Frozen Intelligence Architecture**: The core intelligence layer (Context, Skills, Runtime, Engine) is considered stable and frozen. Future projects MAY extend its functionality through new skills or agents, but MUST NOT modify its core logic. Changes to this layer require explicit versioning and a formal architectural review process.

### Session State Structure

```python
{
    "x": (10, {
        "type": "int",
        "created": "2025-12-27T10:00:00",
        "modified": "2025-12-27T10:05:00"
    }),
    "name": ("Alice", {
        "type": "str",
        "created": "2025-12-27T10:01:00",
        "modified": "2025-12-27T10:01:00"
    })
}
```

## Performance

- **Startup Time**: <1 second
- **Command Response**: <100ms for simple operations
- **Memory Footprint**: <50MB idle, <200MB for large sessions (1000+ variables)
- **Session Limits**: Handles up to 10,000 in-memory objects

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see LICENSE file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

For issues, questions, or feature requests:
- Review [quickstart.md](../specs/001-python-console-app/quickstart.md) for detailed usage guide
- Check [plan.md](../specs/001-python-console-app/plan.md) for architecture details
- Report bugs via GitHub Issues
