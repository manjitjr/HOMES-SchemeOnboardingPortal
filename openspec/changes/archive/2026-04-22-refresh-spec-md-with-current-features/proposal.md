## Why

The current OpenSpec baseline did not fully reflect implemented product behavior in the codebase, which leaves version lifecycle, scheduling booking lists, and field-guidance administration under-specified. This change brings the documented contract back in sync with shipped behavior so future work, QA, and change reviews can rely on OpenSpec as the source of truth.

## What Changes

- Update the existing `homes-onboarding` capability spec to include scheme version lifecycle behavior.
- Update the existing `homes-onboarding` capability spec to include scheduling `my-bookings` behavior and role scoping.
- Update the existing `homes-onboarding` capability spec to include field guidance retrieval and admin update behavior.
- Capture the documentation-sync design and task plan for maintaining spec parity with implemented features.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `homes-onboarding`: Expand the current requirements to cover version lifecycle operations, booking list behavior, and field guidance administration already present in the application.

## Impact

- OpenSpec baseline: `openspec/specs/homes-onboarding/spec.md`
- OpenSpec change artifacts under `openspec/changes/refresh-spec-md-with-current-features/`
- Referenced implementation surfaces:
  - `app/routers/schemes.py`
  - `app/routers/scheduling.py`
  - `app/routers/guidance.py`
  - `app/static/index.html`
