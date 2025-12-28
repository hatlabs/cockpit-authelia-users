"""Tests for create_user command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import create_user
from cockpit_authelia_users.utils.database import UserDatabase
from cockpit_authelia_users.utils.errors import UserExistsError, ValidationError
from cockpit_authelia_users.utils.password import verify_password


class TestCreateUser:
    """Tests for create_user.execute()."""

    def test_create_user_success(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Successfully creates a new user."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = create_user.execute({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
            "groups": ["users"],
        })

        assert result["user_id"] == "newuser"
        assert result["displayname"] == "New User"
        assert result["email"] == "new@example.com"
        assert result["groups"] == ["users"]
        assert result["disabled"] is False

    def test_create_user_excludes_password_from_result(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Password hash not included in result."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = create_user.execute({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
        })

        assert "password" not in result

    def test_create_user_hashes_password(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Password is hashed before storage."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        create_user.execute({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
        })

        # Check the password is hashed and verifiable
        user = db.get_user("newuser")
        assert user is not None
        assert user.password.startswith("$argon2id$")
        assert verify_password("secret123", user.password)

    def test_create_user_duplicate_id(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises UserExistsError for duplicate user ID."""
        _original_load = UserDatabase.load
        db = _original_load(sample_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(UserExistsError) as exc_info:
            create_user.execute({
                "user_id": "admin",  # Already exists
                "displayname": "New Admin",
                "email": "newadmin@example.com",
                "password": "secret123",
            })

        assert exc_info.value.details is not None
        assert exc_info.value.details["user_id"] == "admin"

    def test_create_user_missing_required_fields(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises ValidationError for missing required fields."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(ValidationError):
            create_user.execute({
                "user_id": "newuser",
                # Missing displayname, email, password
            })

    def test_create_user_invalid_email(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Raises ValidationError for invalid email."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)

        with pytest.raises(ValidationError):
            create_user.execute({
                "user_id": "newuser",
                "displayname": "New User",
                "email": "not-an-email",
                "password": "secret123",
            })

    def test_create_user_defaults_disabled_to_false(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Disabled defaults to False if not provided."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = create_user.execute({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
        })

        assert result["disabled"] is False

    def test_create_user_defaults_groups_to_empty(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Groups defaults to empty list if not provided."""
        _original_load = UserDatabase.load
        db = _original_load(empty_users_yaml)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)

        result = create_user.execute({
            "user_id": "newuser",
            "displayname": "New User",
            "email": "new@example.com",
            "password": "secret123",
        })

        assert result["groups"] == []
