#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATABASE_FILE="$PROJECT_ROOT/backend/database/dev.db"

rm -f "$DATABASE_FILE"
echo "Removed the generated development database: $DATABASE_FILE"
echo "Recreate it with: .venv/bin/python -m backend.database.init_db --seed"
