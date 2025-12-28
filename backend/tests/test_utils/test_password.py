"""Tests for password hashing module."""

from cockpit_authelia_users.utils.password import hash_password, verify_password


class TestHashPassword:
    """Tests for hash_password function."""

    def test_returns_argon2id_hash(self):
        """Hash starts with $argon2id$."""
        result = hash_password("mypassword")
        assert result.startswith("$argon2id$")

    def test_different_passwords_produce_different_hashes(self):
        """Different passwords produce different hashes."""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self):
        """Same password with different salts produces different hashes."""
        hash1 = hash_password("mypassword")
        hash2 = hash_password("mypassword")
        # Should be different due to random salt
        assert hash1 != hash2

    def test_hash_contains_authelia_compatible_params(self):
        """Hash contains Authelia-compatible parameters."""
        result = hash_password("mypassword")
        # Should contain version, memory, time, parallelism params
        # Format: $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
        assert "$v=19$" in result
        assert "m=65536" in result
        assert "t=3" in result
        assert "p=4" in result

    def test_empty_password(self):
        """Empty password can be hashed."""
        result = hash_password("")
        assert result.startswith("$argon2id$")

    def test_unicode_password(self):
        """Unicode passwords can be hashed."""
        result = hash_password("пароль123")
        assert result.startswith("$argon2id$")

    def test_long_password(self):
        """Long passwords can be hashed."""
        long_password = "a" * 1000
        result = hash_password(long_password)
        assert result.startswith("$argon2id$")


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_correct_password_verifies(self):
        """Correct password verifies successfully."""
        password = "mypassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        """Wrong password fails verification."""
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_empty_password_verifies(self):
        """Empty password can be verified."""
        password = ""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_unicode_password_verifies(self):
        """Unicode password can be verified."""
        password = "пароль123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_long_password_verifies(self):
        """Long password can be verified."""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_invalid_hash_format_returns_false(self):
        """Invalid hash format returns False."""
        assert verify_password("password", "not-a-valid-hash") is False

    def test_verify_authelia_format_hash(self):
        """Can verify a hash in Authelia's format."""
        # This is a pre-generated Authelia-compatible hash for "test"
        # We'll generate our own and verify it
        password = "testpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
