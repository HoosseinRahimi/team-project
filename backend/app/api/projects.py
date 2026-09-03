"""Project routes."""

from fastapi import APIRouter, status

from ...schemas.api import ProjectResponse, ProjectWrite
from ...services import project_writes, queries

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects() -> list[ProjectResponse]:
    """List registered member projects."""
    return queries.list_projects()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectWrite) -> ProjectResponse:
    """Create a tracked project owned by a team member."""
    return project_writes.create_project(payload)
