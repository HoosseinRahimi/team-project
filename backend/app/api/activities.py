"""Activity routes."""

from fastapi import APIRouter, Response, status

from ...schemas.api import ActivityResponse, ActivityWrite
from ...services import activity_writes, queries

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=list[ActivityResponse])
def list_activities() -> list[ActivityResponse]:
    return queries.list_activities()


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(payload: ActivityWrite) -> ActivityResponse:
    return activity_writes.create_activity(payload)


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: str, payload: ActivityWrite) -> ActivityResponse:
    return activity_writes.update_activity(activity_id, payload)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: str) -> Response:
    activity_writes.delete_activity(activity_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
