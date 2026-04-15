# Reject Scheme Modal

## Purpose

Collect a rejection reason when an approver or MTO administrator sends a scheme back in the workflow.

## Trigger

- Reject action from the scheme detail approval panel

## Primary Users

- Agency approvers
- MTO administrators

## Functional Requirements

- The modal must explain who the scheme will be sent back to.
- The modal must provide a multiline rejection reason field.
- The modal must allow the user to confirm the rejection.
- On successful rejection, the modal must close and the scheme detail screen must refresh.
- The rejection comment must be visible later in the scheme’s collaborative review context.

## Business Rules

- Agency approver rejection returns the scheme to the creator.
- MTO admin rejection returns the scheme to the agency approver.
- The workflow status after rejection must be controlled by backend rules.

## API Dependencies

- `POST /api/schemes/{id}/reject`

## Success Criteria

- Reviewers can reject a scheme with actionable feedback and preserve a traceable reason.