# Project and data contract

## Git-tracked data files (`data/`)

The `data/` directory is the **authoritative shared source** for team
information. One file per logical unit keeps merges conflict-free.

All files: UTF-8, 2-space indent, newline at end, no volatile generated fields.

### Users — `data/users/<user_id>.json`

```json
{
  "id": "hossein",
  "display_name": "Hossein",
  "role": "Developer"
}
```

The file name must match `id`.

### Activities — `data/activities/<user_id>/<YYYY-MM-DD>.json`

```json
{
  "user_id": "hossein",
  "date": "2026-08-31",
  "activities": [
    {
      "id": "hossein-2026-08-31-init-repository",
      "title": "Initialize repository",
      "status": "completed",
      "project_id": "team-foundation"
    }
  ]
}
```

- `id` must be a **stable unique slug**, recommended
  `<user_id>-<date>-<short-description>`.
- `status` is one of `planned | in-progress | completed`.
- `project_id` may be `null` or the id of a project in `data/projects/`.

### Projects — `data/projects/<project_id>.json`

```json
{
  "id": "team-foundation",
  "owner_id": "hossein",
  "name": "Team Project Foundation",
  "description": "Initial repository and application foundation.",
  "technology": ["python"],
  "status": "active"
}
```

- `status` is one of `planned | active | completed | archived`.

### Validation rules

- **Identifiers (user/project/activity ids) are lowercase slugs:**
  `[a-z0-9][a-z0-9-]*`. They are used as file and directory names, so other
  characters are rejected. Path traversal (`../../etc/passwd`) can never escape
  the data directory — slugs are validated before any path is joined.
- Dates are ISO 8601 calendar dates and must match their file name.
- All files are validated with the Pydantic models in
  `backend/schemas/source_data.py`. Malformed files fail loudly at load time
  with a message naming the offending file.

## Writing new activities

Future activity-creation features must preserve the Git-friendly model:

1. validate the activity against the schema,
2. write/update `data/activities/<user_id>/<date>.json`,
3. run the idempotent sync to update the runtime database.

Never store shared activities only in SQLite.

## Student projects (`projects/<owner>/<project>/`)

Each student project directory contains a `project.json` manifest:

```json
{
  "id": "team-platform",
  "name": "Team Platform",
  "owner_id": "hossein",
  "description": "...",
  "technology": ["python"],
  "project_type": "cli",
  "entry_point": "main.py",
  "run": "python main.py",
  "build": null,
  "repository_path": "projects/hossein/team-platform"
}
```

### Security rules

- The backend must never execute arbitrary user-supplied shell strings.
- Future project execution must use the explicit `run`/`build` fields from the
  manifest, allowlisted per project type, after validating the manifest and ids.
- Manifests are untrusted input: validate ids and paths before use.
