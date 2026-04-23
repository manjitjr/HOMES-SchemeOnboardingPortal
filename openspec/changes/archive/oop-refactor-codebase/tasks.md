## 1. Architecture Definition

- [x] 1.1 Identify backend domains that need dedicated classes (workflow, versioning, scheduling, import/export, guidance, notifications)
- [x] 1.2 Define the target responsibilities for routers, service classes, persistence access, and frontend controllers
- [x] 1.3 Confirm preserved public contracts and regression expectations before implementation begins

## 2. Backend Refactor Slices

- [x] 2.1 Extract scheme workflow and version lifecycle logic from `app/routers/schemes.py` into dedicated service classes
- [x] 2.2 Extract import/export and notification-log orchestration into dedicated service classes
- [x] 2.3 Extract scheduling and field-guidance orchestration into dedicated service classes
- [x] 2.4 Keep router handlers limited to auth checks, request parsing, delegation, and response shaping

## 3. Frontend Refactor Slices

- [x] 3.1 Identify feature modules within `app/static/index.html` for auth, schemes list, scheme detail, scheduling, users, notifications, and guidance
- [x] 3.2 Extract one feature slice at a time into controller-style modules or objects with explicit responsibilities
- [x] 3.3 Reduce direct global-state mutation by routing interactions through module boundaries

## 4. Regression Safety

- [x] 4.1 Add or expand regression coverage for workflow, scheduling, import/export, and auth before large refactor slices
- [x] 4.2 Validate preserved API behavior and role-based access after each backend extraction
- [x] 4.3 Validate preserved UI behavior and session handling after each frontend extraction

## 5. Rollout and Review

- [x] 5.1 Deliver the refactor in small domain-focused changes rather than one monolithic rewrite
- [x] 5.2 Run QA and security review on each extracted slice that affects auth, permissions, or file handling
- [x] 5.3 Update OpenSpec tasks and design notes as the architecture plan is refined during implementation
