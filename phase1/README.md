# Phase 1: In-Memory Python Console Application

This directory contains the initial in-memory Python console application. It provides a simple command-line interface for managing todo items.

## Features

- Add new todo items with titles.
- List all existing todo items.
- Mark todo items as completed.
- Exit the application.

## Structure

- `app/`: Contains the main application logic, including the entry point (`main.py`), parsing, and execution.
- `app/spec/`: Defines how user input is interpreted into structured specifications.
- `app/todo/`: Contains logic specific to todo item management (e.g., parsing, execution context).
- `app/utils/`: Provides utility functions for console output and other helper tasks.

## How to Run

To run the Phase 1 console application, navigate to the project root and execute:

```bash
# On Linux/macOS
./run.sh

# On Windows
./run.bat
```

This will activate the virtual environment (if not already active) and start the interactive console.
