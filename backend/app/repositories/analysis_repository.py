"""Data-access layer for the Analysis model.

Keeps SQLAlchemy query logic out of the route/service layers, following the
routes -> services -> pipeline -> database layering described in the
architecture docs.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.pipeline.context import PipelineContext
from app.utils.helpers import code_to_snippet


class AnalysisRepository:
    """CRUD operations for :class:`Analysis` records."""

    def create_from_context(self, db: Session, context: PipelineContext) -> Analysis:
        record = Analysis(
            language=context.language,
            filename=context.filename,
            original_code=context.code,
            optimized_code=context.optimized_code,
            docstring=context.docstring,
            bugs=context.bugs,
            security_issues=context.security_issues,
            complexity=context.complexity,
            score=context.score,
            overall_score=context.score.get("overall", 0.0),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get(self, db: Session, analysis_id: str) -> Analysis | None:
        return db.get(Analysis, analysis_id)

    def list(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[list[Analysis], int]:
        total_count = db.query(Analysis).count()
        items = (
            db.query(Analysis)
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total_count

    @staticmethod
    def to_snippet(record: Analysis) -> str:
        return code_to_snippet(record.original_code)
