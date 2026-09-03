"""Project write service backed by Git-tracked JSON source files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..database import source_files
from ..database.connection import connect
from ..database.sync_data import sync_source_data
from ..schemas.api import ProjectResponse, ProjectWrite
from ..schemas.source_data import ProjectRecord, validate_slug
from .queries import get_user


def _slugify_name(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value[:60] or "project"


def _file_path(project_id: str) -> Path:
    validate_slug(project_id, "project id")
    return source_files.DATA_ROOT / "projects" / f"{project_id}.json"


def _serialize(data: ProjectRecord) -> bytes:
    return (json.dumps(data.model_dump(), indent=2) + "\n").encode()


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _apply_change(path: Path, data: ProjectRecord) -> None:
    """Write the tracked source file and reconcile the database.

    The previous file content is restored if database reconciliation fails,
    so the repository and the runtime database never knowingly diverge.
    """
    snapshot = path.read_bytes() if path.exists() else None
    try:
        _write_atomic(path, _serialize(data))
        with connect() as connection:
            sync_source_data(connection)
    except Exception:
        if snapshot is None:
            path.unlink(missing_ok=True)
        else:
            _write_atomic(path, snapshot)
        raise


def _response(project_id: str, payload: ProjectWrite) -> ProjectResponse:
    return ProjectResponse(
        id=project_id,
        userId=payload.userId,
        name=payload.name,
        description=payload.description,
        technology=payload.technology,
        status=payload.status,
    )


def create_project(payload: ProjectWrite) -> ProjectResponse:
    get_user(payload.userId)
    existing_ids = {project.id for project in source_files.load_projects()}
    base = _slugify_name(payload.name)
    project_id = base
    counter = 2
    while project_id in existing_ids:
        project_id = f"{base}-{counter}"
        counter += 1
    record = ProjectRecord(
        id=project_id,
        owner_id=payload.userId,
        name=payload.name,
        description=payload.description,
        technology=payload.technology,
        status=payload.status,
    )
    _apply_change(_file_path(project_id), record)
    return _response(project_id, payload)
