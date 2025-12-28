"""Logging utilities using systemd journal."""

from typing import Any

LOG_IDENTIFIER = "cockpit-authelia-users"

# Cache the journal module to avoid repeated imports
_journal_module: Any = None
_journal_checked = False


def _get_journal() -> Any:
    """Get the systemd journal module, or None if not available."""
    global _journal_module, _journal_checked

    if _journal_checked:
        return _journal_module

    _journal_checked = True
    try:
        from systemd import journal

        _journal_module = journal
    except ImportError:
        _journal_module = None

    return _journal_module


def log_operation(
    operation: str,
    user_id: str | None = None,
    details: str | None = None,
) -> None:
    """Log an operation to the systemd journal.

    Args:
        operation: The operation being performed (e.g., "create_user", "delete_user")
        user_id: Optional user ID involved in the operation
        details: Optional additional details (never include passwords!)
    """
    journal = _get_journal()
    if journal is None:
        # Systemd journal not available (e.g., in tests or non-Linux)
        return

    # Build the log message
    parts = [f"Operation: {operation}"]
    if user_id is not None:
        parts.append(f"user_id={user_id}")
    if details is not None:
        parts.append(f"details={details}")

    message = " | ".join(parts)

    journal.send(
        message,
        SYSLOG_IDENTIFIER=LOG_IDENTIFIER,
    )
