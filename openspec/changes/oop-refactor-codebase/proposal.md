## Why

The current codebase is heavily procedural in key areas, with large router modules and a single-file frontend carrying workflow, validation, and view logic in one place. Refactoring toward object-oriented design will improve maintainability, testability, and separation of concerns before additional feature growth makes the code harder to evolve safely.

## What Changes

- Introduce object-oriented service and domain-layer abstractions for scheme workflow, versioning, scheduling, guidance, notifications, and import/export behavior.
- Extract business rules from large router functions into cohesive classes with clearer responsibilities.
- Refactor frontend screen and state logic into modular objects or controller-style units where practical, reducing the monolithic behavior in `app/static/index.html`.
- Preserve existing product behavior, API contracts, and role-based access rules during the refactor.
- Add regression validation around the refactored flows to ensure behavior remains unchanged.

## Capabilities

### New Capabilities
- `codebase-architecture`: Defines maintainability and object-oriented structure requirements for backend services, router boundaries, and frontend module decomposition while preserving existing behavior.

### Modified Capabilities
- None. This proposal targets internal architecture and maintainability rather than changing existing user-facing capability contracts.

## Impact

- Backend modules:
  - `app/routers/schemes.py`
  - `app/routers/scheduling.py`
  - `app/routers/guidance.py`
  - `app/auth.py`
  - `app/services/notifications.py`
- Potential new backend packages for domain services, coordinators, or managers under `app/services/` or adjacent modules
- Frontend module currently concentrated in:
  - `app/static/index.html`
- QA impact:
  - existing core workflows need regression verification across auth, scheme editing, workflow approvals, scheduling, notifications, and import/export
- Security impact:
  - role enforcement and agency scoping must remain unchanged after responsibility extraction
