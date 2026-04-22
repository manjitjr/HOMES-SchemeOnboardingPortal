# HOMES Scheme Onboarding Portal Specification

## Purpose

Define the implemented product behavior for the HOMES Scheme Onboarding Portal, including authentication, role-based access, scheme lifecycle management, six setup tabs, approval workflow, slot scheduling, notifications, field guidance, and Excel import/export.
## Requirements
### Requirement: Authentication and session persistence
The system SHALL authenticate users with username and password and persist authenticated session state in browser storage.

#### Scenario: Successful login
- GIVEN a valid username and password
- WHEN the user submits login
- THEN the system returns a JWT token and user profile
- AND the UI stores token and user data in local storage
- AND the user is routed to the authenticated workspace

#### Scenario: Invalid credentials
- GIVEN invalid credentials
- WHEN login is submitted
- THEN the system rejects authentication
- AND the UI displays an error message

#### Scenario: Invalid or expired token during API use
- GIVEN an invalid or expired token
- WHEN the UI calls an authenticated endpoint
- THEN the UI clears local session state
- AND redirects back to login
- AND informs the user to sign in again

### Requirement: Role and agency-based authorization
The system SHALL enforce role and agency restrictions across all protected functionality.

#### Scenario: Agency data scoping
- GIVEN a non-admin user
- WHEN listing schemes or scheduling data
- THEN only records for the user's agency are visible

#### Scenario: Admin data visibility
- GIVEN a user with role mto_admin
- WHEN listing schemes or scheduling data
- THEN records across all agencies are visible

#### Scenario: Administrative operations
- GIVEN a non-admin user
- WHEN attempting user administration or scheme deletion
- THEN access is denied

### Requirement: User management administration
The system SHALL allow MTO administrators to create and manage user accounts.

#### Scenario: Create user
- GIVEN an mto_admin user
- WHEN creating a user with valid username, display name, agency, and roles
- THEN the account is created and appears in the user list

#### Scenario: Role-specific email enforcement
- GIVEN create or update for a user with role agency_approver or mto_admin
- WHEN email is missing
- THEN the operation is rejected

#### Scenario: Reserved admin protections
- GIVEN the reserved mto_admin account
- WHEN attempting prohibited changes (deactivation or loss of admin protection)
- THEN backend guardrails prevent invalid updates

### Requirement: Scheme dashboard operations
The system SHALL provide a dashboard to view, filter, create, open, and (admin-only) delete schemes.

#### Scenario: Status filtering
- GIVEN schemes in multiple states
- WHEN a status chip is selected
- THEN the table and KPI cards reflect the filtered state without page reload

#### Scenario: Create scheme
- GIVEN a user with agency_creator role
- WHEN New Scheme is submitted with required fields
- THEN a draft scheme is created
- AND the user is routed to scheme detail

#### Scenario: Delete scheme
- GIVEN an mto_admin user
- WHEN delete is confirmed
- THEN the scheme is permanently removed

### Requirement: Scheme detail workspace structure
The system SHALL provide one workspace with six functional tabs and shared collaboration controls.

#### Scenario: Tabbed workspace
- GIVEN a selected scheme
- WHEN scheme detail is opened
- THEN the UI presents tabs for:
  - Scheme Overview
  - MT Parameters
  - Transaction Details
  - HOMES Functions
  - MT Bands
  - API & Batch Interfaces

#### Scenario: Collaboration controls
- GIVEN a user with scheme access
- WHEN viewing scheme detail
- THEN comments and change log history are available

### Requirement: Scheme Overview tab behavior
The system SHALL capture overview metadata and background information for each scheme.

#### Scenario: Conditional consent scope
- GIVEN legislated_or_consent value is Consent
- WHEN the overview form is rendered
- THEN consent scope is shown and editable

#### Scenario: Save overview
- GIVEN valid overview form data
- WHEN Save is triggered
- THEN data is persisted to the scheme overview endpoint

### Requirement: MT Parameters tab behavior
The system SHALL capture means-test configuration, including five MTC sections and inclusion/deviation settings.

#### Scenario: MTC section capture
- GIVEN any MTC section (Related, Nuclear, Parent-Guardian, Immediate Family, Free-form)
- WHEN tab data is saved
- THEN used, construct, deviation, and member-status inclusion values are persisted

#### Scenario: Read-only review
- GIVEN a user without edit rights in current status
- WHEN viewing MT Parameters
- THEN values are visible but inputs are non-editable

### Requirement: Transaction Details tab behavior
The system SHALL capture connectivity, interfaces, monthly volume profile, and operational load estimates.

#### Scenario: Monthly and volume capture
- GIVEN transaction details inputs
- WHEN saved
- THEN annual, monthly, reconciliation, and channel volume values are persisted

### Requirement: HOMES Functions tab behavior
The system SHALL capture capability participation and event behavior configuration.

#### Scenario: Event trigger matrix
- GIVEN events EV001 to EV014
- WHEN action values are set
- THEN each event action is independently stored

#### Scenario: Sharing and Auto-MT settings
- GIVEN result sharing and Auto-MT settings
- WHEN saved
- THEN scheme-level sharing and subscription settings are persisted

### Requirement: MT Bands tab behavior
The system SHALL support editing subsidy band definitions and ranking rules.

#### Scenario: Bands and rankings persistence
- GIVEN one or more band/ranking rows
- WHEN saved
- THEN payload stores bands and rankings arrays

#### Scenario: Empty-state handling
- GIVEN no rows
- WHEN viewing MT Bands
- THEN an explicit empty state is shown

### Requirement: API and Batch Interfaces tab behavior
The system SHALL capture per-interface usage and throughput across API, batch, and SFTP items.

#### Scenario: Interface-level configuration
- GIVEN an interface row
- WHEN used/avg/peak fields are edited and saved
- THEN values are persisted independently per row

### Requirement: Scheme workflow lifecycle
The system SHALL enforce workflow transitions and responsibilities across draft, review, and final approval.

#### Scenario: Creator submission
- GIVEN a scheme in draft or rejected
- WHEN agency_creator submits
- THEN status transitions to pending_review

#### Scenario: Agency approval
- GIVEN a scheme in pending_review
- WHEN agency_approver approves
- THEN status transitions to pending_final

#### Scenario: Final approval
- GIVEN a scheme in pending_final
- WHEN mto_admin final-approves
- THEN status transitions to approved

#### Scenario: Rejection with reason
- GIVEN a reviewer in an allowed stage
- WHEN reject is confirmed with reason
- THEN scheme transitions to rejected based on backend workflow rules
- AND rejection comment is recorded

### Requirement: Scheme version lifecycle management
The system SHALL support listing versions, cloning new draft versions, activating approved versions, and retiring active versions.

#### Scenario: List scheme versions
- **WHEN** version listing is requested for a scheme submission
- **THEN** the system returns all versions for the same scheme master in ascending version order

#### Scenario: Clone version
- **WHEN** an agency_creator or mto_admin clones an existing version with a valid date window
- **THEN** the system creates a new draft version with copied tab payloads and clone lineage

#### Scenario: Activate approved version
- **WHEN** an mto_admin activates an approved version
- **THEN** the selected version becomes active
- **AND** any previously active sibling version becomes expired

#### Scenario: Retire active version
- **WHEN** an mto_admin retires an active version
- **THEN** the selected version becomes retired
- **AND** its valid-to date is updated

### Requirement: Workflow action confirmation popup
The UI SHALL require explicit confirmation before submit, approve, and final-approve actions.

#### Scenario: User cancels confirmation
- GIVEN a pending workflow action
- WHEN the user cancels the confirmation modal
- THEN no workflow transition occurs

#### Scenario: User confirms action
- GIVEN a pending workflow action
- WHEN user confirms
- THEN the corresponding workflow endpoint is executed

### Requirement: Workflow notification delivery
The system SHALL trigger workflow notifications to approvers/admins at designated stages.

#### Scenario: Pending review notification
- GIVEN creator submits a scheme
- WHEN status becomes pending_review
- THEN agency approvers for that agency are notification targets

#### Scenario: Pending final notification
- GIVEN agency approver approves a scheme
- WHEN status becomes pending_final
- THEN mto_admin users are notification targets

### Requirement: Notification logging and audit view
The system SHALL persist notification delivery outcomes and expose them to admins.

#### Scenario: Log notification outcome
- GIVEN a workflow notification attempt
- WHEN dispatch completes (sent/skipped/failed)
- THEN a notification log record is stored with recipients and detail

#### Scenario: Admin log visibility
- GIVEN mto_admin user
- WHEN opening Notification Log view
- THEN recent notification logs are listed with status and metadata

### Requirement: Onboarding slot management in scheme detail
The system SHALL allow slot selection and review as part of the scheme detail workflow.

#### Scenario: Creator edits slot in allowed states
- GIVEN scheme status is draft or rejected
- WHEN creator updates primary slot details
- THEN slot data is saved with pending approval status

#### Scenario: Reviewer approves or rejects slot
- GIVEN scheme is in review stage appropriate to reviewer role
- WHEN reviewer approves or rejects slot
- THEN slot approval_status and feedback are updated

#### Scenario: Slot validation rules
- GIVEN slot save request
- WHEN month is invalid, in the past, or go-live dates are before slot month
- THEN request is rejected with validation message

### Requirement: Scheduling calendar overview
The system SHALL provide a quarter-based scheduling view grouped by year.

#### Scenario: Year and quarter overview
- GIVEN selected year
- WHEN scheduling overview is loaded
- THEN bookings are grouped into January, April, July, and November windows

#### Scenario: Agency scoping in scheduling
- GIVEN non-admin user
- WHEN viewing scheduling overview
- THEN only own-agency bookings are visible

### Requirement: Scheduling my-bookings listing
The system SHALL provide a booking list for the current user's visible scope across all slot approval states.

#### Scenario: Include all booking statuses
- **WHEN** my-bookings is requested
- **THEN** the system returns bookings in pending, approved, and rejected states
- **AND** each booking includes scheme, slot, and approver-feedback metadata when available

#### Scenario: Scope bookings by role visibility
- **WHEN** a non-admin user requests my-bookings
- **THEN** only bookings for the user's agency are returned

### Requirement: Field guidance retrieval and administration
The system SHALL provide field-level guidance content to authenticated users and restrict guidance updates to MTO administrators.

#### Scenario: Read guidance content
- **WHEN** guidance is requested globally or for a specific tab and field
- **THEN** the system returns inline hint and popover content for matching guidance records

#### Scenario: Reject non-admin guidance updates
- **WHEN** a non-admin user attempts to update field guidance
- **THEN** the system rejects the operation

#### Scenario: Persist admin guidance updates
- **WHEN** an mto_admin updates field guidance for a tab and field
- **THEN** the system persists the updated guidance content

### Requirement: Single-scheme Excel export
The system SHALL allow exporting an individual scheme workbook.

#### Scenario: Export selected scheme
- GIVEN a user with access to a scheme
- WHEN export is requested for that scheme
- THEN an Excel workbook is generated and downloaded

### Requirement: Bulk Excel export for visible schemes
The system SHALL allow exporting all currently visible schemes in one workbook.

#### Scenario: Admin bulk export
- GIVEN mto_admin user
- WHEN bulk export is triggered
- THEN all schemes are included in workbook sheets:
  - 1. Scheme Overview
  - 2. Scheme MT Parameters
  - 3. Transaction Details
  - 4. HOMES Functions
  - 5. MT Bands
  - 6. API & Batch Interfaces

#### Scenario: Agency user bulk export
- GIVEN non-admin user
- WHEN bulk export is triggered
- THEN only own-agency schemes are included

### Requirement: Excel import with post-import requirement feedback
The system SHALL import schemes from the six-sheet workbook format while returning non-blocking update warnings.

#### Scenario: Import with validation bypass
- GIVEN a valid import workbook
- WHEN import runs
- THEN scheme/tab data is persisted as drafts without blocking on completeness rules

#### Scenario: Post-import warning report
- GIVEN imported rows with missing required details
- WHEN import completes
- THEN response includes per-scheme warnings describing fields still needing updates
- AND UI presents a modal summarizing created/updated/skipped rows and warnings

#### Scenario: Agency-scoped import restriction
- GIVEN a non-admin user importing workbook rows
- WHEN a row targets another agency
- THEN that row is skipped and reported with reason

