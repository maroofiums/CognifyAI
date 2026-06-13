"""Lightweight typed structure mirroring the 'score' JSON block.

Kept separate from app.schemas so it can be reused by services without
importing the full Pydantic schema layer.
"""
from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    correctness: float
    readability: float
    security: float
    performance: float
    documentation: float
    overall: float

    def to_dict(self) -> dict:
        return {
            "correctness": self.correctness,
            "readability": self.readability,
            "security": self.security,
            "performance": self.performance,
            "documentation": self.documentation,
            "overall": self.overall,
        }
