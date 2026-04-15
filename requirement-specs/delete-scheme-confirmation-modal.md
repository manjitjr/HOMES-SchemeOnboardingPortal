# Delete Scheme Confirmation Modal

## Purpose

Require explicit confirmation before permanently deleting a scheme.

## Trigger

- Delete action from the scheme dashboard
- Delete action from the onboarding calendar screen

## Primary Users

- MTO administrators only

## Functional Requirements

- The modal must state that deletion is permanent.
- The modal must identify the scheme being deleted.
- The modal must provide cancel and confirm actions.
- On successful deletion, the modal must close and the source screen must refresh.

## Business Rules

- Only MTO administrators may delete schemes.
- Deletion is irreversible from the user interface.
- The same confirmation pattern must be used from both dashboard and schedule contexts.

## API Dependencies

- `DELETE /api/schemes/{id}`

## Success Criteria

- Permanent deletion is always deliberate and role-restricted.