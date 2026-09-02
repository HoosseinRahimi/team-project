# Convenience wrappers. Every command here also exists as a documented script.

.PHONY: setup test lint format db-init db-sync db-reset dev check

setup:            ## Create venv, install dependencies, initialize DB with data
	./scripts/setup.sh

test:             ## Backend tests + frontend checks + integration test
	./scripts/test.sh

lint:             ## Backend (ruff) and frontend (eslint) lint checks
	.venv/bin/python -m ruff check backend tests
	npm run lint --prefix frontend

format:           ## Auto-format backend and frontend
	.venv/bin/python -m ruff format backend tests
	npm run format --prefix frontend

db-init:          ## Create DB from scratch and apply migrations (no data)
	.venv/bin/python -m backend.database.init_db

db-sync:          ## Idempotently sync Git-tracked data/ into the DB
	.venv/bin/python -m backend.database.sync_data

db-reset:         ## Delete the local dev database (safe, fixed path)
	./scripts/reset-dev-db.sh

dev:              ## Print the two development server commands
	@echo "Backend:  .venv/bin/python -m uvicorn backend.app.main:app --reload"
	@echo "Frontend: npm run dev --prefix frontend"
