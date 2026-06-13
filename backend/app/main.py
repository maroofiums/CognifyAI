"""CognifyAI FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database schema on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered code analysis, optimization and documentation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.PROJECT_NAME, "status": "running", "docs": "/docs"}
