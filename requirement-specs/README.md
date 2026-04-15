# HOMES Onboarding Portal Screen Requirements

This folder contains requirement specifications for each implemented screen in the HOMES Scheme Onboarding Portal.

## Scope

The specifications are based on the current FastAPI backend and the SPA implemented in `app/static/index.html`.

## Primary Screens

- `login-screen.md`
- `scheme-dashboard-screen.md`
- `scheme-detail-overview-screen.md`
- `scheme-detail-mt-parameters-screen.md`
- `scheme-detail-transaction-details-screen.md`
- `scheme-detail-homes-functions-screen.md`
- `scheme-detail-mt-bands-screen.md`
- `scheme-detail-api-batch-interfaces-screen.md`
- `onboarding-calendar-screen.md`
- `user-management-screen.md`

## Modal Interaction Screens

- `new-scheme-modal.md`
- `create-user-modal.md`
- `edit-user-modal.md`
- `reject-scheme-modal.md`
- `reject-onboarding-slot-modal.md`
- `delete-scheme-confirmation-modal.md`

## Role Model Used In These Specs

- `agency_creator`: creates and edits own-agency scheme records while in draft or rejected status.
- `agency_approver`: reviews own-agency submissions, approves to MTO, rejects with comments, and reviews slot requests.
- `mto_admin`: final approver across agencies, user administrator, and deletion authority.

## Status Model Used In These Specs

- `draft`
- `pending_review`
- `pending_final`
- `approved`
- `rejected`

## Notes

- The detailed scheme workspace is a single screen with six functional tabs. Each tab has its own requirement file because each tab behaves like a separate form surface with distinct validation and data dependencies.
- Slot selection and approval are embedded in the scheme detail screen but are also covered in the rejection modal specification because that is a distinct user interaction surface.