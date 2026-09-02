"""Activity write service backed by Git-tracked JSON source files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..database import source_files
from ..database.connection import connect
from ..database.sync_data import sync_source_data
from ..schemas.api import ActivityResponse, ActivityWrite
from ..schemas.source_data import ActivityFile, ActivityRecord, validate_slug
from .queries import NotFoundError, get_user


def _slugify_title(title: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return value[:60] or "activity"


def _file_path(user_id: str, date: str) -> Path:
    validate_slug(user_id, "user id")
    return source_files.DATA_ROOT / "activities" / user_id / f"{date}.json"


def _read_file(path: Path, user_id: str, date: str) -> ActivityFile:
    if not path.exists():
        return ActivityFile(user_id=user_id, date=date, activities=[])
    return ActivityFile.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _serialize(data: ActivityFile) -> bytes:
    return (json.dumps(data.model_dump(), indent=2) + "\n").encode()


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _apply_changes(changes: dict[Path, ActivityFile | None]) -> None:
    """Apply source-file changes and restore them if DB reconciliation fails."""
    snapshots = {path: path.read_bytes() if path.exists() else None for path in changes}
    try:
        for path, data in changes.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                _write_atomic(path, _serialize(data))
        with connect() as connection:
            sync_source_data(connection)
    except Exception:
        for path, content in snapshots.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                _write_atomic(path, content)
        raise


def _all_activity_ids() -> set[str]:
    return {
        activity.id
        for activity_file in source_files.load_activities()
        for activity in activity_file.activities
    }


def _validate_project(project_id: str | None) -> None:
    if project_id is None:
        return
    if not any(project.id == project_id for project in source_files.load_projects()):
        raise NotFoundError(f"Unknown project: {project_id}")


def _find_activity(activity_id: str) -> tuple[Path, ActivityFile, int] | None:
    validate_slug(activity_id, "activity id")
    for activity_file in source_files.load_activities():
        path = _file_path(activity_file.user_id, activity_file.date)
        for index, activity in enumerate(activity_file.activities):
            if activity.id == activity_id:
                return path, activity_file, index
    return None


def _response(activity_id: str, payload: ActivityWrite) -> ActivityResponse:
    return ActivityResponse(
        id=activity_id,
        userId=payload.userId,
        date=payload.date,
        title=payload.title,
        status=payload.status,
        projectId=payload.projectId,
    )


def create_activity(payload: ActivityWrite) -> ActivityResponse:
    get_user(payload.userId)
    _validate_project(payload.projectId)
    path = _file_path(payload.userId, payload.date)
    data = _read_file(path, payload.userId, payload.date)
    existing_ids = _all_activity_ids()
    base = f"{payload.userId}-{payload.date}-{_slugify_title(payload.title)}"
    activity_id = base
    counter = 2
    while activity_id in existing_ids:
        activity_id = f"{base}-{counter}"
        counter += 1
    data.activities.append(
        ActivityRecord(
            id=activity_id,
            title=payload.title,
            status=payload.status,
            project_id=payload.projectId,
        )
    )
    _apply_changes({path: data})
    return _response(activity_id, payload)


def update_activity(activity_id: str, payload: ActivityWrite) -> ActivityResponse:
    found = _find_activity(activity_id)
    if found is None:
        raise NotFoundError(f"Unknown activity: {activity_id}")
    get_user(payload.userId)
    _validate_project(payload.projectId)
    old_path, old_data, index = found
    new_path = _file_path(payload.userId, payload.date)
    record = ActivityRecord(
        id=activity_id,
        title=payload.title,
        status=payload.status,
        project_id=payload.projectId,
    )

    if old_path == new_path:
        old_data.activities[index] = record
        _apply_changes({old_path: old_data})
    else:
        old_data.activities.pop(index)
        new_data = _read_file(new_path, payload.userId, payload.date)
        if any(item.id == activity_id for item in new_data.activities):
            raise ValueError(f"Duplicate activity id: {activity_id}")
        new_data.activities.append(record)
        _apply_changes({old_path: old_data if old_data.activities else None, new_path: new_data})

    return _response(activity_id, payload)


def delete_activity(activity_id: str) -> None:
    found = _find_activity(activity_id)
    if found is None:
        raise NotFoundError(f"Unknown activity: {activity_id}")
    path, data, index = found
    data.activities.pop(index)
    _apply_changes({path: data if data.activities else None})
