"""YAML database operations with file locking.

Handles reading and writing the Authelia users_database.yml file
with proper file locking to prevent concurrent modification issues.
"""

import fcntl
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import DatabaseError

# Default path for the Authelia users database
DEFAULT_DATABASE_PATH = Path(
    "/var/lib/container-apps/halos-authelia-container/data/users_database.yml"
)

# Default groups always included in list_groups
DEFAULT_GROUPS = ["admins", "users", "guests"]


@dataclass
class User:
    """Represents a user in the Authelia database.

    The password field contains the Argon2id hash, not plaintext.
    Extra fields from the YAML are preserved in extra_fields.
    """

    user_id: str
    displayname: str
    password: str
    email: str
    disabled: bool = False
    groups: list[str] = field(default_factory=list)
    extra_fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_password: bool = False) -> dict[str, Any]:
        """Convert to dictionary for JSON output.

        Args:
            include_password: Whether to include the password hash.

        Returns:
            Dictionary representation of the user.
        """
        result: dict[str, Any] = {
            "user_id": self.user_id,
            "displayname": self.displayname,
            "email": self.email,
            "disabled": self.disabled,
            "groups": self.groups,
        }
        if include_password:
            result["password"] = self.password
        return result

    def to_yaml_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML storage.

        Returns:
            Dictionary representation for YAML, including all fields.
        """
        result: dict[str, Any] = {
            "displayname": self.displayname,
            "password": self.password,
            "email": self.email,
        }
        if self.disabled:
            result["disabled"] = self.disabled
        if self.groups:
            result["groups"] = self.groups

        # Merge extra fields (preserves unknown fields)
        result.update(self.extra_fields)

        return result


class UserDatabase:
    """Manages the Authelia users database."""

    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    @classmethod
    def load(cls, path: Path | None = None) -> "UserDatabase":
        """Load the database from a YAML file.

        Args:
            path: Path to the YAML file. Defaults to the standard location.

        Returns:
            UserDatabase instance with loaded users.

        Raises:
            DatabaseError: If the file is malformed.
        """
        if path is None:
            path = DEFAULT_DATABASE_PATH

        db = cls()

        if not path.exists():
            return db

        try:
            with open(path) as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = yaml.safe_load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except yaml.YAMLError as e:
            raise DatabaseError(f"Failed to parse YAML: {e}", path=str(path))
        except OSError as e:
            raise DatabaseError(f"Failed to read file: {e}", path=str(path))

        if data is None:
            return db

        users_data = data.get("users", {})
        if not isinstance(users_data, dict):
            return db

        for user_id, user_data in users_data.items():
            if not isinstance(user_data, dict):
                continue

            # Extract known fields
            displayname = user_data.get("displayname", "")
            password = user_data.get("password", "")
            email = user_data.get("email", "")
            disabled = user_data.get("disabled", False)
            groups = user_data.get("groups", [])

            # Collect extra fields
            known_fields = {"displayname", "password", "email", "disabled", "groups"}
            extra_fields = {k: v for k, v in user_data.items() if k not in known_fields}

            db.users[user_id] = User(
                user_id=user_id,
                displayname=displayname,
                password=password,
                email=email,
                disabled=disabled,
                groups=groups if isinstance(groups, list) else [],
                extra_fields=extra_fields,
            )

        return db

    def save(self, path: Path | None = None) -> None:
        """Save the database to a YAML file atomically.

        Uses a temporary file and rename to ensure atomic writes.

        Note on concurrency: The file lock is held on the temporary file during
        write, not the target file. This means concurrent saves could race on
        os.replace(). Since os.replace() is atomic on POSIX, this is safe -
        the last writer wins and no partial writes occur. This is acceptable
        for this use case where concurrent writes are rare.

        Args:
            path: Path to save to. Defaults to the standard location.

        Raises:
            DatabaseError: If the write fails.
        """
        if path is None:
            path = DEFAULT_DATABASE_PATH

        # Build the YAML structure
        data = {
            "users": {
                user_id: user.to_yaml_dict() for user_id, user in self.users.items()
            }
        }

        try:
            # Write to temporary file first
            dir_path = path.parent
            dir_path.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=dir_path,
                prefix=".users_database_",
                suffix=".yml",
                delete=False,
            ) as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                temp_path = f.name

            # Atomic rename
            os.replace(temp_path, path)

        except OSError as e:
            raise DatabaseError(f"Failed to write file: {e}", path=str(path))

    def get_user(self, user_id: str) -> User | None:
        """Get a user by ID.

        Args:
            user_id: The user ID to look up.

        Returns:
            The User if found, None otherwise.
        """
        return self.users.get(user_id)

    def list_users(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users.
        """
        return list(self.users.values())

    def add_user(self, user: User) -> None:
        """Add a new user.

        Args:
            user: The user to add.
        """
        self.users[user.user_id] = user

    def update_user(self, user: User) -> None:
        """Update an existing user.

        Args:
            user: The user with updated data.
        """
        self.users[user.user_id] = user

    def delete_user(self, user_id: str) -> None:
        """Delete a user.

        Args:
            user_id: The user ID to delete.
        """
        self.users.pop(user_id, None)

    def list_groups(self) -> list[str]:
        """Get all unique groups.

        Returns:
            Sorted list of all unique group names, including defaults.
        """
        groups = set(DEFAULT_GROUPS)
        for user in self.users.values():
            groups.update(user.groups)
        return sorted(groups)
