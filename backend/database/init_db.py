"""Create a SQLite database, apply migrations, and optionally seed development data."""

import argparse
from contextlib import closing
from pathlib import Path

from .connection import connect, get_database_path
from .seed import seed_database

MIGRATIONS_ROOT = Path(__file__).resolve().parent / "migrations"


def apply_migrations(connection) -> list[str]:
    """Apply unapplied SQL migrations in deterministic filename order."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          version TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    applied = {
        row["version"] for row in connection.execute("SELECT version FROM schema_migrations")
    }
    applied_now = []

    migration_files = sorted(MIGRATIONS_ROOT.glob("*.sql"))

    # Two branches that independently introduce the same numeric prefix must
    # never merge silently: the second migration would be recorded under the
    # same version and never executed. Fail loudly instead (see
    # docs/database-rules.md).
    prefixes: dict[str, str] = {}
    for migration_file in migration_files:
        prefix = migration_file.stem.partition("_")[0]
        if prefix in prefixes:
            raise RuntimeError(
                f"Duplicate migration prefix '{prefix}' in "
                f"{prefixes[prefix]}.sql and {migration_file.name}. "
                "Renumber one of them on your feature branch before merging."
            )
        prefixes[prefix] = migration_file.stem

    for migration_file in migration_files:
        version = migration_file.stem  # full stem: unique, collision-safe
        if version in applied:
            continue

        with migration_file.open(encoding="utf-8") as file:
            sql = file.read()
        with connection:
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (version, version),
            )
        applied_now.append(version)

    return applied_now


def initialize_database(database_path: Path | str | None = None, seed: bool = False) -> list[str]:
    """Initialize a database and return the migrations applied during this run."""
    with closing(connect(database_path)) as connection:
        applied_now = apply_migrations(connection)
        if seed:
            seed_database(connection)
    return applied_now


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Load the committed development fixtures after applying migrations.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=None,
        help="Optional SQLite path. Defaults to backend/database/dev.db or DATABASE_PATH.",
    )
    args = parser.parse_args()

    applied_now = initialize_database(args.database, seed=args.seed)
    destination = args.database or get_database_path()
    if applied_now:
        print(f"Applied migrations: {', '.join(applied_now)}")
    else:
        print("Database is already up to date.")
    if args.seed:
        print("Development seed data loaded.")
    print(f"Database ready: {destination}")


if __name__ == "__main__":
    main()
