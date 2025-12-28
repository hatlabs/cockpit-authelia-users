"""List groups command."""

from ..utils.database import UserDatabase


def execute() -> list[str]:
    """List all unique groups.

    Returns:
        Sorted list of unique group names.
    """
    db = UserDatabase.load()
    return db.list_groups()
