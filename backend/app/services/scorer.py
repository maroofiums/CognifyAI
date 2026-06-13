"""Final scoring stage: aggregates results from all pipeline stages into the
'score' block of the strict JSON response.

Each sub-score is on a 0-100 scale:
  - correctness:  penalized by bug count/severity
  - readability:  penalized by low-severity 'style' bugs, rewarded by docstring presence
  - security:     penalized by security findings, weighted by severity
  - performance:  derived from estimated time complexity
  - documentation: based on docstring coverage of functions/classes
  - overall:      weighted average of the above
"""
from __future__ import annotations

from app.pipeline.context import PipelineContext
from app.utils.helpers import clamp, get_class_defs, get_function_defs, has_docstring

_SEVERITY_PENALTY = {"low": 3, "medium": 8, "high": 18}

_TIME_COMPLEXITY_SCORE = {
    "O(1)": 100,
    "O(log n)": 95,
    "O(n)": 85,
    "O(n log n)": 75,
    "O(n^2)": 55,
    "O(n^3)": 35,
    "O(2^n)": 15,
}


class Scorer:
    """Computes the final score breakdown for an analysis."""

    name = "scorer"

    def run(self, context: PipelineContext) -> PipelineContext:
        correctness = self._score_from_issues(context.bugs)
        security = self._score_from_issues(context.security_issues)
        readability = self._readability_score(context)
        performance = _TIME_COMPLEXITY_SCORE.get(context.complexity.get("time", "O(n)"), 70)
        documentation = self._documentation_score(context)

        overall = (
            correctness * 0.30
            + security * 0.20
            + readability * 0.15
            + performance * 0.20
            + documentation * 0.15
        )

        context.score = {
            "correctness": round(correctness, 1),
            "readability": round(readability, 1),
            "security": round(security, 1),
            "performance": round(performance, 1),
            "documentation": round(documentation, 1),
            "overall": round(clamp(overall), 1),
        }
        return context

    @staticmethod
    def _score_from_issues(issues: list[dict]) -> float:
        score = 100.0
        for issue in issues:
            score -= _SEVERITY_PENALTY.get(issue.get("severity", "low"), 3)
        return clamp(score)

    @staticmethod
    def _readability_score(context: PipelineContext) -> float:
        score = 100.0
        low_severity_bugs = sum(1 for b in context.bugs if b.get("severity") == "low")
        score -= low_severity_bugs * 2
        if not context.valid_syntax:
            score = 0.0
        return clamp(score)

    @staticmethod
    def _documentation_score(context: PipelineContext) -> float:
        tree = context.ast_tree
        if tree is None:
            return 50.0

        functions = get_function_defs(tree)
        classes = get_class_defs(tree)
        targets = functions + classes

        if not targets:
            return 100.0 if has_docstring(tree) else 70.0

        documented = sum(1 for t in targets if has_docstring(t))
        coverage = documented / len(targets)
        return clamp(coverage * 100)
