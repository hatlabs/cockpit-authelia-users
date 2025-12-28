"""Tests for database operations module."""

from pathlib import Path

import pytest
import yaml

from cockpit_authelia_users.utils.database import User, UserDatabase
from cockpit_authelia_users.utils.errors import DatabaseError


class TestUser:
    """Tests for User dataclass."""

    def test_create_user(self):
        """User can be created with all fields."""
        user = User(
            user_id="john",
            displayname="John Doe",
            password="$argon2id$hash",
            email="john@example.com",
            disabled=False,
            groups=["users"],
        )
        assert user.user_id == "john"
        assert user.displayname == "John Doe"
        assert user.email == "john@example.com"
        assert user.disabled is False
        assert user.groups == ["users"]

    def test_create_user_defaults(self):
        """User has sensible defaults."""
        user = User(
            user_id="john",
            displayname="John Doe",
            password="$argon2id$hash",
            email="john@example.com",
        )
        assert user.disabled is False
        assert user.groups == []

    def test_to_dict_excludes_password(self):
        """to_dict() excludes password by default."""
        user = User(
            user_id="john",
            displayname="John Doe",
            password="$argon2id$hash",
            email="john@example.com",
            groups=["users"],
        )
        result = user.to_dict()
        assert "password" not in result
        assert result == {
            "user_id": "john",
            "displayname": "John Doe",
            "email": "john@example.com",
            "disabled": False,
            "groups": ["users"],
        }

    def test_to_dict_includes_password_when_requested(self):
        """to_dict() can include password."""
        user = User(
            user_id="john",
            displayname="John Doe",
            password="$argon2id$hash",
            email="john@example.com",
        )
        result = user.to_dict(include_password=True)
        assert result["password"] == "$argon2id$hash"

    def test_preserves_extra_fields(self):
        """Extra fields are preserved."""
        user = User(
            user_id="john",
            displayname="John Doe",
            password="$argon2id$hash",
            email="john@example.com",
            extra_fields={"totp": {"algorithm": "SHA256"}},
        )
        assert user.extra_fields == {"totp": {"algorithm": "SHA256"}}


class TestUserDatabase:
    """Tests for UserDatabase class."""

    def test_load_existing_database(self, sample_users_yaml: Path):
        """Can load existing database."""
        db = UserDatabase.load(sample_users_yaml)
        assert len(db.users) == 3
        assert "admin" in db.users
        assert "john" in db.users
        assert "disabled_user" in db.users

    def test_load_empty_database(self, empty_users_yaml: Path):
        """Can load empty database."""
        db = UserDatabase.load(empty_users_yaml)
        assert len(db.users) == 0

    def test_load_missing_file(self, temp_dir: Path):
        """Missing file returns empty database."""
        db = UserDatabase.load(temp_dir / "nonexistent.yml")
        assert len(db.users) == 0

    def test_load_malformed_yaml(self, temp_dir: Path):
        """Malformed YAML raises DatabaseError."""
        bad_file = temp_dir / "bad.yml"
        bad_file.write_text("not: valid: yaml: {{{{")

        with pytest.raises(DatabaseError):
            UserDatabase.load(bad_file)

    def test_get_user(self, sample_users_yaml: Path):
        """Can get a specific user."""
        db = UserDatabase.load(sample_users_yaml)
        user = db.get_user("admin")

        assert user is not None
        assert user.user_id == "admin"
        assert user.displayname == "Admin User"
        assert user.email == "admin@example.com"
        assert user.disabled is False
        assert "admins" in user.groups

    def test_get_user_not_found(self, sample_users_yaml: Path):
        """Getting non-existent user returns None."""
        db = UserDatabase.load(sample_users_yaml)
        user = db.get_user("nonexistent")
        assert user is None

    def test_list_users(self, sample_users_yaml: Path):
        """Can list all users."""
        db = UserDatabase.load(sample_users_yaml)
        users = db.list_users()

        assert len(users) == 3
        user_ids = [u.user_id for u in users]
        assert "admin" in user_ids
        assert "john" in user_ids
        assert "disabled_user" in user_ids

    def test_add_user(self, empty_users_yaml: Path):
        """Can add a new user."""
        db = UserDatabase.load(empty_users_yaml)

        user = User(
            user_id="newuser",
            displayname="New User",
            password="$argon2id$hash",
            email="new@example.com",
            groups=["users"],
        )
        db.add_user(user)
        db.save(empty_users_yaml)

        # Reload and verify
        db2 = UserDatabase.load(empty_users_yaml)
        assert len(db2.users) == 1
        assert db2.get_user("newuser") is not None

    def test_update_user(self, sample_users_yaml: Path):
        """Can update an existing user."""
        db = UserDatabase.load(sample_users_yaml)

        user = db.get_user("john")
        assert user is not None
        user.displayname = "John Updated"
        user.groups = ["admins", "users"]

        db.update_user(user)
        db.save(sample_users_yaml)

        # Reload and verify
        db2 = UserDatabase.load(sample_users_yaml)
        updated = db2.get_user("john")
        assert updated is not None
        assert updated.displayname == "John Updated"
        assert "admins" in updated.groups

    def test_delete_user(self, sample_users_yaml: Path):
        """Can delete a user."""
        db = UserDatabase.load(sample_users_yaml)
        assert len(db.users) == 3

        db.delete_user("john")
        db.save(sample_users_yaml)

        # Reload and verify
        db2 = UserDatabase.load(sample_users_yaml)
        assert len(db2.users) == 2
        assert db2.get_user("john") is None

    def test_list_groups(self, sample_users_yaml: Path):
        """Can list all unique groups."""
        db = UserDatabase.load(sample_users_yaml)
        groups = db.list_groups()

        # Should include all groups from users plus defaults
        assert "admins" in groups
        assert "users" in groups
        assert "guests" in groups

    def test_list_groups_includes_defaults(self, empty_users_yaml: Path):
        """Group list includes default groups even with no users."""
        db = UserDatabase.load(empty_users_yaml)
        groups = db.list_groups()

        assert "admins" in groups
        assert "users" in groups
        assert "guests" in groups

    def test_save_atomic(self, sample_users_yaml: Path):
        """Save is atomic (temp file + rename)."""
        db = UserDatabase.load(sample_users_yaml)
        db.add_user(
            User(
                user_id="temp",
                displayname="Temp",
                password="hash",
                email="temp@example.com",
            )
        )

        # Save should work
        db.save(sample_users_yaml)

        # File should still be valid
        db2 = UserDatabase.load(sample_users_yaml)
        assert db2.get_user("temp") is not None

    def test_preserves_extra_fields(self, temp_dir: Path):
        """Extra fields in user records are preserved."""
        # Create a user database with extra fields
        db_path = temp_dir / "users.yml"
        data = {
            "users": {
                "john": {
                    "displayname": "John Doe",
                    "password": "$argon2id$hash",
                    "email": "john@example.com",
                    "totp": {"algorithm": "SHA256"},  # Extra field
                }
            }
        }
        with open(db_path, "w") as f:
            yaml.dump(data, f)

        # Load, modify, save
        db = UserDatabase.load(db_path)
        user = db.get_user("john")
        assert user is not None
        user.displayname = "John Updated"
        db.update_user(user)
        db.save(db_path)

        # Verify extra field is preserved
        with open(db_path) as f:
            saved = yaml.safe_load(f)
        assert saved["users"]["john"]["totp"] == {"algorithm": "SHA256"}
        assert saved["users"]["john"]["displayname"] == "John Updated"
