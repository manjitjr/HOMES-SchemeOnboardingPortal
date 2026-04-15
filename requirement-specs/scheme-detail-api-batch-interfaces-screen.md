# Scheme Detail API And Batch Interfaces Screen

## Purpose

Capture detailed interface usage, throughput expectations, and SFTP setup decisions across supported HOMES APIs and batch jobs.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Point

- Scheme detail screen, `API & Batch Interfaces` tab

## Functional Requirements

- The screen must display a table of API interfaces with interface number, name, used flag, average calls per hour, and peak calls per hour.
- The screen must display a table of batch interfaces with interface number, name, used flag, average records per day, and peak records per day.
- The screen must display individual Yes or No selectors for each required SFTP setup item.
- All interface rows must be visible in a single review surface.
- The screen must support read-only review and editable maintenance modes.

## Included Interface Groups

- P12 and P20 APIs
- P13 and P20 batch interfaces
- Supporting-document and report-delivery SFTP setups

## Business Rules

- Each interface entry is independently configurable.
- Numeric throughput fields must accept numeric input only.
- Read-only users must still be able to review every interface line item.

## API Dependencies

- `PUT /api/schemes/{id}/tab/api_interfaces`

## UI States

- Editable matrix state
- Read-only matrix state

## Success Criteria

- Technical teams can confirm the exact integration footprint and expected load characteristics for every relevant interface.