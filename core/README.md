# Core: Shared Logic and Domain Models

This directory serves as the shared codebase for components and domain models that are reusable across different phases of the project (e.g., Phase 1 console application, Phase 2 full-stack application).

## Purpose

The `core/` directory ensures that fundamental data structures, specifications, and business logic are defined once and consistently used throughout the project, promoting code reusability and maintaining a single source of truth for core concepts.

## Structure

- `models/`: Contains dataclasses and Enums defining core domain entities and specifications, such as `Todo` items (`todo_models.py`) and operation specifications (`spec_models.py`).
- `services/`: Houses core business logic and service interfaces that can be implemented or utilized by various application phases (e.g., `todo_service.py` for managing todo operations).

## Contents

- `core/models/spec_models.py`: Defines the `Operation` Enum and `Specification` dataclass, detailing how user input is structured into an intent.
- `core/models/todo_models.py`: Defines the `TodoStatus` Enum and `Todo` dataclass, representing the core attributes and behavior of a todo item.
- `core/services/todo_service.py`: Provides the core business logic for managing todo items, including adding, listing, and completing them.
