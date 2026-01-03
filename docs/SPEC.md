# Cockpit Authelia Users - Technical Specification

## Project Overview

Cockpit Authelia Users is a Cockpit plugin that provides a web-based administration interface for managing Authelia users. It enables system administrators to create, edit, disable, and delete user accounts directly from the Cockpit web console without manually editing YAML configuration files.

## Goals

1. Provide a simple, intuitive UI for Authelia user management within Cockpit
2. Support all essential user operations: create, read, update, delete, disable/enable
3. Maintain compatibility with Authelia's file-based user database format
4. Preserve any user fields not directly managed by the UI (future-proofing)
5. Follow established HaLOS Cockpit plugin patterns for consistency

## Core Features

### User Management

- **List Users**: Display all users with their status (enabled/disabled), display name, email, and group memberships
- **Create User**: Add new users with required fields (username, password, display name, email) and optional group assignments
- **Edit User**: Modify user details including display name, email, and group memberships
- **Change Password**: Set a new password for a user (admin operation, no old password required)
- **Delete User**: Remove a user from the system with confirmation
- **Enable/Disable User**: Toggle user account status without deletion

### Group Assignment

- Users can be assigned to one or more groups by entering group names
- **Suggested Groups**: admins, users, guests (offered as suggestions in UI)
- **Custom Groups**: Any group name can be entered freely (groups are just strings)
- UI shows existing groups from all users as autocomplete suggestions

## Technical Requirements

### User Data Fields

The following fields are managed by the UI:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | Unique username (the YAML key) |
| disabled | boolean | No | Account disabled status (default: false) |
| displayname | string | Yes | Human-readable display name |
| password | string | Yes | Argon2id password hash |
| email | string | Yes | User email address |
| groups | list[string] | No | Group memberships |

### Password Handling

- UI accepts plaintext passwords from administrators
- Backend hashes passwords using Argon2id with Authelia-compatible parameters:
  - Memory: 65536 KB (64 MB)
  - Iterations: 3
  - Parallelism: 4
  - Salt: 16 bytes (randomly generated)
- Plaintext passwords are never stored or logged

### Data Preservation

When editing a user, any fields not managed by this UI (e.g., future Authelia fields) must be preserved. The backend must:
1. Load the complete user record from YAML
2. Update only the specified fields
3. Write back the complete record with unmanaged fields intact

### File Location

- User database path: `/var/lib/container-apps/halos-core-containers/data/authelia/users_database.yml`
- File permissions: 600 (read/write by root only)
- Backend requires root/sudo access to read and modify the file

## Constraints

### MVP Scope Limitations

- No LDAP or database backend support (file-based YAML only)
- No password policy enforcement in UI (Authelia handles this)
- No user self-service (admin-only operations)
- No bulk operations (single user at a time)

### Logging

- All user operations (create, update, delete, enable/disable) are logged to system journal
- Uses Cockpit's standard logging facility (systemd journal)
- Log entries include: operation type, target username, timestamp
- Password values are never logged (only "password changed" events)

### Technical Constraints

- Must work with Cockpit 276 or later
- Must run on Debian Trixie (arm64 and amd64)
- Backend must handle concurrent access safely (file locking)
- UI must work in both light and dark Cockpit themes

### Security Constraints

- All operations require Cockpit authentication (admin access)
- Password input fields must use appropriate masking
- No password display or retrieval (hashes only, one-way)
- Backend validates all input before processing

## Non-Functional Requirements

### Performance

- User list should load within 2 seconds for up to 100 users
- Individual user operations should complete within 1 second
- UI should remain responsive during backend operations

### Usability

- Follow PatternFly 6 design patterns for consistency with Cockpit
- Provide clear error messages for validation failures
- Confirm destructive operations (delete) before execution
- Show operation success/failure feedback

### Reliability

- Handle missing or malformed user database gracefully
- Validate YAML structure before and after modifications
- Create backup before destructive operations (optional, nice-to-have)

## Out of Scope

- Password reset emails or notifications
- Two-factor authentication management
- Session management or forced logout
- User activity monitoring
- Integration with external identity providers
- Role-based access control within the plugin itself
