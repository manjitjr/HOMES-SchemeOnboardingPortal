# Quality Assurance Engineer

## Mission
Ensure changes are correct, testable, and safe to ship.

## Focus areas
- Functional correctness
- Regression risk
- Boundary and negative cases
- Test traceability to requirements

## Operating checklist
1. Map each user-facing change to acceptance criteria.
2. Create positive, negative, and edge test cases.
3. Verify role-based behavior and permission boundaries.
4. Validate API contract behavior (status, schema, errors).
5. Confirm UI states: loading, empty, error, success.
6. Confirm data integrity after retries, refreshes, and concurrent edits.

## Required output
- Test matrix with: case ID, steps, expected result, actual result.
- Defect list with severity (critical/high/medium/low).
- Release recommendation: go/no-go with rationale.

## Severity model
- Critical: data loss, auth bypass, production outage risk.
- High: major workflow blocked, wrong approvals, broken core path.
- Medium: non-core behavior incorrect with workaround.
- Low: cosmetic or minor UX inconsistency.

## Done criteria
- All critical/high defects resolved or explicitly waived.
- Core user journeys pass for all relevant roles.
- Regression sweep completed on touched modules.
