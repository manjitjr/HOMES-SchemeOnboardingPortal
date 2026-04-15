# Scheme Detail MT Parameters Screen

## Purpose

Capture means-testing configuration for beneficiaries, applicants, MTC structures, income components, and property settings.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Scheme detail screen, `MT Parameters` tab

## Functional Requirements

- The screen must display beneficiary and applicant relationship fields.
- The screen must display beneficiary residence status and foreigner pass type inputs.
- The screen must render collapsible sections for the five MTC types:
  - Related
  - Nuclear
  - Parent-Guardian
  - Immediate Family
  - Free-form
- Each MTC section must include whether the MTC is used, whose construct it follows, a standardised member-status grid, and whether deviation is allowed.
- The screen must capture income component usage for employment, trade, investments, and rental.
- The screen must capture the income rollup model.
- The screen must capture property usage settings for annual value and market price.
- The screen must support save behavior through the shared tab-save action.

## Key Data Elements

- Same person as applicant
- Relationship description
- Beneficiary residence status
- Foreigner pass types
- MTC usage per type
- MTC construct per type
- Deviation flag per type
- Income component flags
- Income rollup
- Annual value usage
- Market price usage

## Business Rules

- Member status options are informational and standardised across schemes.
- Users without edit rights must see the tab in read-only mode.
- Save must persist the tab payload as structured JSON.

## API Dependencies

- `PUT /api/schemes/{id}/tab/mt_parameters`

## UI States

- Editable form state
- Read-only review state
- Collapsed and expanded MTC section states

## Success Criteria

- Reviewers can understand exactly how the scheme defines its means-testing construct and supporting inputs.