# Cockpit Authelia Users - Development Guide

## For Agentic Coding: Use the HaLOS Workspace

This repository should be used as part of the halos-distro workspace for AI-assisted development:

```bash
# Clone workspace and all repos
git clone https://github.com/hatlabs/halos-distro.git
cd halos-distro
./run repos:clone
```

See `halos-distro/docs/` for development workflows and guidance.

## About This Project

Cockpit plugin for managing Authelia users. Provides a web-based interface within Cockpit to create, edit, disable, and delete Authelia user accounts.

**Documentation:**
- `docs/SPEC.md` - Technical specification
- `docs/ARCHITECTURE.md` - System architecture
- `docs/IMPLEMENTATION_CHECKLIST.md` - Implementation workflow

## Git Workflow Policy

**MANDATORY:** PRs must ALWAYS have all checks passing before merging.

## Architecture

### Three-Tier Design

1. **Backend** (`backend/`): Python CLI using YAML for Authelia user database
   - JSON input/output for structured communication
   - Command-based interface: list-users, get-user, create-user, update-user, delete-user
   - Runs via cockpit.spawn (no persistent daemon)

2. **API Layer** (`frontend/src/lib/`): TypeScript wrapper
   - Wraps cockpit.spawn calls
   - Provides type-safe Promise-based API
   - Handles error translation

3. **UI Layer** (`frontend/src/`): React + PatternFly
   - User list view
   - User create/edit forms
   - Group assignment with autocomplete

### Key Technologies

- **Backend**: Python 3.11+, PyYAML, argon2-cffi, uv, ruff, pyright, pytest
- **Frontend**: React 18, TypeScript, PatternFly 6, esbuild, vitest
- **Integration**: Cockpit API (cockpit.spawn)
- **Testing**: pytest (backend), vitest (frontend)

## Development Environment

### Quick Start

```bash
# Build development container
./run build-devtools

# Run tests
./run test

# Open shell in container
./run shell
```

### Frontend Development

```bash
cd frontend
npm install
npm run build
npm run watch   # Watch mode
npm run test    # Run tests
```

## Project Structure

```
backend/
  cockpit_authelia_users/
    cli.py                  # Entry point
    commands/               # Command handlers
      list_users.py
      get_user.py
      create_user.py
      update_user.py
      delete_user.py
      list_groups.py
    utils/
      database.py           # YAML file operations
      password.py           # Argon2id hashing
      validators.py         # Input validation
      errors.py             # Error handling
      logging.py            # Systemd journal logging
  tests/
  pyproject.toml

frontend/
  src/
    authelia-users.tsx      # Root component
    lib/
      api.ts               # Backend API wrapper
      types.ts             # TypeScript types
    views/
      UserListView.tsx
      UserFormView.tsx
    components/
      GroupInput.tsx
      ConfirmDialog.tsx
  tests/
  package.json
  tsconfig.json

docker/
  Dockerfile.devtools
  docker-compose.devtools.yml

debian/                     # Debian packaging
run                        # Development commands
VERSION                    # Package version
```

## Development Workflow

**MANDATORY:** Follow `docs/IMPLEMENTATION_CHECKLIST.md` for ALL implementations.

### Testing

```bash
# Backend tests
./run test

# Frontend tests
cd frontend && npm run test

# All linting
./run lint && ./run typecheck
cd frontend && npm run lint && npm run typecheck
```

## Common Development Tasks

### Adding a New Backend Command

1. Create `backend/cockpit_authelia_users/commands/mycommand.py`
2. Add tests in `backend/tests/test_commands/test_mycommand.py`
3. Register command in `cli.py`
4. Run tests: `./run test`

### Adding a New Frontend Component

1. Create `frontend/src/components/MyComponent.tsx`
2. Add tests in `frontend/tests/MyComponent.test.tsx`
3. Import and use in views
4. Run tests: `cd frontend && npm run test`

## Code Patterns

### Backend: Command Handler

```python
from ..utils.database import UserDatabase
from ..utils.errors import UserNotFoundError

def execute(user_id: str) -> dict:
    """Get a single user by ID."""
    db = UserDatabase.load()
    user = db.get_user(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user.to_dict()
```

### Frontend: API Call

```typescript
import { getUser } from "./lib/api";

const user = await getUser(userId);
```

## Git Commit Format

Follow conventional commits:
- `feat(backend): add password hashing`
- `fix(ui): handle empty user list`
- `docs: update README`
- `test: add validation tests`

## References

- [Cockpit Guide](https://cockpit-project.org/guide/latest/)
- [Authelia Users File](https://www.authelia.com/configuration/first-factor/file/)
- [PatternFly React](https://www.patternfly.org/get-started/develop/)

Part of the [HaLOS](https://github.com/hatlabs/halos-distro) distribution.
