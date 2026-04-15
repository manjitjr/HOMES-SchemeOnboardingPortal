# Onboarding Calendar Screen

## Purpose

Provide a visual quarter-based calendar of onboarding bookings for approved scheme go-live commitments.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Header navigation: `Scheduling`

## Functional Requirements

- The screen must display a year selector for the current year and the next two years.
- The screen must retrieve and render quarterly booking data for the selected year.
- The screen must display four quarter columns representing January, April, July, and November onboarding windows.
- Each quarter column must show booking count and any booked schemes.
- Each booking card must show scheme name, agency, technical go-live date, and business go-live date.
- The screen must display a summary badge showing total bookings and the number of filled onboarding windows.
- MTO administrators must be able to delete a scheme directly from a booking card via a confirmation modal.

## Permissions

- All authenticated users can view the calendar.
- Only MTO administrators can delete schemes from this view.

## Business Rules

- Empty quarters must display a `No bookings` state.
- Year changes must refresh the displayed calendar without a full page reload.
- Admin deletion from the calendar must call the same scheme deletion flow used elsewhere.

## API Dependencies

- `GET /api/scheduling/overview/{year}`
- `DELETE /api/schemes/{id}`

## UI States

- Loading state
- Populated quarter state
- Empty quarter state
- Error state

## Success Criteria

- Stakeholders can assess onboarding load distribution for each quarter of a selected year in one glance.