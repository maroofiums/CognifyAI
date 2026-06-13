"""Shared mutable state passed sequentially between pipeline stages."""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PipelineContext:
    """Carries the original input plus accumulated results through the pipeline.

    Each stage reads what previous stages have written and appends its own
    results, enforcing the strict sequential dependency required by the
    analysis pipeline.
    """

    code: str
    language: str = "python"
    filename: Optional[str] = None

    # Stage 1: syntax_checker
    ast_tree: Optional[ast.AST] = None
    valid_syntax: bool = True
    syntax_errors: list[dict[str, Any]] = field(default_factory=list)

    # Stage 2: bug_detector
    bugs: list[dict[str, Any]] = field(default_factory=list)

    # Stage 3: security_scanner
    security_issues: list[dict[str, Any]] = field(default_factory=list)

    # Stage 4: complexity_analyzer
    complexity: dict[str, str] = field(default_factory=lambda: {"time": "O(n)", "space": "O(1)"})

    # Stage 5: optimizer
    optimized_code: str = ""

    # Stage 6: docstring_generator
    docstring: str = ""

    # Final scoring
    score: dict[str, float] = field(default_factory=dict)

    # Bookkeeping
    stages_completed: list[str] = field(default_factory=list)

    def to_result_dict(self) -> dict[str, Any]:
        """Serialize the context into the strict AnalysisResult JSON shape."""
        return {
            "bugs": self.bugs,
            "security_issues": self.security_issues,
            "complexity": self.complexity,
            "optimized_code": self.optimized_code,
            "docstring": self.docstring,
            "score": self.score,
        }
