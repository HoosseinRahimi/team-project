"""Synchronize Git-tracked source files into the derived SQLite database."""

from __future__ import annotations

import argparse
from contextlib import closing

from .connection import connect, get_database_path
from .init_db import initialize_database
from .source_files import load_activities, load_projects, load_users


def sync_source_data(connection) -> dict[str, int]:
    """Make the derived database exactly match tracked source data."""
    users = load_users()
    projects = load_projects()

    with connection:
        connection.executemany(
            """
            INSERT INTO users (id, display_name, role) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              display_name=excluded.display_name,
              role=excluded.role
            """,
            [(u.id, u.display_name, u.role) for u in users],
        )

        connection.executemany(
            """
            INSERT INTO projects (id, user_id, name, description, technology, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              user_id=excluded.user_id,
              name=excluded.name,
              description=excluded.description,
              technology=excluded.technology,
              status=excluded.status
            """,
            [
                (p.id, p.owner_id, p.name, p.description, ",".join(p.technology), p.status)
                for p in projects
            ],
        )

        activity_rows = [
            (
                a.id,
                file.user_id,
                file.date,
                a.title,
                a.status,
                a.project_id,
            )
            for file in load_activities()
            for a in file.activities
        ]

        connection.executemany(
            """
            INSERT INTO activities (id, user_id, date, title, status, project_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              user_id=excluded.user_id,
              date=excluded.date,
              title=excluded.title,
              status=excluded.status,
              project_id=excluded.project_id
            """,
            activity_rows,
        )

        user_ids = [u.id for u in users]
        project_ids = [p.id for p in projects]
        activity_ids = [a[0] for a in activity_rows]

        if user_ids:
            placeholders = ",".join("?" for _ in user_ids)
            connection.execute(
                f"DELETE FROM users WHERE id NOT IN ({placeholders})", user_ids
            )
        else:
            connection.execute("DELETE FROM users")

        if project_ids:
            placeholders = ",".join("?" for _ in project_ids)
            connection.execute(
                f"DELETE FROM projects WHERE id NOT IN ({placeholders})", project_ids
            )
        else:
            connection.execute("DELETE FROM projects")

        if activity_ids:
            placeholders = ",".join("?" for _ in activity_ids)
            connection.execute(
                f"DELETE FROM activities WHERE id NOT IN ({placeholders})", activity_ids
            )
        else:
            connection.execute("DELETE FROM activities")

    return {
        "users": len(users),
        "projects": len(projects),
        "activities": len(activity_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=str, default=None)
    args = parser.parse_args()

    initialize_database(args.database)
    with closing(connect(args.database)) as connection:
        counts = sync_source_data(connection)

    print(
        "Synchronized source data: "
        + ", ".join(f"{count} {name}" for name, count in counts.items())
    )
    print(f"Database ready: {args.database or get_database_path()}")


if __name__ == "__main__":
    main()
