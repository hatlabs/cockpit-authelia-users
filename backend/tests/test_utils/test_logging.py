"""Tests for logging module."""

from unittest.mock import MagicMock, patch

from cockpit_authelia_users.utils.logging import LOG_IDENTIFIER, log_operation


class TestLogOperation:
    """Tests for log_operation function."""

    @patch("cockpit_authelia_users.utils.logging._get_journal")
    def test_log_operation_with_user_id(self, mock_get_journal: MagicMock):
        """Log operation includes user ID."""
        mock_journal = MagicMock()
        mock_get_journal.return_value = mock_journal

        log_operation("create_user", user_id="john")

        mock_journal.send.assert_called_once()
        call_args = mock_journal.send.call_args
        assert "create_user" in call_args[0][0]
        assert "john" in call_args[0][0]
        assert call_args[1]["SYSLOG_IDENTIFIER"] == LOG_IDENTIFIER

    @patch("cockpit_authelia_users.utils.logging._get_journal")
    def test_log_operation_without_user_id(self, mock_get_journal: MagicMock):
        """Log operation works without user ID."""
        mock_journal = MagicMock()
        mock_get_journal.return_value = mock_journal

        log_operation("list_users")

        mock_journal.send.assert_called_once()
        call_args = mock_journal.send.call_args
        assert "list_users" in call_args[0][0]

    @patch("cockpit_authelia_users.utils.logging._get_journal")
    def test_log_operation_with_details(self, mock_get_journal: MagicMock):
        """Log operation can include additional details."""
        mock_journal = MagicMock()
        mock_get_journal.return_value = mock_journal

        log_operation("update_user", user_id="john", details="password changed")

        mock_journal.send.assert_called_once()
        call_args = mock_journal.send.call_args
        assert "update_user" in call_args[0][0]
        assert "john" in call_args[0][0]
        assert "password changed" in call_args[0][0]

    @patch("cockpit_authelia_users.utils.logging._get_journal")
    def test_log_identifier_is_correct(self, mock_get_journal: MagicMock):
        """Log identifier matches expected value."""
        assert LOG_IDENTIFIER == "cockpit-authelia-users"

    @patch("cockpit_authelia_users.utils.logging._get_journal")
    def test_log_operation_handles_missing_journal(self, mock_get_journal: MagicMock):
        """Log operation handles missing systemd journal gracefully."""
        mock_get_journal.return_value = None

        # Should not raise
        log_operation("create_user", user_id="john")
