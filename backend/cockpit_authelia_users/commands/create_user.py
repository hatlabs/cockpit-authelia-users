"""Create user command."""

from typing import Any

from ..utils.database import User, UserDatabase
from ..utils.errors import UserExistsError
from ..utils.logging import log_operation
from ..utils.password import hash_password
from ..utils.validators import validate_user_data


def execute(data: dict[str, Any]) -> dict[str, Any]:
    """Create a new user.

    Args:
        data: User data including user_id, displayname, email, password, groups.

    Returns:
        Created user dictionary (without password hash).

    Raises:
        ValidationError: If the data is invalid.
        UserExistsError: If a user with this ID already exists.
    """
    # Validate input
    validate_user_data(data, require_password=True)

    user_id = data["user_id"]

    # Load database and check for existing user
    db = UserDatabase.load()
    if db.get_user(user_id) is not None:
        raise UserExistsError(user_id)

    # Create user with hashed password
    user = User(
        user_id=user_id,
        displayname=data["displayname"],
        password=hash_password(data["password"]),
        email=data["email"],
        disabled=data.get("disabled", False),
        groups=data.get("groups", []),
    )

    # Save
    db.add_user(user)
    db.save()

    # Log operation
    log_operation("create_user", user_id=user_id)

    return user.to_dict()
