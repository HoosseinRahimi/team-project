# Database rules

The runtime database is local SQLite at `backend/database/dev.db` by default and
is ignored by Git. It is generated state, not the source of truth. Never commit
it or manually copy another developer's database.

## Layers

1. **Schema migrations** — versioned SQL files in `backend/database/migrations/`.
2. **Git-tracked source data** — JSON files in `data/` (the authoritative shared
   source for team information). See `docs/project-contract.md`.
3. **Runtime database** — generated local SQLite, derived from 1 + 2.

## Commands

```bash
make db-init     # create DB from scratch, apply migrations (schema only)
make db-sync     # reconcile Git-tracked data/ into the DB
make db-reset    # delete the local dev database (fixed safe path only)

# equivalent direct commands:
.venv/bin/python -m backend.database.init_db --seed
.venv/bin/python -m backend.database.sync_data
```

`init_db --seed` and `sync_data` are **idempotent**: running them repeatedly
with unchanged repository data produces the same database state and never
duplicates records. `sync_data` performs full **reconciliation**: rows whose
source records were deleted are removed from the database, so SQLite exactly
mirrors the tracked source IDs under `data/`.

## Migration rules

- Every schema change is a new, version-controlled SQL file under
  `backend/database/migrations/`.
- Use a zero-padded numeric prefix and descriptive name, for example
  `005_add_activity_project_id.sql`.
- Migrations are applied in sorted filename order. The **full file stem** (for
  example `005_add_calendar`) is recorded as the version in `schema_migrations`.
- Duplicate numeric prefixes (e.g. two files both starting `005_`) are rejected
  with an error instead of silently skipping the second migration. If two
  branches collide, renumber one on the feature branch before merging.
- Never rewrite or delete a migration after it has merged into `main`. Add a
  new migration for a correction or schema change.
- Migration conflicts require review of both schema changes. Normalize numbering
  and assumptions before merging; do not discard a migration to make the
  conflict disappear.

## Data authority

For Git-shared team activities and project metadata, **the Git-tracked files
under `data/` are authoritative**. SQLite is only a local derived runtime
representation.

Activity create/update/delete operations must follow this flow:

```text
validated API request
        ↓
data/activities/<user_id>/<date>.json
        ↓
database reconciliation
        ↓
SQLite runtime state
```

The activity write service updates the tracked JSON source atomically and then
reconciles SQLite. If reconciliation fails, the source-file change is restored
instead of leaving the repository and runtime database knowingly inconsistent.
Stable activity IDs are authoritative: after a successful sync, the set of
activity IDs in SQLite must equal the set currently present in tracked activity
files.

When running with Docker Compose, `./data` is bind-mounted into the backend
container so web/API edits remain visible to Git on the host.
