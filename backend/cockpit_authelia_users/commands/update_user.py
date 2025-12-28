"""Update user command."""

from typing import Any

from ..utils.database import UserDatabase
from ..utils.errors import UserNotFoundError
from ..utils.logging import log_operation
from ..utils.password import hash_password
from ..utils.validators import (
    validate_displayname,
    validate_email,
    validate_groups,
)


def execute(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Update an existing user.

    Only updates fields that are provided in data.
    Password is optional - if provided, it will be hashed.

    Args:
        user_id: The user ID to update.
        data: Partial user data to update.

    Returns:
        Updated user dictionary (without password hash).

    Raises:
        UserNotFoundError: If the user does not exist.
        ValidationError: If the data is invalid.
    """
    # Load database and find user
    db = UserDatabase.load()
    user = db.get_user(user_id)

    if user is None:
        raise UserNotFoundError(user_id)

    # Update fields if provided
    password_changed = False

    if "displayname" in data:
        validate_displayname(data["displayname"])
        user.displayname = data["displayname"]

    if "email" in data:
        validate_email(data["email"])
        user.email = data["email"]

    if "password" in data and data["password"]:
        user.password = hash_password(data["password"])
        password_changed = True

    if "disabled" in data:
        user.disabled = bool(data["disabled"])

    if "groups" in data:
        validate_groups(data["groups"])
        user.groups = data["groups"]

    # Save
    db.update_user(user)
    db.save()

    # Log operation
    details = "password changed" if password_changed else None
    log_operation("update_user", user_id=user_id, details=details)

    return user.to_dict()
