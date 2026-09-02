"""Health route."""

from fastapi import APIRouter

from ...schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Simple liveness check for the backend."""
    return HealthResponse(status="ok")


@router.get("/health", response_model=HealthResponse, include_in_schema=False)
def legacy_health_check() -> HealthResponse:
    """Backwards-compatible alias for /api/health."""
    return HealthResponse(status="ok")
