"""Tests for CLI entry point."""

import argparse
import io
import json
import sys
from pathlib import Path

import pytest

from cockpit_authelia_users import cli
from cockpit_authelia_users.utils.database import UserDatabase


class TestDispatchCommand:
    """Tests for dispatch_command()."""

    def test_dispatch_list_users(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """list-users command dispatches correctly."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        args = argparse.Namespace(command="list-users")
        result = cli.dispatch_command(args)

        assert isinstance(result, list)
        assert len(result) == 3

    def test_dispatch_get_user(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """get-user command dispatches correctly."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        args = argparse.Namespace(command="get-user", user_id="admin")
        result = cli.dispatch_command(args)

        assert isinstance(result, dict)
        assert result["user_id"] == "admin"

    def test_dispatch_create_user(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """create-user command dispatches correctly."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        user_data = json.dumps({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
        })
        monkeypatch.setattr(sys, "stdin", io.StringIO(user_data))

        args = argparse.Namespace(command="create-user")
        result = cli.dispatch_command(args)

        assert isinstance(result, dict)
        assert result["user_id"] == "newuser"

    def test_dispatch_update_user(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """update-user command dispatches correctly."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        user_data = json.dumps({"displayname": "Updated Name"})
        monkeypatch.setattr(sys, "stdin", io.StringIO(user_data))

        args = argparse.Namespace(command="update-user", user_id="john")
        result = cli.dispatch_command(args)

        assert isinstance(result, dict)
        assert result["displayname"] == "Updated Name"

    def test_dispatch_delete_user(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """delete-user command dispatches correctly."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        args = argparse.Namespace(command="delete-user", user_id="john")
        result = cli.dispatch_command(args)

        assert result == {"success": True}

    def test_dispatch_list_groups(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """list-groups command dispatches correctly."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        args = argparse.Namespace(command="list-groups")
        result = cli.dispatch_command(args)

        assert isinstance(result, list)
        assert "admins" in result

    def test_dispatch_unknown_command(self):
        """Unknown command raises ValueError."""
        args = argparse.Namespace(command="unknown-command")

        with pytest.raises(ValueError, match="Unknown command"):
            cli.dispatch_command(args)


class TestMainFunction:
    """Tests for main() entry point."""

    def test_main_success_json_output(
        self,
        sample_users_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Successful command outputs JSON to stdout."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))
        monkeypatch.setattr(sys, "argv", ["cli", "list-groups"])

        cli.main()

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "admins" in result
        assert captured.err == ""

    def test_main_error_json_output(
        self,
        sample_users_yaml: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Error outputs JSON to stderr with exit code 1."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))
        monkeypatch.setattr(sys, "argv", ["cli", "get-user", "nonexistent"])

        with pytest.raises(SystemExit) as exc_info:
            cli.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert error["code"] == "USER_NOT_FOUND"
        assert "nonexistent" in error["message"]

    def test_main_internal_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Internal error outputs JSON to stderr with exit code 1."""
        # Simulate an internal error by making dispatch_command raise a generic exception
        def raise_error(args: argparse.Namespace):
            raise RuntimeError("Internal failure")

        monkeypatch.setattr(cli, "dispatch_command", raise_error)
        monkeypatch.setattr(sys, "argv", ["cli", "list-users"])

        with pytest.raises(SystemExit) as exc_info:
            cli.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        error = json.loads(captured.err)
        assert error["code"] == "INTERNAL_ERROR"
        assert "Internal failure" in error["message"]

    def test_main_help_available(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ):
        """Help text is available."""
        monkeypatch.setattr(sys, "argv", ["cli", "--help"])

        with pytest.raises(SystemExit) as exc_info:
            cli.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "list-users" in captured.out
        assert "get-user" in captured.out
        assert "create-user" in captured.out
        assert "update-user" in captured.out
        assert "delete-user" in captured.out
        assert "list-groups" in captured.out
