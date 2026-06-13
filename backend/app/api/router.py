"""Aggregates all API routers under a single prefix."""
from fastapi import APIRouter

from app.api.routes import analysis, health, history

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(analysis.router)
api_router.include_router(history.router)
