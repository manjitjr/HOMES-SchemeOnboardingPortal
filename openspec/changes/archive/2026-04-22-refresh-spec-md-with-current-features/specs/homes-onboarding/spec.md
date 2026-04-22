## MODIFIED Requirements

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
