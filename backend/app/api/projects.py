"""Project routes."""

from fastapi import APIRouter

from ...schemas.api import ProjectResponse
from ...services import queries

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects() -> list[ProjectResponse]:
    """List registered member projects."""
    return queries.list_projects()
