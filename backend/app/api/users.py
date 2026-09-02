"""User routes."""

from fastapi import APIRouter

from ...schemas.api import UserResponse
from ...services import queries

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users() -> list[UserResponse]:
    """List all team members."""
    return queries.list_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str) -> UserResponse:
    """Return one team member, or 404 if the user does not exist."""
    return queries.get_user(user_id)
