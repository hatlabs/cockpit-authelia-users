"""List users command."""

from typing import Any

from ..utils.database import UserDatabase


def execute() -> list[dict[str, Any]]:
    """List all users.

    Returns:
        List of user dictionaries (without password hashes).
    """
    db = UserDatabase.load()
    return [user.to_dict() for user in db.list_users()]
