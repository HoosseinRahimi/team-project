# Architecture

## Overview

The project is a **modular monolith**: one FastAPI backend, one React frontend,
one SQLite database. No microservices, queues, or distributed infrastructure.

- **Frontend** (`frontend/`): React + Vite + TypeScript. Route modules under
  `src/components/`, shared types in `src/types.ts`, API client in `src/api.ts`.
- **Backend** (`backend/`):
  - `app/` — FastAPI application. Routes live in small modules under `app/api/`
    and are registered in `app/main.py`.
  - `schemas/` — Pydantic models. `api.py` for HTTP contracts,
    `source_data.py` for Git-tracked data validation.
  - `services/` — business logic / queries between routes and the database.
  - `database/` — connection helpers, SQL migrations, init/seed/sync commands.
- **Data** (`data/`): Git-tracked source of truth for shared team information
  (users, activities, projects). See `docs/project-contract.md`.
- **Student projects** (`projects/<owner>/<project>/`): runnable member
  projects with a `project.json` manifest.

## Database approach

We deliberately use **SQLite with ordered plain-SQL migrations** instead of
SQLAlchemy + Alembic. For a student team the stdlib `sqlite3` approach is
simpler to understand and debug while still giving deterministic, reviewable
schema evolution. Migration rules are in `docs/database-rules.md`.

- All application timestamps are UTC (`CURRENT_TIMESTAMP` in SQLite is UTC).
- Activity dates are explicit ISO-8601 calendar dates (`YYYY-MM-DD`).
- Primary keys are stable text slugs (`hossein`, `team-foundation`) or stable
  composite slugs (`hossein-2026-08-31-init-repository`), so records created
  independently by different developers cannot collide.

## Extension points

- **New backend feature:** add `backend/app/api/<feature>.py` with its own
  `APIRouter`, register it in `backend/app/main.py` (one line), put queries in
  `backend/services/`, schemas in `backend/schemas/`.
- **New frontend feature:** add a component module under `frontend/src/components/`
  and a route branch in `App.tsx`; reuse shared types from `src/types.ts`.
- **New schema change:** new numbered SQL migration file. Never edit an
  already-merged migration.
- **New shared team data:** add files under `data/` following the contracts in
  `docs/project-contract.md`, then run `make db-sync`.
