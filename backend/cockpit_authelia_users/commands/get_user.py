"""Get user command."""

from typing import Any

from ..utils.database import UserDatabase
from ..utils.errors import UserNotFoundError


def execute(user_id: str) -> dict[str, Any]:
    """Get a single user by ID.

    Args:
        user_id: The user ID to retrieve.

    Returns:
        User dictionary (without password hash).

    Raises:
        UserNotFoundError: If the user does not exist.
    """
    db = UserDatabase.load()
    user = db.get_user(user_id)

    if user is None:
        raise UserNotFoundError(user_id)

    return user.to_dict()
