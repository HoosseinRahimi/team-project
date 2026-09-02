"""Pydantic contracts for the public API. ISO 8601 is used for dates."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .source_data import ACTIVITY_STATUSES, validate_date_string, validate_slug


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
