"""Tests for get_user command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import get_user
from cockpit_authelia_users.utils.database import UserDatabase
from cockpit_authelia_users.utils.errors import UserNotFoundError


class TestGetUser:
    """Tests for get_user.execute()."""

    def test_get_user_existing(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can retrieve an existing user."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = get_user.execute("admin")

        assert result["user_id"] == "admin"
        assert result["displayname"] == "Admin User"
        assert result["email"] == "admin@example.com"
        assert result["disabled"] is False
        assert "admins" in result["groups"]

    def test_get_user_not_found(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises UserNotFoundError for non-existent user."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        with pytest.raises(UserNotFoundError) as exc_info:
            get_user.execute("nonexistent")

        assert exc_info.value.details is not None
        assert exc_info.value.details["user_id"] == "nonexistent"

    def test_get_user_excludes_password(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Password hash is not included in result."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = get_user.execute("admin")

        assert "password" not in result

    def test_get_user_disabled_user(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can retrieve disabled users."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = get_user.execute("disabled_user")

        assert result["user_id"] == "disabled_user"
        assert result["disabled"] is True
