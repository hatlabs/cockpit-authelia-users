# Cockpit Authelia Users - System Architecture

## System Overview

The plugin follows the established HaLOS Cockpit plugin pattern with a Python backend and React/TypeScript frontend. The backend provides a CLI interface for user database operations, invoked by the frontend via Cockpit's process spawning API.

```
┌─────────────────────────────────────────────────────────────┐
│                      Cockpit Web UI                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              cockpit-authelia-users                   │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │           React Frontend (PatternFly 6)         │  │  │
│  │  │  - User list view                               │  │  │
│  │  │  - User edit/create forms                       │  │  │
│  │  │  - Group assignment UI                          │  │  │
│  │  └──────────────────────┬──────────────────────────┘  │  │
│  │                         │ cockpit.spawn()              │  │
│  │  ┌──────────────────────▼──────────────────────────┐  │  │
│  │  │         Python Backend CLI                      │  │  │
│  │  │  cockpit-authelia-users-bridge <command>        │  │  │
│  │  │  - list-users                                   │  │  │
│  │  │  - get-user <id>                                │  │  │
│  │  │  - create-user                                  │  │  │
│  │  │  - update-user <id>                             │  │  │
│  │  │  - delete-user <id>                             │  │  │
│  │  └──────────────────────┬──────────────────────────┘  │  │
│  └─────────────────────────┼─────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │ File I/O (with locking)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  /var/lib/container-apps/halos-authelia-container/data/     │
│  └── users_database.yml                                     │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Frontend (React/TypeScript)

**Purpose**: Provides the user interface for managing Authelia users within Cockpit.

**Technology Stack**:
- React 18 with TypeScript
- PatternFly 6 (UI component library, consistent with Cockpit)
- esbuild (bundler)
- vitest (testing)

**Key Modules**:
- `authelia-users.tsx` - Root component with routing
- `lib/api.ts` - Backend communication via cockpit.spawn()
- `lib/types.ts` - TypeScript type definitions
- `views/UserListView.tsx` - Main user listing
- `views/UserFormView.tsx` - Create/edit user form
- `components/` - Reusable UI components

**Routing** (via cockpit.location):
- `/authelia-users/` - User list (default)
- `/authelia-users/new` - Create new user
- `/authelia-users/edit/:userId` - Edit existing user

### Backend (Python)

**Purpose**: Handles all user database operations with proper validation, file locking, and password hashing.

**Technology Stack**:
- Python 3.11+
- PyYAML (YAML parsing)
- argon2-cffi (password hashing)
- fcntl (file locking)
- systemd journal (logging)

**CLI Commands**:

| Command | Input | Output | Description |
|---------|-------|--------|-------------|
| `list-users` | - | JSON array of users | List all users (without password hashes) |
| `get-user <id>` | user_id | JSON user object | Get single user details |
| `create-user` | JSON via stdin | JSON result | Create new user |
| `update-user <id>` | JSON via stdin | JSON result | Update existing user |
| `delete-user <id>` | user_id | JSON result | Delete user |
| `list-groups` | - | JSON array of strings | List all unique groups |

**Key Modules**:
- `cli.py` - Command dispatcher (entry point)
- `commands/` - Individual command implementations
- `utils/database.py` - YAML file operations with locking
- `utils/password.py` - Argon2id hashing
- `utils/validators.py` - Input validation
- `utils/errors.py` - Custom exception hierarchy

## Data Models

### User (YAML Storage)

```yaml
users:
  johndoe:                    # user_id (key)
    displayname: "John Doe"   # required
    password: "$argon2id$..." # required, Argon2id hash
    email: "john@example.com" # required
    disabled: false           # optional, default false
    groups:                   # optional
      - admins
      - users
    # ... any other fields preserved on edit
```

### User (API Response)

Backend returns user data as JSON without the password hash:

```json
{
  "user_id": "johndoe",
  "displayname": "John Doe",
  "email": "john@example.com",
  "disabled": false,
  "groups": ["admins", "users"]
}
```

### User (API Request for Create/Update)

Frontend sends user data as JSON. Password field is plaintext (hashed by backend):

```json
{
  "displayname": "John Doe",
  "email": "john@example.com",
  "password": "plaintext-password",
  "disabled": false,
  "groups": ["admins", "users"]
}
```

For updates, only changed fields need to be included. Password field is optional on update.

## Integration Points

### Cockpit Integration

- **Manifest**: `manifest.json` registers the plugin with Cockpit
- **Menu Entry**: Appears in Cockpit sidebar under "Authelia Users"
- **Authentication**: Inherits Cockpit session authentication
- **Privilege Escalation**: Uses `superuser: "require"` for backend operations

### Authelia Integration

- **Read Path**: Backend reads users_database.yml directly
- **Write Path**: Backend writes users_database.yml with atomic replacement
- **No Restart Required**: Authelia watches the file for changes and auto-reloads
- **File Locking**: fcntl advisory locking prevents concurrent modifications

### Logging Integration

- Backend logs to systemd journal via Python's `systemd.journal` module
- Log identifier: `cockpit-authelia-users`
- Log levels: INFO for operations, WARNING for validation failures, ERROR for system failures

## Deployment Architecture

### Debian Package Contents

```
/usr/share/cockpit/authelia-users/
├── manifest.json
├── index.html
├── authelia-users.js
└── authelia-users.css

/usr/bin/
└── cockpit-authelia-users-bridge

/usr/lib/python3/dist-packages/
└── cockpit_authelia_users/
    ├── __init__.py
    ├── cli.py
    ├── commands/
    └── utils/
```

### Package Dependencies

- `cockpit (>= 276)` - Cockpit web console
- `python3 (>= 3.11)` - Python runtime
- `python3-yaml` - YAML parsing
- `python3-argon2` - Password hashing
- `python3-systemd` - Journal logging

## Security Considerations

### Authentication & Authorization

- All operations require authenticated Cockpit session
- Backend runs with elevated privileges (root) for file access
- No additional authorization layer (Cockpit login = admin access)

### Password Security

- Plaintext passwords only in memory during hashing
- Argon2id with memory-hard parameters resists GPU attacks
- Password hashes never returned to frontend
- Password fields cleared from memory after use

### Input Validation

- Backend validates all input before processing
- User ID: alphanumeric, underscore, hyphen, 1-64 chars
- Email: basic format validation
- Display name: non-empty, max 256 chars
- Groups: alphanumeric, underscore, hyphen per group name

### File Access

- User database file: mode 600 (owner read/write only)
- Atomic writes via temporary file + rename
- Advisory file locking prevents race conditions

## File Tree Structure

```
cockpit-authelia-users/
├── docs/
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_CHECKLIST.md
├── backend/
│   ├── cockpit_authelia_users/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── list_users.py
│   │   │   ├── get_user.py
│   │   │   ├── create_user.py
│   │   │   ├── update_user.py
│   │   │   ├── delete_user.py
│   │   │   └── list_groups.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── database.py
│   │       ├── password.py
│   │       ├── validators.py
│   │       ├── errors.py
│   │       └── logging.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_commands/
│   │   └── test_utils/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── authelia-users.tsx
│   │   ├── authelia-users.css
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── types.ts
│   │   │   └── errors.ts
│   │   ├── views/
│   │   │   ├── UserListView.tsx
│   │   │   └── UserFormView.tsx
│   │   └── components/
│   │       ├── UserCard.tsx
│   │       ├── GroupInput.tsx
│   │       └── ConfirmDialog.tsx
│   ├── tests/
│   ├── package.json
│   ├── tsconfig.json
│   └── esbuild.config.js
├── debian/
│   ├── control
│   ├── rules
│   ├── changelog
│   └── install
├── docker/
│   ├── Dockerfile.devtools
│   └── docker-compose.devtools.yml
├── run
├── VERSION
├── README.md
├── AGENTS.md
└── lefthook.yml
```
