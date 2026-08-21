from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


def create_health_router(service_name: str) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="UP", service=service_name, timestamp=datetime.now(timezone.utc))

    @router.get("/ready", response_model=HealthResponse)
    async def ready() -> HealthResponse:
        return HealthResponse(status="UP", service=service_name, timestamp=datetime.now(timezone.utc))

    return router
