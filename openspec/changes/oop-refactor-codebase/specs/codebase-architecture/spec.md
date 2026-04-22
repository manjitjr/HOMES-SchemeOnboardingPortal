## ADDED Requirements

### Requirement: Backend domain orchestration shall be encapsulated in dedicated classes
The codebase SHALL encapsulate business orchestration for major backend domains in dedicated classes rather than leaving it embedded in route handlers.

#### Scenario: Route handler delegates domain logic
- **WHEN** a route performs workflow, versioning, scheduling, import/export, notification, or guidance orchestration
- **THEN** the route delegates that orchestration to a dedicated class or object with a focused responsibility

#### Scenario: Domain logic remains testable outside HTTP routing
- **WHEN** a backend domain class is implemented
- **THEN** its core behavior can be tested without requiring direct invocation of FastAPI route functions

### Requirement: Router modules shall remain thin integration boundaries
The codebase SHALL keep router modules focused on request validation, auth entry checks, dependency wiring, and response shaping.

#### Scenario: Router avoids owning business rules
- **WHEN** a router endpoint is reviewed after refactor
- **THEN** business rule branches are primarily implemented in service or domain classes rather than inline in the endpoint

### Requirement: Frontend behavior shall be decomposed into cohesive object-like modules
The frontend SHALL organize major UI concerns into cohesive modules or controller-style objects rather than a single undifferentiated script body.

#### Scenario: Feature slice ownership is explicit
- **WHEN** a frontend concern such as auth, scheme dashboard, scheme detail workflow, scheduling, user management, or guidance is implemented
- **THEN** its state transitions and handlers live in a named module or controller boundary

#### Scenario: Shared state access is constrained
- **WHEN** a frontend module interacts with global application state
- **THEN** that interaction occurs through explicit module methods or well-defined shared interfaces

### Requirement: Public behavior shall remain stable during the refactor
The refactor SHALL preserve existing externally visible behavior unless a separate capability change explicitly authorizes functional changes.

#### Scenario: API contract preservation
- **WHEN** backend internals are refactored
- **THEN** existing endpoint paths, expected request shapes, and response semantics remain compatible unless separately approved

#### Scenario: Workflow parity preservation
- **WHEN** workflow-related code is moved into new classes or modules
- **THEN** scheme status transitions, role enforcement, and notification side effects remain unchanged from the user perspective

### Requirement: Refactor rollout shall be incremental and regression-guarded
The codebase SHALL be refactored in slices with validation after each significant extraction.

#### Scenario: Slice-level extraction
- **WHEN** a major domain is refactored
- **THEN** the change is delivered in an isolated slice that can be validated and rolled back independently

#### Scenario: Regression verification accompanies extraction
- **WHEN** a domain slice is refactored
- **THEN** regression checks cover the preserved flows for that slice before the refactor is considered complete
