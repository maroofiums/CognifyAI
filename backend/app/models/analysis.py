"""SQLAlchemy ORM model for stored code analysis results."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Analysis(Base):
    """Represents a single AI code analysis run, persisted for history lookups."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    language: Mapped[str] = mapped_column(String(32), default="python")
    filename: Mapped[str] = mapped_column(String(255), nullable=True)

    original_code: Mapped[str] = mapped_column(Text)
    optimized_code: Mapped[str] = mapped_column(Text)
    docstring: Mapped[str] = mapped_column(Text)

    bugs: Mapped[list] = mapped_column(JSON, default=list)
    security_issues: Mapped[list] = mapped_column(JSON, default=list)
    complexity: Mapped[dict] = mapped_column(JSON, default=dict)
    score: Mapped[dict] = mapped_column(JSON, default=dict)

    overall_score: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
