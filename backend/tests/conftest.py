"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


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
