# Scheme Dashboard Screen

## Purpose

Provide the primary operational dashboard for viewing, filtering, creating, and opening scheme submissions.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Points

- Default landing screen after login
- Header navigation: `Schemes`
- Back action from scheme detail screen

## Functional Requirements

- The screen must display a portal header with role tags, agency tag, and logout action.
- The screen must display KPI cards for total schemes, draft schemes, in-approval schemes, and approved schemes.
- The screen must display a list of schemes returned by the backend.
- Each row must show scheme name, scheme code, agency, status, version, and last updated date.
- Clicking a row must open the selected scheme in the scheme detail screen.
- The screen must provide status filter chips for `all`, `draft`, `pending_review`, `pending_final`, `approved`, and `rejected`.
- The screen must update table content and KPIs when scheme data is loaded.
- The screen must show an empty state when no schemes are available for the selected filter.
- Agency creators must see a `New Scheme` action.
- MTO administrators must see delete actions for each scheme row.

## Permissions

- Agency creators can create schemes.
- Agency approvers can review schemes visible to their agency.
- MTO administrators can view all schemes and delete any scheme.

## Validation And Business Rules

- Filter changes must not require a full page reload.
- Delete must require explicit confirmation through a modal.
- Non-admin users must not be able to trigger deletion.

## API Dependencies

- `GET /api/schemes`
- `DELETE /api/schemes/{id}`

## UI States

- Initial loading state
- Populated table state
- Empty table state
- Backend error state

## Success Criteria

- Users can quickly find a scheme by status and open it for action.