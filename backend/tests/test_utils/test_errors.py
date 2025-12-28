"""Tests for error handling module."""

from cockpit_authelia_users.utils.errors import (
    AutheliaUsersError,
    DatabaseError,
    UserExistsError,
    UserNotFoundError,
    ValidationError,
)


class TestAutheliaUsersError:
    """Tests for the base exception class."""

    def test_create_with_message(self):
        """Error can be created with just a message."""
        error = AutheliaUsersError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.code == "AUTHELIA_USERS_ERROR"
        assert error.details is None

    def test_create_with_all_fields(self):
        """Error can be created with all fields."""
        error = AutheliaUsersError(
            message="Something went wrong",
            code="CUSTOM_ERROR",
            details={"key": "value"},
        )
        assert error.message == "Something went wrong"
        assert error.code == "CUSTOM_ERROR"
        assert error.details == {"key": "value"}

    def test_to_dict(self):
        """Error can be serialized to dictionary."""
        error = AutheliaUsersError(
            message="Something went wrong",
            code="CUSTOM_ERROR",
            details={"key": "value"},
        )
        result = error.to_dict()
        assert result == {
            "code": "CUSTOM_ERROR",
            "message": "Something went wrong",
            "details": {"key": "value"},
        }

    def test_to_dict_without_details(self):
        """Error serialization excludes None details."""
        error = AutheliaUsersError("Something went wrong")
        result = error.to_dict()
        assert result == {
            "code": "AUTHELIA_USERS_ERROR",
            "message": "Something went wrong",
        }

    def test_str_representation(self):
        """Error has string representation."""
        error = AutheliaUsersError("Something went wrong", code="CUSTOM_ERROR")
        assert str(error) == "CUSTOM_ERROR: Something went wrong"


class TestUserNotFoundError:
    """Tests for UserNotFoundError."""

    def test_create_with_user_id(self):
        """Error is created with user ID."""
        error = UserNotFoundError("john")
        assert error.message == "User not found: john"
        assert error.code == "USER_NOT_FOUND"
        assert error.details == {"user_id": "john"}

    def test_inherits_from_base(self):
        """Error inherits from AutheliaUsersError."""
        error = UserNotFoundError("john")
        assert isinstance(error, AutheliaUsersError)


class TestUserExistsError:
    """Tests for UserExistsError."""

    def test_create_with_user_id(self):
        """Error is created with user ID."""
        error = UserExistsError("john")
        assert error.message == "User already exists: john"
        assert error.code == "USER_EXISTS"
        assert error.details == {"user_id": "john"}

    def test_inherits_from_base(self):
        """Error inherits from AutheliaUsersError."""
        error = UserExistsError("john")
        assert isinstance(error, AutheliaUsersError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_create_with_field_and_message(self):
        """Error is created with field and message."""
        error = ValidationError("email", "Invalid email format")
        assert error.message == "Invalid email format"
        assert error.code == "VALIDATION_ERROR"
        assert error.details == {"field": "email"}

    def test_create_with_general_message(self):
        """Error can be created without a specific field."""
        error = ValidationError(None, "Invalid user data")
        assert error.message == "Invalid user data"
        assert error.code == "VALIDATION_ERROR"
        assert error.details is None

    def test_inherits_from_base(self):
        """Error inherits from AutheliaUsersError."""
        error = ValidationError("email", "Invalid email format")
        assert isinstance(error, AutheliaUsersError)


class TestDatabaseError:
    """Tests for DatabaseError."""

    def test_create_with_message(self):
        """Error is created with message."""
        error = DatabaseError("Failed to read database")
        assert error.message == "Failed to read database"
        assert error.code == "DATABASE_ERROR"

    def test_create_with_path(self):
        """Error can include file path."""
        error = DatabaseError("Failed to read database", path="/path/to/file.yml")
        assert error.message == "Failed to read database"
        assert error.code == "DATABASE_ERROR"
        assert error.details == {"path": "/path/to/file.yml"}

    def test_inherits_from_base(self):
        """Error inherits from AutheliaUsersError."""
        error = DatabaseError("Failed to read database")
        assert isinstance(error, AutheliaUsersError)


class TestErrorCodes:
    """Tests to ensure unique error codes."""

    def test_all_errors_have_unique_codes(self):
        """All error types have unique codes."""
        codes = [
            AutheliaUsersError("test").code,
            UserNotFoundError("test").code,
            UserExistsError("test").code,
            ValidationError("field", "test").code,
            DatabaseError("test").code,
        ]
        assert len(codes) == len(set(codes)), "Error codes must be unique"
