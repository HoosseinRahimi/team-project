"""Load and validate Git-tracked source data under ``data/``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..schemas.source_data import (
    ActivityFile,
    ProjectRecord,
    UserRecord,
    validate_date_string,
    validate_slug,
)
from .connection import REPOSITORY_ROOT

DATA_ROOT = REPOSITORY_ROOT / "data"


class SourceDataError(ValueError):
    """Raised when a Git-tracked source data file is missing or malformed."""


def _validated(path: Path, model, data: Any):
    try:
        return model.model_validate(data)
    except ValidationError as error:
        raise SourceDataError(
            f"Invalid source data in {path}: {error.error_count()} validation error(s): "
            f"{error.errors()[:3]}"
        ) from error


def _read_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise SourceDataError(f"Missing source data file: {path}") from error
    except json.JSONDecodeError as error:
        raise SourceDataError(f"Malformed JSON in {path}: {error}") from error
    except OSError as error:
        raise SourceDataError(f"Cannot read source data file {path}: {error}") from error


def _user_directory(user_id: str) -> Path:
    validate_slug(user_id, "user id")
    directory = (DATA_ROOT / "activities" / user_id).resolve()
    expected_root = (DATA_ROOT / "activities").resolve()
    if expected_root not in directory.parents:
        raise SourceDataError(f"Resolved path for user {user_id!r} escaped the data directory.")
    return directory


def _activity_file_path(user_id: str, date: str) -> Path:
    validate_date_string(date, "activity date")
    return _user_directory(user_id) / f"{date}.json"


def load_users() -> list[UserRecord]:
    records: list[UserRecord] = []
    users_dir = DATA_ROOT / "users"
    for path in sorted(users_dir.glob("*.json")):
        validate_slug(path.stem, "user file name")
        record = _validated(path, UserRecord, _read_json(path))
        if record.id != path.stem:
            raise SourceDataError(
                f"{path}: user id {record.id!r} does not match file name {path.stem!r}."
            )
        records.append(record)
    return records


def load_activity_dates(user_id: str) -> list[str]:
    directory = _user_directory(user_id)
    return sorted(path.stem for path in directory.glob("*.json"))


def load_activities(user_id: str | None = None) -> list[ActivityFile]:
    if user_id is not None:
        user_ids = [user_id]
    else:
        activities_root = DATA_ROOT / "activities"
        user_ids = (
            sorted(path.name for path in activities_root.iterdir() if path.is_dir())
            if activities_root.is_dir()
            else []
        )

    files: list[ActivityFile] = []
    seen_activity_ids: dict[str, Path] = {}
    for uid in user_ids:
        for date in load_activity_dates(uid):
            path = _activity_file_path(uid, date)
            data = _validated(path, ActivityFile, _read_json(path))
            if data.user_id != uid:
                raise SourceDataError(
                    f"{path}: user_id {data.user_id!r} does not match directory {uid!r}."
                )
            if data.date != date:
                raise SourceDataError(
                    f"{path}: date {data.date!r} does not match file name {date!r}."
                )
            for activity in data.activities:
                previous = seen_activity_ids.get(activity.id)
                if previous is not None:
                    raise SourceDataError(
                        f"Duplicate activity id {activity.id!r} in {previous} and {path}."
                    )
                seen_activity_ids[activity.id] = path
            files.append(data)
    return files


def load_projects() -> list[ProjectRecord]:
    records: list[ProjectRecord] = []
    projects_dir = DATA_ROOT / "projects"
    for path in sorted(projects_dir.glob("*.json")):
        validate_slug(path.stem, "project file name")
        record = _validated(path, ProjectRecord, _read_json(path))
        if record.id != path.stem:
            raise SourceDataError(
                f"{path}: project id {record.id!r} does not match file name {path.stem!r}."
            )
        records.append(record)
    return records
