#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-$PROJECT_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing project Python environment. Run ./scripts/setup.sh first." >&2
  exit 1
fi

TEMP_ROOT="$(mktemp -d)"
DATABASE_PATH="$TEMP_ROOT/test.db"
BACKEND_LOG="$TEMP_ROOT/backend.log"
FRONTEND_LOG="$TEMP_ROOT/frontend.log"
backend_pid=""
frontend_pid=""

cleanup() {
  [[ -n "$frontend_pid" ]] && kill "$frontend_pid" 2>/dev/null || true
  [[ -n "$backend_pid" ]] && kill "$backend_pid" 2>/dev/null || true
  rm -rf "$TEMP_ROOT"
}
trap cleanup EXIT

echo "Running backend tests..."
"$PYTHON_BIN" -m pytest -q

echo "Creating a fresh test database and applying migrations with seed data..."
DATABASE_PATH="$DATABASE_PATH" "$PYTHON_BIN" -m backend.database.init_db --seed
[[ -s "$DATABASE_PATH" ]]

echo "Starting backend and checking API endpoints..."
DATABASE_PATH="$DATABASE_PATH" "$PYTHON_BIN" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 18000 >"$BACKEND_LOG" 2>&1 &
backend_pid=$!
for _ in {1..20}; do
  if curl -fsS http://127.0.0.1:18000/health >/dev/null; then break; fi
  sleep 1
done
curl -fsS http://127.0.0.1:18000/api/users | grep -q "hossein"
curl -fsS http://127.0.0.1:18000/api/activities | grep -q "Initialize repository"
curl -fsS http://127.0.0.1:18000/api/projects | grep -q "team-foundation"

echo "Building frontend and checking the development server..."
npm run build --prefix frontend
npm run dev --prefix frontend -- --host 127.0.0.1 --port 4173 >"$FRONTEND_LOG" 2>&1 &
frontend_pid=$!
for _ in {1..20}; do
  if curl -fsS http://127.0.0.1:4173/ >/dev/null; then break; fi
  sleep 1
done
curl -fsS http://127.0.0.1:4173/ | grep -q "Team Project"
curl -fsS http://127.0.0.1:4173/users/hossein | grep -q "Team Project"

echo "Integration check passed."
