"""Unit tests for security module."""

import sys

import pytest

from src.security import SafeImportFinder, install_import_hook, is_safe_module, uninstall_import_hook


class TestSafeImportFinder:
    """Tests for SafeImportFinder class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.finder = SafeImportFinder()

    def test_safe_module_math_allowed(self) -> None:
        """Test that math module (whitelisted) is allowed."""
        # Should return None (delegate to default import system)
        result = self.finder.find_spec("math")
        assert result is None

    def test_safe_module_datetime_allowed(self) -> None:
        """Test that datetime module is allowed."""
        result = self.finder.find_spec("datetime")
        assert result is None

    def test_safe_module_json_allowed(self) -> None:
        """Test that json module is allowed."""
        result = self.finder.find_spec("json")
        assert result is None

    def test_blocked_module_os_raises_error(self) -> None:
        """Test that os module (blocked) raises ImportError."""
        with pytest.raises(ImportError, match="Security.*'os'.*blocked"):
            self.finder.find_spec("os")

    def test_blocked_module_sys_raises_error(self) -> None:
        """Test that sys module raises ImportError."""
        with pytest.raises(ImportError, match="Security.*'sys'.*blocked"):
            self.finder.find_spec("sys")

    def test_blocked_module_subprocess_raises_error(self) -> None:
        """Test that subprocess module raises ImportError."""
        with pytest.raises(ImportError, match="Security.*'subprocess'.*blocked"):
            self.finder.find_spec("subprocess")

    def test_blocked_module_socket_raises_error(self) -> None:
        """Test that socket module raises ImportError."""
        with pytest.raises(ImportError, match="Security.*'socket'.*blocked"):
            self.finder.find_spec("socket")

    def test_submodule_of_safe_module_allowed(self) -> None:
        """Test that submodule of safe module is allowed."""
        # collections.abc should be allowed since collections is safe
        result = self.finder.find_spec("collections.abc")
        assert result is None

    def test_submodule_of_blocked_module_raises_error(self) -> None:
        """Test that submodule of blocked module is blocked."""
        with pytest.raises(ImportError, match="Security.*blocked"):
            self.finder.find_spec("os.path")

    def test_unknown_module_not_in_whitelist_raises_error(self) -> None:
        """Test that unknown module not in whitelist raises ImportError."""
        with pytest.raises(ImportError, match="Security.*not in the allowed whitelist"):
            self.finder.find_spec("some_unknown_module")

    def test_safe_modules_set_contains_expected_modules(self) -> None:
        """Test that SAFE_MODULES contains expected standard library modules."""
        expected_safe = {"math", "datetime", "json", "itertools", "collections"}
        assert expected_safe.issubset(SafeImportFinder.SAFE_MODULES)

    def test_blocked_modules_set_contains_dangerous_modules(self) -> None:
        """Test that BLOCKED_MODULES contains dangerous modules."""
        expected_blocked = {"os", "sys", "subprocess", "socket", "pickle"}
        assert expected_blocked.issubset(SafeImportFinder.BLOCKED_MODULES)


class TestInstallImportHook:
    """Tests for install_import_hook function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.finder = SafeImportFinder()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        # Ensure hook is removed after each test
        uninstall_import_hook(self.finder)

    def test_install_adds_finder_to_meta_path(self) -> None:
        """Test that install adds finder to sys.meta_path."""
        install_import_hook(self.finder)
        assert self.finder in sys.meta_path

    def test_install_adds_at_beginning(self) -> None:
        """Test that finder is added at beginning of meta_path."""
        original_length = len(sys.meta_path)
        install_import_hook(self.finder)

        assert sys.meta_path[0] == self.finder
        assert len(sys.meta_path) == original_length + 1

    def test_install_is_idempotent(self) -> None:
        """Test that installing multiple times doesn't duplicate."""
        install_import_hook(self.finder)
        length_after_first = len(sys.meta_path)

        install_import_hook(self.finder)
        length_after_second = len(sys.meta_path)

        assert length_after_first == length_after_second
        assert sys.meta_path.count(self.finder) == 1


class TestUninstallImportHook:
    """Tests for uninstall_import_hook function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.finder = SafeImportFinder()

    def test_uninstall_removes_finder(self) -> None:
        """Test that uninstall removes finder from sys.meta_path."""
        install_import_hook(self.finder)
        assert self.finder in sys.meta_path

        uninstall_import_hook(self.finder)
        assert self.finder not in sys.meta_path

    def test_uninstall_when_not_installed_is_safe(self) -> None:
        """Test that uninstall doesn't raise error if finder not installed."""
        # Should not raise any error
        uninstall_import_hook(self.finder)


class TestIsSafeModule:
    """Tests for is_safe_module function."""

    def test_safe_module_returns_true(self) -> None:
        """Test that safe module returns True."""
        assert is_safe_module("math") is True
        assert is_safe_module("datetime") is True
        assert is_safe_module("json") is True

    def test_blocked_module_returns_false(self) -> None:
        """Test that blocked module returns False (not in whitelist)."""
        assert is_safe_module("os") is False
        assert is_safe_module("sys") is False
        assert is_safe_module("subprocess") is False

    def test_unknown_module_returns_false(self) -> None:
        """Test that unknown module returns False."""
        assert is_safe_module("some_unknown_module") is False

    def test_submodule_checks_base_module(self) -> None:
        """Test that submodule check uses base module name."""
        assert is_safe_module("collections.abc") is True
        assert is_safe_module("os.path") is False


class TestImportHookIntegration:
    """Integration tests for import hook functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.finder = SafeImportFinder()
        install_import_hook(self.finder)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        uninstall_import_hook(self.finder)

    def test_can_import_safe_module_with_hook_installed(self) -> None:
        """Test that safe modules can be imported with hook active."""
        # Should succeed
        import math
        assert math.pi > 3.14

    def test_cannot_import_blocked_module_with_hook_installed(self) -> None:
        """Test that blocked modules cannot be imported with hook active."""
        # Remove from sys.modules if already cached
        import sys
        if 'subprocess' in sys.modules:
            del sys.modules['subprocess']

        with pytest.raises(ImportError, match="Security.*blocked"):
            import subprocess  # type: ignore  # noqa: F401

    def test_cannot_import_unlisted_module_with_hook_installed(self) -> None:
        """Test that unlisted modules cannot be imported with hook active."""
        with pytest.raises(ImportError, match="Security.*not in the allowed whitelist"):
            import some_fake_module  # type: ignore  # noqa: F401
