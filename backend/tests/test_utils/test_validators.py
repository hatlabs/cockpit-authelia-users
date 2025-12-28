"""Tests for input validation module."""

import pytest

from cockpit_authelia_users.utils.errors import ValidationError
from cockpit_authelia_users.utils.validators import (
    validate_displayname,
    validate_email,
    validate_groups,
    validate_user_data,
    validate_user_id,
)


class TestValidateUserId:
    """Tests for validate_user_id function."""

    def test_valid_alphanumeric(self):
        """Alphanumeric user IDs are valid."""
        validate_user_id("john123")  # Should not raise

    def test_valid_with_underscore(self):
        """User IDs with underscores are valid."""
        validate_user_id("john_doe")  # Should not raise

    def test_valid_with_hyphen(self):
        """User IDs with hyphens are valid."""
        validate_user_id("john-doe")  # Should not raise

    def test_valid_single_character(self):
        """Single character user IDs are valid."""
        validate_user_id("a")  # Should not raise

    def test_valid_max_length(self):
        """User IDs at max length (64) are valid."""
        validate_user_id("a" * 64)  # Should not raise

    def test_invalid_empty(self):
        """Empty user IDs are invalid."""
        with pytest.raises(ValidationError) as exc:
            validate_user_id("")
        assert exc.value.details == {"field": "user_id"}

    def test_invalid_too_long(self):
        """User IDs over 64 characters are invalid."""
        with pytest.raises(ValidationError) as exc:
            validate_user_id("a" * 65)
        assert exc.value.details == {"field": "user_id"}

    def test_invalid_special_chars(self):
        """User IDs with special characters are invalid."""
        with pytest.raises(ValidationError):
            validate_user_id("john@doe")

    def test_invalid_spaces(self):
        """User IDs with spaces are invalid."""
        with pytest.raises(ValidationError):
            validate_user_id("john doe")

    def test_invalid_unicode(self):
        """User IDs with unicode are invalid."""
        with pytest.raises(ValidationError):
            validate_user_id("пользователь")


class TestValidateEmail:
    """Tests for validate_email function."""

    def test_valid_simple(self):
        """Simple email addresses are valid."""
        validate_email("john@example.com")  # Should not raise

    def test_valid_subdomain(self):
        """Emails with subdomains are valid."""
        validate_email("john@mail.example.com")  # Should not raise

    def test_valid_plus_addressing(self):
        """Emails with plus addressing are valid."""
        validate_email("john+tag@example.com")  # Should not raise

    def test_invalid_empty(self):
        """Empty emails are invalid."""
        with pytest.raises(ValidationError) as exc:
            validate_email("")
        assert exc.value.details == {"field": "email"}

    def test_invalid_no_at(self):
        """Emails without @ are invalid."""
        with pytest.raises(ValidationError):
            validate_email("johnexample.com")

    def test_invalid_no_domain(self):
        """Emails without domain are invalid."""
        with pytest.raises(ValidationError):
            validate_email("john@")

    def test_invalid_no_local(self):
        """Emails without local part are invalid."""
        with pytest.raises(ValidationError):
            validate_email("@example.com")


class TestValidateDisplayname:
    """Tests for validate_displayname function."""

    def test_valid_simple(self):
        """Simple display names are valid."""
        validate_displayname("John Doe")  # Should not raise

    def test_valid_unicode(self):
        """Unicode display names are valid."""
        validate_displayname("Иван Петров")  # Should not raise

    def test_valid_max_length(self):
        """Display names at max length (256) are valid."""
        validate_displayname("a" * 256)  # Should not raise

    def test_invalid_empty(self):
        """Empty display names are invalid."""
        with pytest.raises(ValidationError) as exc:
            validate_displayname("")
        assert exc.value.details == {"field": "displayname"}

    def test_invalid_whitespace_only(self):
        """Whitespace-only display names are invalid."""
        with pytest.raises(ValidationError):
            validate_displayname("   ")

    def test_invalid_too_long(self):
        """Display names over 256 characters are invalid."""
        with pytest.raises(ValidationError):
            validate_displayname("a" * 257)


class TestValidateGroups:
    """Tests for validate_groups function."""

    def test_valid_empty_list(self):
        """Empty group list is valid."""
        validate_groups([])  # Should not raise

    def test_valid_single_group(self):
        """Single group is valid."""
        validate_groups(["admins"])  # Should not raise

    def test_valid_multiple_groups(self):
        """Multiple groups are valid."""
        validate_groups(["admins", "users", "guests"])  # Should not raise

    def test_valid_group_with_hyphen(self):
        """Group names with hyphens are valid."""
        validate_groups(["power-users"])  # Should not raise

    def test_valid_group_with_underscore(self):
        """Group names with underscores are valid."""
        validate_groups(["power_users"])  # Should not raise

    def test_invalid_not_list(self):
        """Non-list groups are invalid."""
        with pytest.raises(ValidationError) as exc:
            validate_groups("admins")  # type: ignore
        assert exc.value.details == {"field": "groups"}

    def test_invalid_empty_group_name(self):
        """Empty group names are invalid."""
        with pytest.raises(ValidationError):
            validate_groups(["admins", ""])

    def test_invalid_group_special_chars(self):
        """Group names with special characters are invalid."""
        with pytest.raises(ValidationError):
            validate_groups(["admin@group"])

    def test_invalid_group_spaces(self):
        """Group names with spaces are invalid."""
        with pytest.raises(ValidationError):
            validate_groups(["admin group"])


class TestValidateUserData:
    """Tests for validate_user_data function."""

    def test_valid_complete(self):
        """Complete user data is valid."""
        data = {
            "user_id": "john",
            "displayname": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
            "groups": ["users"],
        }
        validate_user_data(data, require_password=True)  # Should not raise

    def test_valid_minimal(self):
        """Minimal user data is valid."""
        data = {
            "user_id": "john",
            "displayname": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
        }
        validate_user_data(data, require_password=True)  # Should not raise

    def test_valid_without_password_when_not_required(self):
        """User data without password is valid when not required."""
        data = {
            "user_id": "john",
            "displayname": "John Doe",
            "email": "john@example.com",
        }
        validate_user_data(data, require_password=False)  # Should not raise

    def test_invalid_missing_user_id(self):
        """Missing user_id is invalid."""
        data = {
            "displayname": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)

    def test_invalid_missing_displayname(self):
        """Missing displayname is invalid."""
        data = {
            "user_id": "john",
            "email": "john@example.com",
            "password": "secret123",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)

    def test_invalid_missing_email(self):
        """Missing email is invalid."""
        data = {
            "user_id": "john",
            "displayname": "John Doe",
            "password": "secret123",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)

    def test_invalid_missing_password_when_required(self):
        """Missing password is invalid when required."""
        data = {
            "user_id": "john",
            "displayname": "John Doe",
            "email": "john@example.com",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)

    def test_invalid_user_id_format(self):
        """Invalid user_id format is caught."""
        data = {
            "user_id": "john@doe",
            "displayname": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)

    def test_validates_all_fields(self):
        """All fields are validated."""
        data = {
            "user_id": "john",
            "displayname": "",  # Invalid
            "email": "john@example.com",
            "password": "secret123",
        }
        with pytest.raises(ValidationError):
            validate_user_data(data, require_password=True)
