"""Pydantic schema for the score breakdown block."""
from pydantic import BaseModel, Field


class ScoreSchema(BaseModel):
    correctness: float = Field(ge=0, le=100)
    readability: float = Field(ge=0, le=100)
    security: float = Field(ge=0, le=100)
    performance: float = Field(ge=0, le=100)
    documentation: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)
