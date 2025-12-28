"""Pytest configuration and fixtures."""

import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from cockpit_authelia_users.utils.database import UserDatabase


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_database(monkeypatch: pytest.MonkeyPatch) -> Callable[[Path, bool], UserDatabase]:
    """Factory fixture to mock UserDatabase.load() with a specific YAML file.

    Usage:
        def test_example(mock_database, sample_users_yaml):
            db = mock_database(sample_users_yaml)
            # Now UserDatabase.load() returns the mocked database
            # db.save() is a no-op by default

        def test_with_save(mock_database, sample_users_yaml):
            db = mock_database(sample_users_yaml, mock_save=False)
            # Now db.save() actually saves to the file
    """
    _original_load = UserDatabase.load

    def factory(yaml_path: Path, mock_save: bool = True) -> UserDatabase:
        db = _original_load(yaml_path)
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: db)
        if mock_save:
            monkeypatch.setattr(UserDatabase, "save", lambda self, path=None: None)
        return db

    return factory


@pytest.fixture
def sample_users_yaml(temp_dir: Path) -> Path:
    """Create a sample users_database.yml file."""
    users_data = {
        "users": {
            "admin": {
                "displayname": "Admin User",
                "password": "$argon2id$v=19$m=65536,t=3,p=4$abc123$hash123",
                "email": "admin@example.com",
                "disabled": False,
                "groups": ["admins", "users"],
            },
            "john": {
                "displayname": "John Doe",
                "password": "$argon2id$v=19$m=65536,t=3,p=4$def456$hash456",
                "email": "john@example.com",
                "disabled": False,
                "groups": ["users"],
            },
            "disabled_user": {
                "displayname": "Disabled User",
                "password": "$argon2id$v=19$m=65536,t=3,p=4$ghi789$hash789",
                "email": "disabled@example.com",
                "disabled": True,
                "groups": ["guests"],
            },
        }
    }

    db_path = temp_dir / "users_database.yml"
    with open(db_path, "w") as f:
        yaml.dump(users_data, f)

    return db_path


@pytest.fixture
def empty_users_yaml(temp_dir: Path) -> Path:
    """Create an empty users_database.yml file."""
    users_data = {"users": {}}

    db_path = temp_dir / "users_database.yml"
    with open(db_path, "w") as f:
        yaml.dump(users_data, f)

    return db_path
