"""SQLite connection helpers used by the API and database bootstrap command."""

import os
import sqlite3
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = REPOSITORY_ROOT / "backend" / "database" / "dev.db"


def get_database_path() -> Path:
    """Return the configured runtime database path, defaulting to local SQLite."""
    configured_path = os.getenv("DATABASE_PATH")
    return Path(configured_path).expanduser() if configured_path else DEFAULT_DATABASE_PATH


def connect(database_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key checks enabled."""
    path = Path(database_path) if database_path else get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
