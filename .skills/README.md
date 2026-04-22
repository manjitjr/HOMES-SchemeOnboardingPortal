# Skill Library

This folder stores reusable role skills for agent workflows.

## How to use in AGENTS.md

1. Reference one or more skill files by relative path.
2. Copy the sections you need into your active agent instructions.
3. Keep role scope narrow and outcome-oriented.

Example references:
- .skills/product-manager.md
- .skills/quality-assurance-engineer.md
- .skills/backend-engineer.md
- .skills/frontend-engineer.md
- .skills/security-engineer.md
- .skills/release-engineer.md

## Recommended pattern

For each task, pick one primary role and one supporting role:
- Primary role drives decisions and acceptance criteria.
- Supporting role reviews risks and edge cases.

## Maintenance rules

- Keep each skill file under 200 lines.
- Prefer checklists over prose.
- Update acceptance criteria when the product behavior changes.
- Add role-specific test strategy for every new feature area.
