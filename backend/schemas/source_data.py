"""Shared validation contracts for Git-tracked source data (see docs/project-contract.md)."""

from __future__ import annotations

import re
from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Stable identifiers are lowercase slugs. These are also used as directory and
# file names, so the allowed character set is intentionally strict.
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ACTIVITY_STATUSES = {"planned", "in-progress", "completed"}
PROJECT_STATUSES = {"planned", "active", "completed", "archived"}


def validate_slug(value: str, field: str) -> str:
    """Validate a slug identifier, raising ValueError with a useful message."""
    if not SLUG_PATTERN.match(value):
        raise ValueError(
            f"Invalid {field} {value!r}: use lowercase letters, digits, and hyphens "
            "(must start with a letter or digit)."
        )
    return value


def validate_date_string(value: str, field: str) -> str:
    """Validate an ISO 8601 calendar date (YYYY-MM-DD)."""
    if not DATE_PATTERN.match(value):
        raise ValueError(f"Invalid {field} {value!r}: expected ISO 8601 date YYYY-MM-DD.")
    try:
        date_type.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Invalid {field} {value!r}: not a real calendar date.") from error
    return value


class UserRecord(BaseModel):
    """A team member, one file per user: data/users/<id>.json."""

    model_config = ConfigDict(extra="forbid")

    id: str
    display_name: str = Field(min_length=1)
    role: str = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        return validate_slug(value, "user id")


class ActivityRecord(BaseModel):
    """A single daily activity inside data/activities/<user_id>/<date>.json."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str = Field(min_length=1)
    status: str
    project_id: str | None = None

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        return validate_slug(value, "activity id")

    @field_validator("status")
    @classmethod
    def _valid_status(cls, value: str) -> str:
        if value not in ACTIVITY_STATUSES:
            raise ValueError(
                f"Invalid activity status {value!r}: expected one of {sorted(ACTIVITY_STATUSES)}."
            )
        return value

    @field_validator("project_id")
    @classmethod
    def _valid_project(cls, value: str | None) -> str | None:
        return validate_slug(value, "project id") if value is not None else None


class ActivityFile(BaseModel):
    """Per-user, per-date activity file data/activities/<user_id>/<date>.json."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    date: str
    activities: list[ActivityRecord]

    @field_validator("user_id")
    @classmethod
    def _valid_user(cls, value: str) -> str:
        return validate_slug(value, "user id")

    @field_validator("date")
    @classmethod
    def _valid_date(cls, value: str) -> str:
        return validate_date_string(value, "date")


class ProjectRecord(BaseModel):
    """Project metadata, one file per project: data/projects/<id>.json."""

    model_config = ConfigDict(extra="forbid")

    id: str
    owner_id: str
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    technology: list[str] = Field(default_factory=list)
    status: str

    @field_validator("id")
    @classmethod
    def _valid_id(cls, value: str) -> str:
        return validate_slug(value, "project id")

    @field_validator("owner_id")
    @classmethod
    def _valid_owner(cls, value: str) -> str:
        return validate_slug(value, "owner id")

    @field_validator("status")
    @classmethod
    def _valid_status(cls, value: str) -> str:
        if value not in PROJECT_STATUSES:
            raise ValueError(
                f"Invalid project status {value!r}: expected one of {sorted(PROJECT_STATUSES)}."
            )
        return value
