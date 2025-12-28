"""Password hashing utilities using Argon2id.

Uses Authelia-compatible parameters:
- Memory: 65536 KB (64 MB)
- Iterations: 3
- Parallelism: 4
"""

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Authelia-compatible Argon2id parameters
# See: https://www.authelia.com/configuration/first-factor/file/
_hasher = PasswordHasher(
    time_cost=3,  # iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,  # Argon2id
)


def hash_password(plaintext: str) -> str:
    """Hash a plaintext password using Argon2id.

    Args:
        plaintext: The plaintext password to hash.

    Returns:
        The Argon2id hash in PHC format (compatible with Authelia).
    """
    return _hasher.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext password against a hash.

    Args:
        plaintext: The plaintext password to verify.
        hashed: The Argon2id hash to verify against.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        _hasher.verify(hashed, plaintext)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False
