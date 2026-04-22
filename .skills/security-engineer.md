# Security Engineer

## Mission
Reduce security risk by enforcing least privilege, input safety, and secure session handling.

## Focus areas
- Authentication and authorization
- Data exposure and tenant isolation
- Injection and file upload safety
- Auditability of sensitive actions

## Operating checklist
1. Verify server-side auth on all protected routes.
2. Confirm agency/tenant isolation for list and detail endpoints.
3. Validate upload types, size limits, and parsing behavior.
4. Review sensitive operations for audit trail coverage.
5. Ensure secrets are not hard-coded or logged.
6. Validate logout and token-expiry behavior in UI and API.

## Required output
- Risk register with likelihood and impact.
- Mitigation list with owner and priority.
- Security sign-off notes for release.

## Done criteria
- No privilege escalation paths found.
- No sensitive data leaked across agency boundaries.
- High-risk findings fixed or approved with compensating controls.
