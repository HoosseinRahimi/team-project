"""Query services separating API routes from database access."""

from __future__ import annotations

from ..database.connection import connect
from ..schemas.api import ActivityResponse, ProjectResponse, UserResponse
from ..schemas.source_data import validate_slug


class NotFoundError(LookupError):
    """Raised when a requested resource does not exist (mapped to HTTP 404)."""


def list_users() -> list[UserResponse]:
    with connect() as connection:
        rows = connection.execute("SELECT id, display_name, role FROM users ORDER BY id").fetchall()
    return [UserResponse(id=r["id"], name=r["display_name"], role=r["role"]) for r in rows]


def get_user(user_id: str) -> UserResponse:
    validate_slug(user_id, "user id")
    with connect() as connection:
        row = connection.execute(
            "SELECT id, display_name, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if row is None:
        raise NotFoundError(f"Unknown user: {user_id}")
    return UserResponse(id=row["id"], name=row["display_name"], role=row["role"])


def list_activities() -> list[ActivityResponse]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, user_id, date, title, status, project_id
            FROM activities ORDER BY date, id
            """
        ).fetchall()
    return [
        ActivityResponse(
            id=r["id"],
            userId=r["user_id"],
            date=r["date"],
            title=r["title"],
            status=r["status"],
            projectId=r["project_id"],
        )
        for r in rows
    ]


def list_projects() -> list[ProjectResponse]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, user_id, name, description, technology, status
            FROM projects ORDER BY id
            """
        ).fetchall()
    return [
        ProjectResponse(
            id=r["id"],
            userId=r["user_id"],
            name=r["name"],
            description=r["description"],
            technology=[item for item in r["technology"].split(",") if item],
            status=r["status"],
        )
        for r in rows
    ]


def user_exists(user_id: str) -> bool:
    try:
        get_user(user_id)
    except (NotFoundError, ValueError):
        return False
    return True
