# User Management Screen

## Purpose

Allow MTO administrators to manage portal users, agency assignments, roles, and account activation.

## Primary Users

- MTO administrators only

## Entry Point

- Header navigation: `User Management`

## Functional Requirements

- The screen must show KPI cards for total users, active users, creators, and approvers.
- The screen must provide search by display name, username, agency, or role.
- The screen must provide agency, role, and status filters.
- The screen must provide a reset action that clears all filters.
- The screen must list users in a scrollable table with sticky headers.
- Each user row must show display name, username, agency, roles, and account status.
- Each user row must provide edit and activate or deactivate actions.
- The screen must provide a `Create User` action.
- The screen must show a helpful empty state when no users match the current filters.

## Permissions

- Only MTO administrators can access the page and its actions.

## Business Rules

- Search and filters must apply client-side to the loaded dataset.
- The `mto_admin` user cannot have the MTO admin role removed and cannot be deactivated by backend rule.
- Activation and deactivation must take effect immediately after successful update.

## API Dependencies

- `GET /api/auth/agencies`
- `GET /api/auth/users`
- `POST /api/auth/users`
- `PUT /api/auth/users/{id}`

## UI States

- Initial loading state
- Filtered list state
- Empty results state
- Error state

## Success Criteria

- Administrators can manage the portal user base from a single operational screen without direct database access.