#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python is required. Set PYTHON_BIN to a Python 3.11+ executable." >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Install Node.js 20+ and npm, then run setup again." >&2
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install -r backend/requirements-dev.txt
npm ci --prefix frontend
.venv/bin/python -m backend.database.init_db --seed

echo "Setup complete. Run ./scripts/test.sh, then start the frontend and backend as documented in README.md."
