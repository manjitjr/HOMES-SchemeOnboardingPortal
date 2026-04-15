# Scheme Detail MT Bands Screen

## Purpose

Capture subsidy band configuration and subsidy ranking rules for the scheme.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Scheme detail screen, `MT Bands` tab

## Functional Requirements

- The screen must display a tabular editor for subsidy bands.
- Users with edit rights must be able to add a new subsidy band row.
- Users with edit rights must be able to delete an existing subsidy band row.
- Each band row must capture MTC type, rollup, effective start date, effective end date, income range, annual value range, multi-property flag, ID type, band name, near-margin buffer, and display labels.
- The screen must display a second tabular editor for subsidy ranking.
- Users with edit rights must be able to add and remove ranking rows.
- Each ranking row must capture effective date range, subsidy band, and ranking order.
- Empty tables must show a clear no-data state.

## Key Data Elements

- Band definitions
- Income and AV thresholds
- Effective dates
- Ranking sequence

## Business Rules

- The tab payload must store `bands` and `rankings` as arrays.
- Read-only users must not see add or delete controls.
- Date and numeric fields must use appropriate HTML input types.

## API Dependencies

- `PUT /api/schemes/{id}/tab/mt_bands`

## UI States

- Empty table state
- Editable table state
- Read-only table state

## Success Criteria

- Policy reviewers can inspect the scheme’s subsidy logic without exporting to an external spreadsheet.