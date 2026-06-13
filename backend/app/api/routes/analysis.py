"""Routes for running and retrieving code analyses."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, AnalysisResult
from app.services.analyzer import AnalyzerService

router = APIRouter(tags=["analysis"])
service = AnalyzerService()


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
def analyze_code(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> AnalyzeResponse:
    """Run the full sequential AI pipeline on the submitted code and persist the result."""
    if not payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code must not be empty.")

    record = service.analyze_and_store(db, code=payload.code, language=payload.language, filename=payload.filename)

    result = AnalysisResult(
        bugs=record.bugs,
        security_issues=record.security_issues,
        complexity=record.complexity,
        optimized_code=record.optimized_code,
        docstring=record.docstring,
        score=record.score,
    )
    return AnalyzeResponse(id=record.id, created_at=record.created_at, result=result)


@router.post("/analyze/stream")
def analyze_code_stream(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    """Run the pipeline, streaming newline-delimited JSON progress events.

    Each line is a JSON object. Intermediate lines have ``"type": "stage"``
    with ``stage`` and ``status`` ("running"/"done"). The final line has
    ``"type": "result"`` and carries the persisted analysis id plus the full
    :class:`AnalysisResult` payload.
    """
    if not payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code must not be empty.")

    def event_stream():
        for event in service.analyze_streaming(db, code=payload.code, language=payload.language, filename=payload.filename):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
