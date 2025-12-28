"""Tests for list_users command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import list_users
from cockpit_authelia_users.utils.database import UserDatabase


class TestListUsers:
    """Tests for list_users.execute()."""

    def test_list_users_empty_database(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Empty database returns empty list."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(empty_users_yaml))

        result = list_users.execute()

        assert result == []

    def test_list_users_returns_all_users(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Returns all users in database."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_users.execute()

        assert len(result) == 3
        user_ids = [u["user_id"] for u in result]
        assert "admin" in user_ids
        assert "john" in user_ids
        assert "disabled_user" in user_ids

    def test_list_users_excludes_passwords(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Password hashes are never included in output."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_users.execute()

        for user in result:
            assert "password" not in user

    def test_list_users_includes_all_fields(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Each user includes required fields."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_users.execute()

        for user in result:
            assert "user_id" in user
            assert "displayname" in user
            assert "email" in user
            assert "disabled" in user
            assert "groups" in user
