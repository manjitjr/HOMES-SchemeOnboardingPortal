# Reject Onboarding Slot Modal

## Purpose

Collect feedback when a reviewer rejects a proposed onboarding slot.

## Trigger

- Reject action from the slot approval area in the scheme detail side panel

## Primary Users

- Agency approvers
- MTO administrators

## Functional Requirements

- The modal must explain that the reviewer can suggest a different slot.
- The modal must provide a multiline feedback field.
- The modal must provide a reject action.
- On successful rejection, the modal must close and the scheme detail screen must refresh.
- The feedback must be displayed on the rejected slot card.

## Business Rules

- Agency approvers can review slot requests while the scheme is in `pending_review`.
- MTO administrators can review slot requests while the scheme is in `pending_final`.
- Rejected slot feedback should guide the creator or approver toward a corrected slot selection.

## API Dependencies

- `POST /api/schemes/{id}/slot/approve`

## Success Criteria

- Slot reviewers can reject and annotate a slot proposal without leaving the scheme workspace.