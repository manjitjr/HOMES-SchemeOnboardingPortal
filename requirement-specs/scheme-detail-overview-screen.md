# Scheme Detail Overview Screen

## Purpose

Provide the main scheme workspace, including the overview form, workflow controls, comments, change log, and slot-selection side panel.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Points

- Selecting a scheme from the scheme dashboard
- Returning to an in-progress scheme after creation

## Functional Requirements

- The screen must show the selected scheme title, current status badge, and a back-to-dashboard action.
- The screen must display top summary cards for scheme name, agency, version, and status.
- The screen must show six tabs for the scheme setup lifecycle.
- The screen must render the `Scheme Overview` tab as the default active tab.
- The overview form must support editing of agency, scheme name, scheme code, legislated or consent selection, consent scope, and background information.
- Consent scope must only be visible when `Legislated or Consent` is set to `Consent`.
- The screen must show save controls when the user has edit rights.
- Agency creators in `draft` or `rejected` status must see draft save and submit actions.
- Agency approvers in `pending_review` must see approve and reject actions.
- MTO administrators in `pending_final` must see final approve and reject actions.
- The screen must show an onboarding slot panel in the right rail.
- The screen must show comments with add-comment capability.
- The screen must show a change log with a toggle between current-screen changes and all-screen changes.

## Overview Form Fields

- Agency
- Full Name of Scheme/Fund
- Scheme Code
- Legislated or Consent
- Consent Scope
- Organisation which established the fund or scheme
- Purpose of fund or scheme
- Source of funding
- Governing body
- Organisation setting eligibility criteria
- Organisations evaluating applications
- Third parties receiving data
- Group schemes name
- Scheme logo info

## Permissions

- `agency_creator` can edit when status is `draft` or `rejected`.
- `agency_approver` can edit when status is `pending_review` or `rejected`.
- `mto_admin` can edit regardless of workflow state in the current implementation.

## Validation And Business Rules

- Save tab must persist overview data to the scheme overview endpoint.
- Submit for review must transition a draft or rejected scheme into approval flow.
- Reject actions must require a reason via modal.
- Comments are independent of form save and must be postable at any time by an authenticated user with access.

## API Dependencies

- `GET /api/schemes/{id}`
- `PUT /api/schemes/{id}`
- `GET /api/schemes/{id}/comments`
- `POST /api/schemes/{id}/comments`
- `GET /api/schemes/{id}/changes`
- `POST /api/schemes/{id}/submit`
- `POST /api/schemes/{id}/approve`
- `POST /api/schemes/{id}/final-approve`
- `POST /api/schemes/{id}/reject`
- `PUT /api/schemes/{id}/slot`
- `POST /api/schemes/{id}/slot/approve`

## UI States

- Loading scheme state
- Editable state
- Read-only state
- Draft banner state
- Rejected-with-feedback state

## Success Criteria

- Users can maintain the overview content, collaborate through comments, and move the scheme through workflow without leaving the screen.