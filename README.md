# Team Project

Team Project is a local web application for a university team and their
professor. Team members get a personal dashboard for daily activities,
calendar history, timeline, and projects.

The shared platform currently includes the stable repository/database
foundation plus the Phase 2 activity experience: activity create/edit/delete,
calendar, timeline, and per-user dashboard statistics. Authentication,
professor-wide administration, advanced Git integration, and project execution
remain future features.

## Architecture

Modular monolith — no microservices:

- **Frontend:** React + Vite + **TypeScript** (`frontend/`)
- **Backend:** FastAPI with small route modules, services, and Pydantic schemas (`backend/`)
- **Database:** SQLite generated from ordered SQL migrations; the generated
  file is **never committed** (`backend/database/`)
- **Source data:** Git-tracked JSON files under `data/` are the **authoritative
  shared source** for users, activities, and projects
- **Docker:** Compose runs one backend and one frontend container locally; the
  backend bind-mounts `./data` so activity edits remain Git-visible on the host

See [docs/architecture.md](docs/architecture.md) for details.

## Repository structure

```text
team-project/
├── frontend/                 # React/Vite/TypeScript application
│   └── src/{components,types.ts,api.ts,App.tsx,main.tsx}
├── backend/
│   ├── app/                  # FastAPI app; routes in app/api/*.py
│   ├── schemas/              # Pydantic request/response + data validation
│   ├── services/             # Queries + tracked activity write logic
│   └── database/
│       ├── migrations/       # Ordered SQL migrations (committed)
│       ├── connection.py     # SQLite connection helpers
│       ├── init_db.py        # Create DB + apply migrations (+ --seed)
│       ├── sync_data.py      # Reconcile data/ into the DB
│       └── source_files.py   # Validated loader for data/ files
├── data/                     # AUTHORITATIVE shared team data (Git-tracked)
│   ├── users/<id>.json
│   ├── activities/<user_id>/<date>.json
│   └── projects/<id>.json
├── projects/<owner>/<name>/  # Student projects with project.json manifests
├── scripts/                  # setup, test, reset, conflict-marker check
├── docs/                     # architecture, git workflow, database rules, contracts
├── tests/                    # Backend/API/database tests
├── .github/                  # CI workflow + PR template
├── docker-compose.yml
└── Makefile
```

## Prerequisites

- Git
- Python 3.11+ (3.12+ recommended)
- Node.js 20+ and npm
- Docker (optional, for the container workflow)

## Quick setup (native)

```bash
git clone <repository-url> team-project
cd team-project
make setup
```

This creates `.venv`, installs backend and frontend dependencies, and builds
the database from migrations with the tracked data.

## Database initialization and synchronization

```bash
make db-init        # create DB from scratch, apply migrations (schema only)
make db-sync        # reconcile Git-tracked data/ into the DB
make db-reset       # delete the local dev database

# equivalent direct commands:
.venv/bin/python -m backend.database.init_db --seed
.venv/bin/python -m backend.database.sync_data
```

Running sync repeatedly never duplicates records. The Git-tracked files under
`data/` are authoritative; SQLite is derived local state and is ignored by Git.
Activity writes made through the web/API update the corresponding tracked JSON
file first and then reconcile SQLite. See [docs/database-rules.md](docs/database-rules.md).

## Run the backend

```bash
.venv/bin/python -m uvicorn backend.app.main:app --reload
```

API at <http://localhost:8000>. Interactive docs: <http://localhost:8000/docs>.

Core endpoints:

```text
GET    /api/health
GET    /api/users
GET    /api/users/{id}
GET    /api/activities
POST   /api/activities
PUT    /api/activities/{activity_id}
DELETE /api/activities/{activity_id}
GET    /api/projects
```

## Run the frontend

```bash
npm run dev --prefix frontend
```

Open <http://localhost:5173>. Member routes such as `/users/hossein` expose the
shared user dashboard with activity statistics, activity management, calendar,
timeline, and connected projects. Override the backend URL with
`VITE_API_BASE_URL` (see `.env.example`).

## Run tests

```bash
make test
```

Individual checks:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check backend tests
npm run lint --prefix frontend
npm run format:check --prefix frontend
npm run type-check --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
```

## Docker

```bash
docker compose up --build
```

Then open <http://localhost:5173>. The Compose configuration bind-mounts
`./data:/app/data`, so activities created or edited through the site update the
host repository's tracked JSON files and appear in `git status`.

Stop with `Ctrl+C` or `docker compose down`.

## Git workflow

`main` is the stable integration branch — never commit features directly.
Branches: `feature/<name>`, `fix/<name>`, `docs/<name>`, `refactor/<name>`,
`test/<name>`. Update feature branches with `git merge main`; open Pull
Requests into `main` (squash merge by default).

- [CONTRIBUTING.md](CONTRIBUTING.md) — branch, commit, test, migration, and PR workflow
- [docs/git-workflow.md](docs/git-workflow.md) — branch model and conflict rules
- [docs/database-rules.md](docs/database-rules.md) — migrations and data authority
- [docs/project-contract.md](docs/project-contract.md) — `data/` file and project manifest contracts
- [docs/branch-protection.md](docs/branch-protection.md) — recommended GitHub settings for `main`

## API conventions

- Prefix all routes with `/api/`, use plural nouns (`/api/users`)
- Typed Pydantic request/response models; structured errors; no stack traces
- Unknown user/project/activity → 404; malformed input → 422
- Git-tracked JSON remains authoritative for shared activity state
