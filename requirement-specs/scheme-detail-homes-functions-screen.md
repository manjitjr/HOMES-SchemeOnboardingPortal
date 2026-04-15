# Scheme Detail HOMES Functions Screen

## Purpose

Capture how the scheme will use HOMES capabilities such as MTC visibility, result sharing, affiliations, event triggers, and Auto-MT.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Scheme detail screen, `HOMES Functions` tab

## Functional Requirements

- The screen must capture which MTCs the scheme can view.
- The screen must capture whether other schemes can view this scheme's results.
- The screen must capture whether this scheme can view other schemes' results.
- The screen must capture which MTCs are included in result sharing.
- The screen must capture affiliated schemes and whether MSHL computed results are read.
- The screen must capture event-notification subscription preference.
- The screen must capture beneficiary list scope.
- The screen must present event subscription rows for EV001 through EV014.
- Each event row must support action selection of `Auto-MT them`, `Notify me`, or `Do nothing`.
- The screen must capture Auto-MT subscription and cohort basis.

## Key Data Elements

- View permissions by MTC type
- Result-sharing permissions
- Affiliated schemes notes
- Event trigger actions
- Auto-MT participation flags

## Business Rules

- Event handling selections must be independently configurable.
- The screen must remain usable as a review-only matrix for approvers and admins.

## API Dependencies

- `PUT /api/schemes/{id}/tab/homes_functions`

## UI States

- Editable matrix state
- Read-only matrix state

## Success Criteria

- Stakeholders can verify how the scheme participates in HOMES ecosystem functions and event-driven behavior.