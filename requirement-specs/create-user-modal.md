# Create User Modal

## Purpose

Allow an MTO administrator to create a new portal user.

## Trigger

- `Create User` button from the user management screen

## Primary Users

- MTO administrators

## Functional Requirements

- The modal must capture username.
- The modal must capture password.
- The modal must capture display name.
- The modal must allow agency selection.
- The modal must allow one or more role selections.
- On successful submission, the modal must close and refresh the user list.

## Validation Rules

- Username is required.
- Password is required.
- Display name is required.
- Agency is required.
- At least one role is required.
- Reserved username `mto_admin` must be rejected by backend rule.

## API Dependencies

- `GET /api/auth/agencies`
- `POST /api/auth/users`

## Success Criteria

- Administrators can provision a new user without leaving the main user management screen.