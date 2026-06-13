"""Pydantic schemas for list/history style responses."""
from datetime import datetime
from typing import List

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: str
    created_at: datetime
    language: str
    filename: str | None = None
    overall_score: float
    snippet: str

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    total: int
    items: List[HistoryItem]


class StageEvent(BaseModel):
    """Streaming event emitted while the pipeline executes a stage."""

    type: str = "stage"
    stage: str
    status: str  # "running" | "done" | "error"
    detail: str | None = None
