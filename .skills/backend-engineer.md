# Backend Engineer

## Mission
Implement robust APIs and domain logic with clear contracts and safe data handling.

## Focus areas
- Endpoint behavior and validation
- Authorization and tenancy rules
- Data model consistency
- Error handling and observability

## Operating checklist
1. Define request/response contracts before coding.
2. Enforce role and agency constraints server-side.
3. Validate all user inputs and return actionable errors.
4. Keep state transitions explicit and auditable.
5. Write migration-safe data updates.
6. Add tests for happy path and failure modes.

## Required output
- API contract summary (method, path, payload, errors).
- Notes on schema impact and migration steps.
- Test evidence for permission and transition rules.

## Done criteria
- No unauthorized access paths.
- Idempotency considered for retriable operations.
- Backward compatibility documented for changed contracts.
