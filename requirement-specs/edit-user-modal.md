# Edit User Modal

## Purpose

Allow an MTO administrator to modify an existing user’s profile, agency, roles, password, and active status.

## Trigger

- Edit action on a user row in the user management screen

## Primary Users

- MTO administrators

## Functional Requirements

- The modal must display the selected user’s current display name.
- The modal must allow updating display name.
- The modal must allow changing agency.
- The modal must allow setting a new password.
- The modal must allow role selection changes.
- The modal must allow toggling active status.
- On successful save, the modal must close and refresh the user list.

## Validation Rules

- Display name is required.
- Agency is required.
- At least one role is required when roles are submitted.
- Backend rules must prevent deactivation of the reserved `mto_admin` account.
- Backend rules must prevent removing the `mto_admin` role from the reserved `mto_admin` account.

## API Dependencies

- `GET /api/auth/agencies`
- `PUT /api/auth/users/{id}`

## Success Criteria

- Administrators can maintain account access and role hygiene without navigating away from the user table.