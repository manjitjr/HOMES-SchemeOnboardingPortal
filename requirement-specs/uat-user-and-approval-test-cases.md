# UAT Test Cases: Users, Change Confirmation Popup, and Approval Notifications

## Scope

This UAT suite covers:
- User management (create, update, role/agency/email validation)
- Scheme action confirmation popup with saved change summary
- Notification emails for Pending Review and Pending Final workflow stages

## Preconditions

- Application is running locally on http://localhost:8000
- Test users exist for at least one agency:
  - Agency Creator
  - Agency Approver
  - MTO Admin
- SMTP settings are configured in `.env` for end-to-end email delivery checks:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USERNAME` (if required)
  - `SMTP_PASSWORD` (if required)
  - `SMTP_USE_TLS`
  - `SMTP_SENDER`

## Test Data

- Scheme A (MOH)
- Scheme B (MSE)
- User accounts with valid email addresses
- One account per role with missing email for negative checks

## Test Cases

### User Management

1. UAT-USER-001: Create user with creator role and optional email
- Steps:
  - Login as MTO Admin
  - Open User Management
  - Create user with role `agency_creator` and valid agency
  - Leave email empty
- Expected:
  - User is created successfully
  - User appears in list with email shown as `-`

2. UAT-USER-002: Create approver without email should fail
- Steps:
  - Login as MTO Admin
  - Create user with role `agency_approver` and no email
- Expected:
  - API rejects request with validation error
  - Message indicates email is required for approver/admin roles

3. UAT-USER-003: Create approver with valid email
- Steps:
  - Login as MTO Admin
  - Create user with `agency_approver` role and unique email
- Expected:
  - User is created
  - Email is displayed in user table

4. UAT-USER-004: Update user email to duplicate should fail
- Steps:
  - Login as MTO Admin
  - Edit user and set email to an existing user's email
- Expected:
  - Validation error returned
  - No update saved

5. UAT-USER-005: Remove email from existing mto_admin should fail
- Steps:
  - Login as MTO Admin
  - Edit an `mto_admin` user and clear email
- Expected:
  - Validation error returned (email required for admin role)

### Change Confirmation Popup

6. UAT-WORKFLOW-001: Submit for Review shows confirmation popup
- Steps:
  - Login as Agency Creator
  - Open draft scheme, save at least one tab change
  - Click `Submit for Review`
- Expected:
  - Popup appears with title confirming submit action
  - Popup lists recent saved changes (field-level old/new)
  - Cancel closes popup with no workflow status change

7. UAT-WORKFLOW-002: Approve & Send to MTO shows confirmation popup
- Steps:
  - Login as Agency Approver
  - Open `pending_review` scheme
  - Click `Approve & Send to MTO`
- Expected:
  - Popup appears with change summary and action details
  - Confirm proceeds and status changes to `pending_final`

8. UAT-WORKFLOW-003: Final Approve shows confirmation popup
- Steps:
  - Login as MTO Admin
  - Open `pending_final` scheme
  - Click `Final Approve`
- Expected:
  - Popup appears with change summary
  - Confirm proceeds and status becomes `approved`

9. UAT-WORKFLOW-004: Popup when no saved change history
- Steps:
  - Open scheme with minimal/no audited changes
  - Trigger workflow confirmation popup
- Expected:
  - Popup displays fallback note indicating no saved change log entries
  - User can still proceed or cancel

### Notification Emails

10. UAT-NOTIF-001: Pending Review email goes to agency approvers only
- Steps:
  - Ensure MOH has two active approvers with emails
  - Submit MOH draft scheme as MOH creator
- Expected:
  - Emails sent to active MOH approver email addresses only
  - Other agency approvers do not receive this email

11. UAT-NOTIF-002: Pending Final email goes to MTO admins only
- Steps:
  - Approve `pending_review` scheme as agency approver
- Expected:
  - Emails sent to active MTO Admin email addresses
  - Agency approvers do not receive this email

12. UAT-NOTIF-003: Users without email are skipped safely
- Steps:
  - Keep one approver/admin without email
  - Trigger corresponding workflow transition
- Expected:
  - Workflow transition succeeds
  - Email attempt does not fail request
  - Missing-email user is skipped

13. UAT-NOTIF-004: SMTP not configured fallback behavior
- Steps:
  - Remove `SMTP_HOST` from environment
  - Trigger submit/approve transition
- Expected:
  - Workflow transition succeeds
  - App logs notification skipped message
  - No runtime exception shown to end user

## Exit Criteria

- All critical cases (workflow + notification routing + validation) pass
- No regressions in user management CRUD
- No blocking errors in submit/approve/final-approve flows
