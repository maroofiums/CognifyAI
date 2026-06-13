"""Routes for browsing previously stored analyses."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analysis import AnalysisResult, AnalyzeResponse
from app.schemas.response import HistoryItem, HistoryResponse
from app.services.analyzer import AnalyzerService

router = APIRouter(tags=["history"])
service = AnalyzerService()


@router.get("/history", response_model=HistoryResponse)
def get_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    """Return a paginated list of past analyses, most recent first."""
    items, total = service.list(db, skip=skip, limit=limit)

    history_items = [
        HistoryItem(
            id=record.id,
            created_at=record.created_at,
            language=record.language,
            filename=record.filename,
            overall_score=record.overall_score,
            snippet=service.to_snippet(record),
        )
        for record in items
    ]
    return HistoryResponse(total=total, items=history_items)


@router.get("/analysis/{analysis_id}", response_model=AnalyzeResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> AnalyzeResponse:
    """Fetch a single stored analysis by id."""
    record = service.get(db, analysis_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    result = AnalysisResult(
        bugs=record.bugs,
        security_issues=record.security_issues,
        complexity=record.complexity,
        optimized_code=record.optimized_code,
        docstring=record.docstring,
        score=record.score,
    )
    return AnalyzeResponse(id=record.id, created_at=record.created_at, result=result)
