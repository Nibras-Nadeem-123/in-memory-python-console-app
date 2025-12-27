"""Session state management for in-memory variable storage."""

from datetime import datetime
from typing import Any, Dict, List, Tuple

# Type alias for session state structure
# Maps variable name to (value, metadata) tuple
SessionState = Dict[str, Tuple[Any, Dict[str, Any]]]


def create_session_state() -> SessionState:
    """Create an empty session state.

    Returns:
        Empty dictionary for storing variables with metadata
    """
    return {}


def add_variable(state: SessionState, name: str, value: Any) -> None:
    """Add or update a variable in session state with metadata.

    Args:
        state: Session state dictionary
        name: Variable name (must be valid Python identifier)
        value: Variable value (any Python object)

    Raises:
        ValueError: If variable name is invalid or shadows built-ins
    """
    # Validate variable name
    if not name.isidentifier():
        raise ValueError(f"Invalid variable name: '{name}'")

    # Check for shadowing system commands (not built-ins, but our commands)
    reserved_names = {"help", "exit", "quit", "vars", "clear", "save", "load", "history"}
    if name in reserved_names:
        raise ValueError(f"Cannot use reserved name: '{name}'")

    now = datetime.now().isoformat()

    if name in state:
        # Update existing variable - preserve created timestamp
        _, old_metadata = state[name]
        metadata = {
            "type": type(value).__name__,
            "created": old_metadata.get("created", now),
            "modified": now,
        }
    else:
        # Create new variable
        metadata = {
            "type": type(value).__name__,
            "created": now,
            "modified": now,
        }

    state[name] = (value, metadata)


def get_variable(state: SessionState, name: str) -> Tuple[Any, Dict[str, Any]]:
    """Retrieve a variable and its metadata from session state.

    Args:
        state: Session state dictionary
        name: Variable name

    Returns:
        Tuple of (value, metadata)

    Raises:
        KeyError: If variable does not exist
    """
    if name not in state:
        raise KeyError(f"Variable '{name}' not found in session")

    return state[name]


def delete_variable(state: SessionState, name: str) -> None:
    """Delete a variable from session state.

    Args:
        state: Session state dictionary
        name: Variable name to delete

    Raises:
        KeyError: If variable does not exist
    """
    if name not in state:
        raise KeyError(f"Variable '{name}' not found in session")

    del state[name]


def list_variables(
    state: SessionState,
    type_filter: str | None = None
) -> List[Tuple[str, Any, Dict[str, Any]]]:
    """List all variables in session state with optional type filtering.

    Args:
        state: Session state dictionary
        type_filter: Optional type name to filter by (e.g., "int", "str")

    Returns:
        List of (name, value, metadata) tuples, sorted by name
    """
    variables = []

    for name, (value, metadata) in state.items():
        if type_filter is None or metadata["type"] == type_filter:
            variables.append((name, value, metadata))

    # Sort by variable name
    return sorted(variables, key=lambda x: x[0])


def clear_session(state: SessionState) -> int:
    """Clear all variables from session state.

    Args:
        state: Session state dictionary

    Returns:
        Number of variables that were cleared
    """
    count = len(state)
    state.clear()
    return count
