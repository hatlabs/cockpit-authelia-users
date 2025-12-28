# Cockpit Authelia Users - Backend

Python backend for the Cockpit Authelia Users plugin.

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Type check
uv run pyright
```

## CLI Commands

- `cockpit-authelia-users-bridge list-users` - List all users
- `cockpit-authelia-users-bridge get-user <id>` - Get a single user
- `cockpit-authelia-users-bridge create-user` - Create a user (reads JSON from stdin)
- `cockpit-authelia-users-bridge update-user <id>` - Update a user (reads JSON from stdin)
- `cockpit-authelia-users-bridge delete-user <id>` - Delete a user
- `cockpit-authelia-users-bridge list-groups` - List all groups
