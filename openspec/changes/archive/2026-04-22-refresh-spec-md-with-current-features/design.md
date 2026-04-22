## Context

This is a specification-alignment change rather than a product implementation change. The repository already contains behavior for scheme version lifecycle management, scheduling booking list retrieval, and field guidance administration, but those behaviors were missing from the baseline OpenSpec specification. The goal is to document existing behavior accurately without expanding scope beyond what is already implemented.

## Goals / Non-Goals

**Goals:**
- Bring OpenSpec requirements into parity with implemented backend and frontend behavior.
- Capture missing requirements in a way that QA, security review, and future change proposals can reference.
- Keep all updates within the existing `homes-onboarding` capability rather than fragmenting the baseline spec unnecessarily.

**Non-Goals:**
- Do not introduce new runtime behavior.
- Do not refactor application code.
- Do not redefine existing requirements that are already accurate.

## Decisions

### Decision: Treat this as a modification to the existing capability
The missing behavior belongs to the same product surface already covered by `homes-onboarding`.

**Rationale:**
- The missing requirements are part of the current authenticated workflow and not separate product domains.
- Keeping them in one capability avoids splitting a cohesive portal spec into artificial sub-capabilities.

**Alternatives considered:**
- Create separate capabilities for scheduling, guidance, and versioning.
- Rejected because the baseline spec is already organized as one integrated portal capability and this change is documentation synchronization, not domain decomposition.

### Decision: Add new requirements instead of modifying unrelated existing ones
The missing features are additive and do not materially alter the meaning of previously captured requirements.

**Rationale:**
- Delta specs stay easier to audit when only the newly documented behavior is added.
- Archive behavior remains clear because no existing requirement text needs wholesale replacement.

**Alternatives considered:**
- Expand existing scheduling/workflow requirements under MODIFIED sections.
- Rejected because the net change is clearer as additive requirements.

### Decision: Reference implemented routes and UI behavior as the review source of truth
The design uses current router and UI behavior to define the spec update boundary.

**Rationale:**
- Product documentation should reflect shipped behavior when the task is a sync review.
- Backend routes and UI surfaces provide the most concrete evidence for the update.

## Risks / Trade-offs

- [Risk] Future implementation may drift again after this sync -> Mitigation: keep OpenSpec update tasks in the change checklist for feature work.
- [Risk] Single-capability spec may grow large over time -> Mitigation: defer capability splitting until a future change explicitly reorganizes the spec structure.
- [Risk] Readers may confuse documentation sync with feature delivery -> Mitigation: proposal and tasks explicitly state that scope is spec parity only.

## Migration Plan

1. Create proposal, design, delta spec, and tasks for the documentation sync change.
2. Update the baseline `openspec/specs/homes-onboarding/spec.md` to include the missing requirements.
3. Validate artifact completeness through OpenSpec status checks.
4. Archive the change once stakeholders accept that the baseline spec matches the current implementation.

Rollback strategy:
- Revert the OpenSpec files for this change and restore the previous baseline spec if the review identifies that the documented behavior should not be considered committed product behavior.

## Open Questions

- Should the long-term OpenSpec structure remain a single `homes-onboarding` capability, or should it later be decomposed by domain such as auth, workflow, scheduling, and import/export?
- Should future Product Manager-led reviews require delta specs before any baseline spec edits to keep change history stricter?
