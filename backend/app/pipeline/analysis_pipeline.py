"""Sequential AI analysis pipeline orchestrator.

Implements a LangChain-style chain-of-responsibility where each stage
receives the :class:`PipelineContext` produced by the previous stage and
returns an updated context. The strict order below MUST be preserved:

    1. SyntaxChecker
    2. BugDetector
    3. SecurityScanner
    4. ComplexityAnalyzer
    5. Optimizer
    6. DocstringGenerator
    7. Scorer (final aggregation)

Each stage is a small, independently testable class exposing a ``run``
method with the signature ``run(context: PipelineContext) -> PipelineContext``,
which makes the pipeline trivially extensible (e.g. adding a new stage is a
single line in ``self.stages``).
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from app.pipeline.context import PipelineContext
from app.services.bug_detector import BugDetector
from app.services.complexity_analyzer import ComplexityAnalyzer
from app.services.docstring_generator import DocstringGenerator
from app.services.optimizer import Optimizer
from app.services.scorer import Scorer
from app.services.security_scanner import SecurityScanner
from app.services.syntax_checker import SyntaxChecker


class AnalysisPipeline:
    """Runs the full, strictly-ordered code analysis pipeline."""

    def __init__(self) -> None:
        # Order matters: each stage depends on the output of the previous one.
        self.stages = [
            SyntaxChecker(),
            BugDetector(),
            SecurityScanner(),
            ComplexityAnalyzer(),
            Optimizer(),
            DocstringGenerator(),
            Scorer(),
        ]

    def run(self, code: str, language: str = "python", filename: str | None = None) -> PipelineContext:
        """Run all stages sequentially and return the final context."""
        context = PipelineContext(code=code, language=language, filename=filename)
        for stage in self.stages:
            context = stage.run(context)
            context.stages_completed.append(stage.name)
        return context

    def run_streaming(
        self, code: str, language: str = "python", filename: str | None = None
    ) -> Generator[dict[str, Any], None, None]:
        """Run all stages sequentially, yielding a status event before/after each stage.

        This generator is consumed by the streaming API endpoint to provide
        real-time progress updates to the frontend. The final event has
        ``type == "result"`` and carries the complete serialized context.
        """
        context = PipelineContext(code=code, language=language, filename=filename)

        for stage in self.stages:
            yield {"type": "stage", "stage": stage.name, "status": "running"}
            try:
                context = stage.run(context)
            except Exception as exc:  # pragma: no cover - defensive guard
                yield {"type": "stage", "stage": stage.name, "status": "error", "detail": str(exc)}
                raise
            context.stages_completed.append(stage.name)
            yield {"type": "stage", "stage": stage.name, "status": "done"}

        yield {"type": "result", "data": context.to_result_dict()}
