# Scheme Detail Transaction Details Screen

## Purpose

Capture how the scheme will connect to HOMES, the interfacing systems involved, and the expected transaction and volume profile.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Scheme detail screen, `Transaction Details` tab

## Functional Requirements

- The screen must capture whether the scheme uses HOMES portal access through CorpPass and Intranet.
- The screen must capture number of organisations for each portal mode.
- The screen must capture whether Batch SFTP and real-time APEX API are used.
- The screen must capture scheduled report delivery mode and required report details.
- The screen must capture intranet and internet interface system counts for SFTP and API.
- The screen must capture interface status and estimated ready date.
- The screen must capture names of interfacing systems.
- The screen must capture annual means-test application volume.
- The screen must capture monthly breakdown values for all twelve months.
- The screen must capture manual reconciliation percentage and max concurrent users per hour.
- The screen must capture reconciliation breakdown notes.
- The screen must capture peak and average volumes for SFTP, API, Portal, and Bulk Query.

## Key Data Elements

- Portal access flags
- Organisation counts
- Batch and real-time integration flags
- Scheduled report handling
- Interface readiness
- Load and traffic estimates

## Business Rules

- Numeric inputs must accept numeric data only.
- Date input must use a date picker.
- The monthly breakdown must support partial completion.
- Read-only permissions must disable editing without hiding values.

## API Dependencies

- `PUT /api/schemes/{id}/tab/transactions`

## UI States

- Editable form state
- Read-only review state

## Success Criteria

- Technical reviewers can assess integration readiness, traffic expectations, and operational dependency footprint from a single tab.