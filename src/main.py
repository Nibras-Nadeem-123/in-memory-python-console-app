"""Application entry point with CLI argument parsing."""

import argparse
import sys
from typing import Any, Dict

from src import __version__
from src.config import load_config, setup_logging
from src.repl import repl_loop
from src.security import SafeImportFinder, install_import_hook
from src.session_manager import create_session_state


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="python-console",
        description="Interactive Python console with in-memory session state and safe execution",
        epilog="For more information, see README.md"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )

    parser.add_argument(
        "--load-session",
        metavar="FILE",
        help="Load session from JSON file on startup"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Application entry point.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Parse arguments
        parsed_args = parse_arguments(args)

        # Setup logging
        setup_logging(parsed_args.log_level)

        # Load configuration
        config = load_config()

        # Create execution context
        session_state = create_session_state()
        context: Dict[str, Any] = {
            "session_state": session_state,
            "globals": {},
            "locals": {},
            "config": config,
        }

        # Install security import hooks
        finder = SafeImportFinder()
        install_import_hook(finder)

        # Load session if requested
        if parsed_args.load_session:
            print(f"Note: Session loading not yet implemented ({parsed_args.load_session})")
            print()

        # Start REPL loop
        repl_loop(context)

        # REPL loop never returns normally (exits via sys.exit)
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130  # Standard Unix exit code for Ctrl+C

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
