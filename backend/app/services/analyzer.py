"""Service layer: orchestrates the analysis pipeline and persistence.

This is the boundary between the API routes and the lower-level pipeline /
repository layers (routes -> services -> pipeline -> database).
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.pipeline.analysis_pipeline import AnalysisPipeline
from app.repositories.analysis_repository import AnalysisRepository

_pipeline = AnalysisPipeline()
_repository = AnalysisRepository()


class AnalyzerService:
    """High-level API used by route handlers to run and persist analyses."""

    def analyze_and_store(self, db: Session, code: str, language: str, filename: str | None) -> Analysis:
        """Run the full pipeline synchronously and persist the result."""
        context = _pipeline.run(code=code, language=language, filename=filename)
        return _repository.create_from_context(db, context)

    def analyze_streaming(
        self, db: Session, code: str, language: str, filename: str | None
    ) -> Generator[dict[str, Any], None, None]:
        """Run the pipeline yielding progress events, persisting the result once complete.

        Yields NDJSON-serializable dicts. The final event includes the
        persisted record's ``id`` and ``created_at`` alongside the result.
        """
        from app.pipeline.context import PipelineContext

        context = PipelineContext(code=code, language=language, filename=filename)

        for stage in _pipeline.stages:
            yield {"type": "stage", "stage": stage.name, "status": "running"}
            context = stage.run(context)
            context.stages_completed.append(stage.name)
            yield {"type": "stage", "stage": stage.name, "status": "done"}

        record = _repository.create_from_context(db, context)

        yield {
            "type": "result",
            "data": {
                "id": record.id,
                "created_at": record.created_at.isoformat(),
                "result": context.to_result_dict(),
            },
        }

    def get(self, db: Session, analysis_id: str) -> Analysis | None:
        return _repository.get(db, analysis_id)

    def list(self, db: Session, skip: int, limit: int) -> tuple[list[Analysis], int]:
        return _repository.list(db, skip=skip, limit=limit)

    @staticmethod
    def to_snippet(record: Analysis) -> str:
        return _repository.to_snippet(record)
