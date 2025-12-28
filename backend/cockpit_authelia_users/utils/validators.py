"""Input validation for user data.

Validation rules:
- user_id: alphanumeric, underscore, hyphen, 1-64 chars
- email: basic email format validation
- displayname: non-empty, max 256 chars
- groups: list of valid group names (alphanumeric, underscore, hyphen)
"""

import re
from typing import Any

from .errors import ValidationError

# Validation patterns
USER_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
GROUP_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Limits
MAX_USER_ID_LENGTH = 64
MAX_DISPLAYNAME_LENGTH = 256


def validate_user_id(value: str) -> None:
    """Validate a user ID.

    Args:
        value: The user ID to validate.

    Raises:
        ValidationError: If the user ID is invalid.
    """
    if not value:
        raise ValidationError("user_id", "User ID cannot be empty")

    if len(value) > MAX_USER_ID_LENGTH:
        raise ValidationError(
            "user_id", f"User ID cannot exceed {MAX_USER_ID_LENGTH} characters"
        )

    if not USER_ID_PATTERN.match(value):
        raise ValidationError(
            "user_id",
            "User ID must contain only alphanumeric characters, underscores, and hyphens",
        )


def validate_email(value: str) -> None:
    """Validate an email address.

    Args:
        value: The email to validate.

    Raises:
        ValidationError: If the email is invalid.
    """
    if not value:
        raise ValidationError("email", "Email cannot be empty")

    if not EMAIL_PATTERN.match(value):
        raise ValidationError("email", "Invalid email format")


def validate_displayname(value: str) -> None:
    """Validate a display name.

    Args:
        value: The display name to validate.

    Raises:
        ValidationError: If the display name is invalid.
    """
    if not value or not value.strip():
        raise ValidationError("displayname", "Display name cannot be empty")

    if len(value) > MAX_DISPLAYNAME_LENGTH:
        raise ValidationError(
            "displayname", f"Display name cannot exceed {MAX_DISPLAYNAME_LENGTH} characters"
        )


def validate_groups(value: Any) -> None:
    """Validate a list of group names.

    Args:
        value: The groups list to validate.

    Raises:
        ValidationError: If the groups are invalid.
    """
    if not isinstance(value, list):
        raise ValidationError("groups", "Groups must be a list")

    for group in value:
        if not group:
            raise ValidationError("groups", "Group name cannot be empty")

        if not GROUP_NAME_PATTERN.match(group):
            raise ValidationError(
                "groups",
                f"Group name '{group}' must contain only alphanumeric characters, "
                "underscores, and hyphens",
            )


def validate_user_data(data: dict[str, Any], require_password: bool = True) -> None:
    """Validate complete user data for create/update operations.

    Args:
        data: The user data dictionary to validate.
        require_password: Whether password is required (True for create, False for update).

    Raises:
        ValidationError: If any field is invalid.
    """
    # Required fields
    if "user_id" not in data:
        raise ValidationError("user_id", "User ID is required")
    validate_user_id(data["user_id"])

    if "displayname" not in data:
        raise ValidationError("displayname", "Display name is required")
    validate_displayname(data["displayname"])

    if "email" not in data:
        raise ValidationError("email", "Email is required")
    validate_email(data["email"])

    # Password - required for create, optional for update
    if require_password and "password" not in data:
        raise ValidationError("password", "Password is required")

    # Optional fields
    if "groups" in data:
        validate_groups(data["groups"])
