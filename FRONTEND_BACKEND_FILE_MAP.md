# Frontend and Backend File Map

This map separates UI-facing files from API/domain files so changes are easier to navigate.

## Frontend Files

- `app/static/index.html`
  - Main SPA UI shell, rendering, API calls, and client-side interactions.
- `requirement-specs/`
  - UI/UX requirement markdown references by screen and modal.

## Backend Files

- `app/main.py`
  - FastAPI application startup and router registration.
- `app/auth.py`
  - Auth, token verification, and current-user access control.
- `app/models.py`
  - SQLAlchemy models and status enums.
- `app/routers/`
  - API route handlers.
  - `app/routers/schemes.py`: schemes CRUD/workflow/import-export endpoints.
  - `app/routers/scheduling.py`: scheduling overview and booking endpoints.
  - `app/routers/guidance.py`: field-guidance endpoints.
- `app/services/`
  - Backend domain services.
  - `app/services/schemes/lifecycle.py`: scheme lifecycle and workflow transitions.
  - `app/services/schemes/import_export.py`: Excel import/export orchestration.
  - `app/services/schemes/notifications.py`: workflow notification and notification-log orchestration.
  - `app/services/scheduling/service.py`: scheduling aggregation logic.
  - `app/services/guidance/service.py`: field-guidance read/update orchestration.
  - `app/services/notifications.py`: email delivery utility.

## Related Testing and Ops Files

- `test_features.py`: regression/integration coverage.
- `requirements.txt`: Python dependency lock list.
- `Dockerfile`, `Procfile`, `railway.json`: deployment/runtime configuration.
