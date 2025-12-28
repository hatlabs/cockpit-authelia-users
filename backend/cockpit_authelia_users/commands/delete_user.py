"""Delete user command."""

from typing import Any

from ..utils.database import UserDatabase
from ..utils.errors import UserNotFoundError
from ..utils.logging import log_operation


def execute(user_id: str) -> dict[str, Any]:
    """Delete a user.

    Args:
        user_id: The user ID to delete.

    Returns:
        Success confirmation.

    Raises:
        UserNotFoundError: If the user does not exist.
    """
    # Load database and find user
    db = UserDatabase.load()
    user = db.get_user(user_id)

    if user is None:
        raise UserNotFoundError(user_id)

    # Delete
    db.delete_user(user_id)
    db.save()

    # Log operation
    log_operation("delete_user", user_id=user_id)

    return {"success": True}
