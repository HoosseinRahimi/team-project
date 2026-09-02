# Contributing

## 1. Create a branch (never commit features directly to `main`)

```bash
git switch main
git pull
git switch -c feature/<feature-name>   # or fix/ docs/ refactor/ test/
```

## 2. Update from main (default strategy: merge)

Before opening or updating a Pull Request, merge the latest main into your
branch and resolve conflicts **on the feature branch**:

```bash
git switch feature/<feature-name>
git merge main
# resolve conflicts, then verify:
./scripts/test.sh
```

Do not mix rebase into this workflow, do not force-push `main`.

## 3. Commit format (Conventional Commits)

```text
feat: add calendar page
fix: handle missing activity files
docs: document migration workflow
test: add user API tests
chore: update dependencies
```

Meaningful messages only — no `update`, `final`, `fix stuff`.

## 4. Run tests and checks before pushing

```bash
./scripts/test.sh                                  # full integration check
.venv/bin/python -m pytest -q                      # backend tests
.venv/bin/python -m ruff check backend tests      # backend lint
.venv/bin/python -m ruff format backend tests     # backend format
npm run lint --prefix frontend                    # frontend lint
npm run type-check --prefix frontend              # frontend types
npm test --prefix frontend                        # frontend unit tests
npm run build --prefix frontend                   # frontend build
```

## 5. Database migration workflow

```bash
# add backend/database/migrations/00N_description.sql, then verify:
rm -f /tmp/mig-test.db
DATABASE_PATH=/tmp/mig-test.db .venv/bin/python -m backend.database.init_db --seed
```

Never edit a migration that is already merged into `main`; add a new one.
Details: `docs/database-rules.md`.

## 6. Resolving conflicts

1. Inspect **both** sides; never blindly take `ours` or `theirs`.
2. Determine the intended combined behavior.
3. Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
4. Build/run affected components, run `./scripts/test.sh`.
5. If migrations conflicted, normalize order and verify a fresh DB init.
6. Commit the resolution on the feature branch.

High-risk files: migrations, `package.json`/lock files, `requirements*.txt`,
Dockerfiles, `docker-compose.yml`, `backend/app/main.py`, shared schemas,
CI config. Lock-file conflicts are regenerated with `npm install` — never
solved by deleting the lock file.

## 7. Open a Pull Request

```bash
git push -u origin feature/<feature-name>
```

Open a PR into `main` using the repository template. CI must pass. Squash-merge
is the default merge strategy; delete the branch after merging.

## 8. Definition of Done

A task is Done when: implementation completed, code formatted, lint passed,
tests added/updated and passing, migrations included where required, API
documentation/contract updated where required, docs updated where required,
PR reviewed and merged, and `main` remains runnable.
