"""Security sandboxing through custom import hooks."""

import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Optional, Sequence, Set


class SafeImportFinder(MetaPathFinder):
    """Custom import hook to restrict module imports for security.

    Maintains whitelist of safe modules and blacklist of dangerous ones.
    Blocks any import attempts for modules not in the whitelist or
    explicitly in the blacklist.
    """

    # Whitelist of safe standard library modules
    SAFE_MODULES: Set[str] = {
        # Math and numbers
        "math", "cmath", "decimal", "fractions", "random", "statistics",
        # Data structures and algorithms
        "collections", "itertools", "functools", "operator",
        # Text processing
        "string", "re", "difflib", "textwrap",
        # Date and time
        "datetime", "time", "calendar",
        # Data formats
        "json", "csv", "base64", "binascii", "struct",
        # Utilities
        "copy", "pprint", "enum", "dataclasses", "typing",
        # Testing (for unit tests)
        "unittest", "doctest",
    }

    # Explicit blacklist of dangerous modules
    BLOCKED_MODULES: Set[str] = {
        # File system and OS access
        "os", "sys", "pathlib", "shutil", "glob", "fnmatch", "tempfile",
        # Process and system
        "subprocess", "multiprocessing", "threading", "asyncio",
        # Network
        "socket", "ssl", "http", "urllib", "ftplib", "smtplib",
        "poplib", "imaplib", "telnetlib",
        # Code execution
        "code", "codeop", "compile", "eval", "exec",
        # Import system
        "imp", "importlib", "pkgutil", "modulefinder",
        # Other dangerous
        "ctypes", "pickle", "shelve", "dbm",
    }

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]] = None,
        target: Optional[object] = None
    ) -> Optional[ModuleSpec]:
        """Find module spec, blocking dangerous imports.

        Args:
            fullname: Fully qualified module name
            path: Package path
            target: Target module

        Returns:
            None (delegates to default import system for safe modules)

        Raises:
            ImportError: If module is blocked for security reasons
        """
        # Get base module name (before first dot)
        base_module = fullname.split(".")[0]

        # Check if explicitly blocked
        if base_module in self.BLOCKED_MODULES:
            raise ImportError(
                f"Security: Module '{fullname}' is blocked for safety. "
                f"This console restricts access to system, file, and network operations."
            )

        # Check if in whitelist
        if base_module not in self.SAFE_MODULES:
            raise ImportError(
                f"Security: Module '{fullname}' is not in the allowed whitelist. "
                f"Only safe standard library modules are permitted."
            )

        # Module is safe - return None to delegate to default import system
        return None


def install_import_hook(finder: SafeImportFinder) -> None:
    """Install the import hook in sys.meta_path.

    Args:
        finder: SafeImportFinder instance to install

    Note:
        Idempotent - won't duplicate if already installed
    """
    if finder not in sys.meta_path:
        # Insert at beginning to intercept before default import system
        sys.meta_path.insert(0, finder)


def uninstall_import_hook(finder: SafeImportFinder) -> None:
    """Remove the import hook from sys.meta_path.

    Args:
        finder: SafeImportFinder instance to remove

    Note:
        Safe - no error if finder not in sys.meta_path
    """
    if finder in sys.meta_path:
        sys.meta_path.remove(finder)


def is_safe_module(module_name: str) -> bool:
    """Check if a module is in the safe whitelist.

    Args:
        module_name: Module name to check

    Returns:
        True if module is whitelisted, False otherwise
    """
    base_module = module_name.split(".")[0]
    return base_module in SafeImportFinder.SAFE_MODULES
