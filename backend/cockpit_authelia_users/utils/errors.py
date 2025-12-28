"""Custom exception hierarchy for Authelia Users backend."""

from typing import Any


class AutheliaUsersError(Exception):
    """Base exception for all Authelia Users errors.

    All errors have a code, message, and optional details dictionary.
    Errors can be serialized to JSON for CLI output.
    """

    code: str = "AUTHELIA_USERS_ERROR"

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Serialize error to dictionary for JSON output."""
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details is not None:
            result["details"] = self.details
        return result

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class UserNotFoundError(AutheliaUsersError):
    """Raised when a requested user does not exist."""

    code = "USER_NOT_FOUND"

    def __init__(self, user_id: str) -> None:
        super().__init__(
            message=f"User not found: {user_id}",
            details={"user_id": user_id},
        )


class UserExistsError(AutheliaUsersError):
    """Raised when trying to create a user that already exists."""

    code = "USER_EXISTS"

    def __init__(self, user_id: str) -> None:
        super().__init__(
            message=f"User already exists: {user_id}",
            details={"user_id": user_id},
        )


class ValidationError(AutheliaUsersError):
    """Raised when input validation fails."""

    code = "VALIDATION_ERROR"

    def __init__(self, field: str | None, message: str) -> None:
        details = {"field": field} if field is not None else None
        super().__init__(message=message, details=details)


class DatabaseError(AutheliaUsersError):
    """Raised when database operations fail."""

    code = "DATABASE_ERROR"

    def __init__(self, message: str, path: str | None = None) -> None:
        details = {"path": path} if path is not None else None
        super().__init__(message=message, details=details)
