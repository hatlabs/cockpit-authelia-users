"""Tests for update_user command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import update_user
from cockpit_authelia_users.utils.database import UserDatabase
from cockpit_authelia_users.utils.errors import UserNotFoundError, ValidationError
from cockpit_authelia_users.utils.password import verify_password


class TestUpdateUser:
    """Tests for update_user.execute()."""

    def test_update_user_displayname(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update displayname only."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"displayname": "John Updated"})

        assert result["displayname"] == "John Updated"
        # Other fields unchanged
        assert result["email"] == "john@example.com"

    def test_update_user_email(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update email only."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"email": "john.new@example.com"})

        assert result["email"] == "john.new@example.com"

    def test_update_user_groups(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update groups only."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"groups": ["admins", "users"]})

        assert result["groups"] == ["admins", "users"]

    def test_update_user_disabled(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update disabled status."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"disabled": True})

        assert result["disabled"] is True

    def test_update_user_password(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update password (hashed)."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        update_user.execute("john", {"password": "newpassword123"})

        # Verify password was updated and hashed
        user = db.get_user("john")
        assert user is not None
        assert verify_password("newpassword123", user.password)

    def test_update_user_password_not_in_result(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Password not included in result."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"password": "newpassword123"})

        assert "password" not in result

    def test_update_user_empty_password_unchanged(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Empty password string doesn't change existing password."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        original_user = db.get_user("john")
        assert original_user is not None
        original_hash = original_user.password
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        update_user.execute("john", {"password": ""})

        user = db.get_user("john")
        assert user is not None
        assert user.password == original_hash

    def test_update_user_not_found(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises UserNotFoundError for non-existent user."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(UserNotFoundError) as exc_info:
            update_user.execute("nonexistent", {"displayname": "New Name"})

        assert exc_info.value.details is not None
        assert exc_info.value.details["user_id"] == "nonexistent"

    def test_update_user_partial_update(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Only updates provided fields."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        original_user = db.get_user("john")
        assert original_user is not None
        original_email = original_user.email
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {"displayname": "Only Name Changed"})

        assert result["displayname"] == "Only Name Changed"
        assert result["email"] == original_email  # Unchanged

    def test_update_user_invalid_email(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises ValidationError for invalid email."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(ValidationError):
            update_user.execute("john", {"email": "not-an-email"})

    def test_update_user_multiple_fields(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Can update multiple fields at once."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = update_user.execute("john", {
            "displayname": "John Updated",
            "email": "john.new@example.com",
            "groups": ["admins"],
        })

        assert result["displayname"] == "John Updated"
        assert result["email"] == "john.new@example.com"
        assert result["groups"] == ["admins"]
