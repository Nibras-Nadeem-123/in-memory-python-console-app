"""Utility functions for Intelligence Framework."""

from typing import Dict, Any


def format_output(context: Any, event_type: str, details: Dict[str, Any]) -> None:
    """Format and display output from SDD operations.

    Args:
        context: Execution context.
        event_type: Type of event (e.g., "intent_parsed", "spec_generated").
        details: Event details dictionary.
    """
    # Simple console output
    pass  # Events are logged to context already


def log_event(context: Any, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the execution context.

    Args:
        context: Execution context.
        event_type: Type of event (e.g., "sdd_intent_parsed").
        details: Event details dictionary.
    """
    # Add event to context
    if hasattr(context, "add_event"):
        context.add_event(event_type, details)
