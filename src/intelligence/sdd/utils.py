"""Utilities for Spec-Driven Development system."""
import logging
from typing import Any, Dict, Optional
from src.intelligence.context import ExecutionContext


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def log_error(context: ExecutionContext, error: Exception, context: str = "") -> None:
    """Log error with context information."""
    logger.error(
        f"Error in {context or context.execution_id}: {str(error)}",
        exc_info=error,
        extra={'execution_id': getattr(context, 'execution_id', 'unknown')}
    )
    raise error


def log_event(context: ExecutionContext, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the context history."""
    context.add_event(event_type, details)
    logger.info(
        f"[{context.execution_id}] {event_type}",
        extra={'execution_id': context.execution_id}
    )


def format_output(context: ExecutionContext, output: Any, title: str = "Output") -> str:
    """Format output for display."""
    if isinstance(output, (str, int, float, bool, type(None))):
        logger.info(f"[{context.execution_id}] {title}: {output}")
        return f"{title}: {output}"
    elif isinstance(output, dict):
        logger.info(f"[{context.execution_id}] {title}: {len(output)} items")
        return f"{title}: {len(output)} items"
    else:
        logger.info(f"[{context.execution_id}] {title}: {str(type(output))}")
        return f"{title}: {str(type(output))}"
