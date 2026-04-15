# Login Screen

## Purpose

Provide authenticated access to the HOMES Scheme Onboarding Portal for agency users and MTO administrators.

## Primary Users

- Agency creators
- Agency approvers
- MTO administrators

## Entry Conditions

- User is unauthenticated.
- No valid token is present in local storage.

## Functional Requirements

- The screen must display the HOMES branding and product description.
- The screen must provide username and password input fields.
- The screen must provide a primary sign-in action.
- The screen must provide a demo admin shortcut that logs the user in using the seeded `mto_admin` account.
- The screen must display demo credentials for seeded users.
- On successful login, the screen must persist the JWT token and user profile in browser local storage.
- On successful login, the user must be redirected into the authenticated portal shell.
- On failed login, the screen must show an error toast with the backend error message.

## Data Inputs

- Username
- Password

## Validation Rules

- Username is required.
- Password is required.
- Authentication failure must not reveal whether the username or password was incorrect.

## API Dependencies

- `POST /api/auth/login`

## UI States

- Default state
- Submitting state
- Error state
- Demo login success state

## Security Requirements

- The token must be sent on subsequent API calls using the `Authorization: Bearer` header.
- Logged-in state must survive browser refresh by reading local storage.

## Success Criteria

- Authenticated users land on the correct workspace without re-entering credentials until logout or token expiry.