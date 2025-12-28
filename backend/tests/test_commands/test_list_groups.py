"""Tests for list_groups command."""

from pathlib import Path

import pytest

from cockpit_authelia_users.commands import list_groups
from cockpit_authelia_users.utils.database import UserDatabase


class TestListGroups:
    """Tests for list_groups.execute()."""

    def test_list_groups_includes_defaults(self, empty_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Default groups (admins, users, guests) always included."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(empty_users_yaml))

        result = list_groups.execute()

        assert "admins" in result
        assert "users" in result
        assert "guests" in result

    def test_list_groups_collects_from_users(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Groups are collected from all users."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_groups.execute()

        # Sample users have: admins, users, guests
        assert "admins" in result
        assert "users" in result
        assert "guests" in result

    def test_list_groups_returns_sorted_list(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Groups are returned sorted."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_groups.execute()

        assert result == sorted(result)

    def test_list_groups_deduplicates(self, sample_users_yaml: Path, monkeypatch: pytest.MonkeyPatch):
        """Groups are deduplicated."""
        _original_load = UserDatabase.load
        monkeypatch.setattr(UserDatabase, "load", lambda path=None: _original_load(sample_users_yaml))

        result = list_groups.execute()

        # Each group should appear only once
        assert len(result) == len(set(result))
