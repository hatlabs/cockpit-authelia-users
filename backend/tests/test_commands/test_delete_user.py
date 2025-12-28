"""Tests for delete_user command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import delete_user
from cockpit_authelia_users.utils.database import UserDatabase
from cockpit_authelia_users.utils.errors import UserNotFoundError


class TestDeleteUser:
    """Tests for delete_user.execute()."""

    def test_delete_user_success(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Successfully deletes an existing user."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = delete_user.execute("john")

        assert result == {"success": True}
        # Verify user is removed from database
        assert db.get_user("john") is None

    def test_delete_user_not_found(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises UserNotFoundError for non-existent user."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(UserNotFoundError) as exc_info:
            delete_user.execute("nonexistent")

        assert exc_info.value.details is not None
        assert exc_info.value.details["user_id"] == "nonexistent"

    def test_delete_user_other_users_remain(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Deleting one user doesn't affect others."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        delete_user.execute("john")

        # Other users still exist
        assert db.get_user("admin") is not None
        assert db.get_user("disabled_user") is not None
