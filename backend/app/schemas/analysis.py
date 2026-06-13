"""Pydantic request/response schemas for the analysis pipeline."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.score import ScoreSchema


class AnalyzeRequest(BaseModel):
    """Payload sent by the client to trigger an analysis."""

    code: str = Field(..., min_length=1, description="Raw source code to analyze")
    language: str = Field(default="python", description="Source language (currently 'python' is fully supported)")
    filename: Optional[str] = Field(default=None, description="Optional filename for context")


class BugItem(BaseModel):
    line: int
    issue: str
    severity: Literal["low", "medium", "high"]
    fix: str


class SecurityIssueItem(BaseModel):
    line: int
    issue: str
    severity: Literal["low", "medium", "high"]
    fix: str


class ComplexitySchema(BaseModel):
    time: str
    space: str


class AnalysisResult(BaseModel):
    """The strict JSON structure produced by the AI pipeline."""

    bugs: List[BugItem] = Field(default_factory=list)
    security_issues: List[SecurityIssueItem] = Field(default_factory=list)
    complexity: ComplexitySchema
    optimized_code: str
    docstring: str
    score: ScoreSchema


class AnalysisRecord(AnalysisResult):
    """Analysis result enriched with persistence metadata."""

    id: str
    language: str
    filename: Optional[str] = None
    original_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    id: str
    created_at: datetime
    result: AnalysisResult
