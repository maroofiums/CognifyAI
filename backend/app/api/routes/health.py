"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness probe used by Docker healthchecks and uptime monitors."""
    return {"status": "ok", "service": "CognifyAI"}
