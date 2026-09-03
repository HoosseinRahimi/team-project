"""Pydantic contracts for the public API. ISO 8601 is used for dates."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .source_data import (
    ACTIVITY_STATUSES,
    PROJECT_STATUSES,
    validate_date_string,
    validate_slug,
)


class HealthResponse(BaseModel):
    status: str


class UserResponse(BaseModel):
    id: str
    name: str
    role: str


class ActivityResponse(BaseModel):
    id: str
    userId: str
    date: str
    title: str
    status: str
    projectId: str | None = None


class ActivityWrite(BaseModel):
    """Payload used to create or replace a tracked activity."""

    model_config = ConfigDict(extra="forbid")

    userId: str
    date: str
    title: str = Field(min_length=1, max_length=200)
    status: str = "planned"
    projectId: str | None = None

    @field_validator("title")
    @classmethod
    def _clean_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Title must contain non-whitespace characters.")
        return cleaned

    @field_validator("userId")
    @classmethod
    def _valid_user(cls, value: str) -> str:
        return validate_slug(value, "user id")

    @field_validator("date")
    @classmethod
    def _valid_date(cls, value: str) -> str:
        return validate_date_string(value, "activity date")

    @field_validator("status")
    @classmethod
    def _valid_status(cls, value: str) -> str:
        if value not in ACTIVITY_STATUSES:
            raise ValueError(f"Invalid activity status {value!r}.")
        return value

    @field_validator("projectId")
    @classmethod
    def _valid_project(cls, value: str | None) -> str | None:
        return validate_slug(value, "project id") if value is not None else None


class ProjectWrite(BaseModel):
    """Payload used to create a tracked project owned by a team member."""

    model_config = ConfigDict(extra="forbid")

    userId: str
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    technology: list[str] = Field(default_factory=list)
    status: str = "planned"

    @field_validator("name", "description")
    @classmethod
    def _clean_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value must contain non-whitespace characters.")
        return cleaned

    @field_validator("userId")
    @classmethod
    def _valid_user(cls, value: str) -> str:
        return validate_slug(value, "user id")

    @field_validator("status")
    @classmethod
    def _valid_status(cls, value: str) -> str:
        if value not in PROJECT_STATUSES:
            raise ValueError(f"Invalid project status {value!r}.")
        return value

    @field_validator("technology")
    @classmethod
    def _clean_technology(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if any(len(item) > 60 for item in cleaned):
            raise ValueError("Technology entries must be at most 60 characters long.")
        return cleaned


class ProjectResponse(BaseModel):
    id: str
    userId: str
    name: str
    description: str
    technology: list[str]
    status: str


class ErrorResponse(BaseModel):
    """Structured error envelope returned for non-2xx API responses."""

    error: str
    detail: str | None = None
