"""CLI entry point for cockpit-authelia-users-bridge."""

import argparse
import json
import sys
from typing import Any

from .utils.errors import AutheliaUsersError
from .utils.logging import log_operation


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cockpit-authelia-users-bridge",
        description="Backend CLI for Authelia user management",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-users command
    subparsers.add_parser("list-users", help="List all users")

    # get-user command
    get_user = subparsers.add_parser("get-user", help="Get a single user")
    get_user.add_argument("user_id", help="User ID to retrieve")

    # create-user command
    subparsers.add_parser("create-user", help="Create a new user (reads JSON from stdin)")

    # update-user command
    update_user = subparsers.add_parser("update-user", help="Update a user (reads JSON from stdin)")
    update_user.add_argument("user_id", help="User ID to update")

    # delete-user command
    delete_user = subparsers.add_parser("delete-user", help="Delete a user")
    delete_user.add_argument("user_id", help="User ID to delete")

    # list-groups command
    subparsers.add_parser("list-groups", help="List all unique groups")

    args = parser.parse_args()

    try:
        result = dispatch_command(args)
        print(json.dumps(result))
    except AutheliaUsersError as e:
        print(json.dumps(e.to_dict()), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        log_operation("internal_error", details=str(e))
        error = {
            "code": "INTERNAL_ERROR",
            "message": str(e),
        }
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)


def dispatch_command(args: argparse.Namespace) -> dict[str, Any] | list[Any]:
    """Dispatch to the appropriate command handler."""
    # Import here to avoid circular imports
    from .commands import create_user, delete_user, get_user, list_groups, list_users, update_user

    match args.command:
        case "list-users":
            return list_users.execute()
        case "get-user":
            return get_user.execute(args.user_id)
        case "create-user":
            data = json.loads(sys.stdin.read())
            return create_user.execute(data)
        case "update-user":
            data = json.loads(sys.stdin.read())
            return update_user.execute(args.user_id, data)
        case "delete-user":
            return delete_user.execute(args.user_id)
        case "list-groups":
            return list_groups.execute()
        case _:
            raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
