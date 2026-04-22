## Context

The HOMES onboarding portal currently concentrates major application behavior in a few large procedural modules: `app/routers/schemes.py` is 1781 lines and `app/static/index.html` is 3514 lines, with workflow, validation, import/export, notification, scheduling, and screen state logic mixed together. The system works, but feature growth now increases the cost of change because responsibilities are not isolated behind cohesive objects or service boundaries.

## Goals / Non-Goals

**Goals:**
- Introduce an object-oriented structure for major business domains without changing user-visible behavior.
- Reduce router responsibility by moving workflow, versioning, scheduling, import/export, and guidance logic into dedicated classes.
- Define clear collaboration boundaries between data access, domain rules, orchestration, and presentation logic.
- Make core behaviors easier to test independently from FastAPI route handlers and monolithic frontend rendering code.

**Non-Goals:**
- Do not redesign the product workflow or change API contracts as part of this initial refactor.
- Do not replace the frontend framework or migrate away from the existing single-page architecture in one step.
- Do not introduce speculative abstractions for domains that have minimal logic.

## Decisions

### Decision: Introduce service-layer classes for backend domain orchestration
Domain-heavy route logic will move into classes such as `SchemeWorkflowService`, `SchemeVersionService`, `SchemeImportExportService`, `SchedulingService`, and `FieldGuidanceService`.

**Rationale:**
- Router functions should focus on request/response handling, authorization entry checks, and dependency wiring.
- Domain classes make business rules independently testable and easier to reuse.

**Alternatives considered:**
- Keep procedural helper functions inside routers.
- Rejected because current modules already show scale problems and weak cohesion.

### Decision: Keep SQLAlchemy models as persistence models, not domain-service containers
The refactor will not push business logic into ORM models beyond lightweight model helpers.

**Rationale:**
- The codebase already uses routers + sessions in a service-oriented backend shape.
- Service classes are a lower-risk path than active-record style model methods for async database workflows.

**Alternatives considered:**
- Rich domain models with behavior on ORM entities.
- Rejected because async session boundaries and current persistence setup make that migration riskier.

### Decision: Introduce frontend controller/module objects incrementally
Frontend logic in `app/static/index.html` will be decomposed into object-like modules or controllers by concern, such as auth/session, scheme list, scheme detail workflow, scheduling, user management, and guidance.

**Rationale:**
- A full framework migration is out of scope, but structured objects can still reduce global-state sprawl.
- Incremental extraction preserves existing UI behavior while improving readability and testability.

**Alternatives considered:**
- Rewrite the frontend into a new framework.
- Rejected because it is too large a simultaneous change for an architecture refactor.

### Decision: Preserve public contracts during the first refactor phase
Existing endpoints, request/response shapes, role checks, and major UI flows remain stable while internals are reorganized.

**Rationale:**
- Refactoring should minimize product and deployment risk.
- QA and security validation can compare old and new behavior more easily when contracts remain stable.

## Risks / Trade-offs

- [Risk] The refactor could introduce subtle workflow regressions while preserving the same endpoints -> Mitigation: add regression tests around workflow, scheduling, import/export, and auth before and during extraction.
- [Risk] Too many new classes may create unnecessary indirection -> Mitigation: only extract domains with significant orchestration logic and keep simple concerns procedural where appropriate.
- [Risk] Frontend extraction from a single HTML file may stall halfway and leave mixed patterns -> Mitigation: refactor by feature slice, with one ownership boundary per pass.
- [Risk] Security rules may drift during service extraction -> Mitigation: keep authorization checks explicit at router entry points and add security review for every moved permission rule.

## Migration Plan

1. Define the target architecture and service boundaries in OpenSpec.
2. Extract backend domains one slice at a time, starting with the highest-complexity modules.
3. Add or expand regression coverage around each extracted slice before large moves.
4. Extract frontend behavior into module/controller objects without changing UI contracts.
5. Validate parity after each slice and deploy incrementally.

Rollback strategy:
- Revert the latest slice-level refactor commit if behavior changes unexpectedly.
- Keep refactors isolated by domain so rollback remains narrow.

## Open Questions

- Which backend domain should be extracted first: workflow/versioning, import/export, or scheduling?
- Should frontend decomposition remain in one file initially or move to multiple static JS files as part of the same change?
- What minimum regression suite is required before starting the first extraction slice?
