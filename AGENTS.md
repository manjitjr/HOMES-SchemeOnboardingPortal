# Agent Roles

Use this file to select role behavior per task by importing skill content from the .skills folder.

## Skill references
- .skills/product-manager.md
- .skills/quality-assurance-engineer.md
- .skills/backend-engineer.md
- .skills/frontend-engineer.md
- .skills/security-engineer.md
- .skills/release-engineer.md

## Suggested usage

For feature implementation tasks:
- Primary: Product Manager (coordination)
- Delivery lead: Backend Engineer or Frontend Engineer
- Secondary reviewer: Quality Assurance Engineer

For multi-team or cross-surface tasks:
- Primary: Product Manager
- Primary: Backend Engineer or Frontend Engineer
- Supporting roles: Backend Engineer, Frontend Engineer, Quality Assurance Engineer

For release readiness tasks:
- Primary: Release Engineer
- Secondary reviewer: Security Engineer and Quality Assurance Engineer

## Example assignment block

Task: Implement and verify Excel import warning behavior.

Primary role:
- Product Manager

Delivery lead:
- Backend Engineer

Supporting roles:
- Frontend Engineer
- Quality Assurance Engineer
- Security Engineer

## Team policy
- Every task must have one primary role.
- Product Manager is recommended as primary role when work requires coordination across multiple engineers.
- Every code change must include QA acceptance checks.
- Any auth, file import, or permission change must include Security review.
