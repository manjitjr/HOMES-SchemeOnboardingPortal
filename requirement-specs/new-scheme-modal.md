# New Scheme Modal

## Purpose

Capture the minimum information required to create a new scheme record in draft mode.

## Trigger

- `New Scheme` button from the scheme dashboard

## Primary Users

- Agency creators

## Functional Requirements

- The modal must allow the user to select an agency.
- The modal must capture scheme full name.
- The modal must capture scheme code.
- The modal must capture legislated or consent selection.
- The modal must capture consent scope.
- The modal must capture background information notes.
- On successful creation, the modal must close and route the user into the new scheme detail screen.
- The created scheme must start in draft mode.

## Validation Rules

- Agency is required.
- Scheme name is required.
- Scheme code is required.
- Legislated or consent is required.

## API Dependencies

- `GET /api/auth/agencies`
- `POST /api/schemes`

## Success Criteria

- A creator can create a new draft and immediately continue editing the full scheme workspace.