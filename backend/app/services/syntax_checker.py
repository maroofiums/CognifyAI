"""Stage 1: Syntax validation.

Parses the submitted source code using Python's ``ast`` module. If parsing
fails, a single high-severity bug entry describing the syntax error is
recorded and ``valid_syntax`` is set to ``False`` so downstream stages can
skip AST-dependent analysis gracefully.
"""
from __future__ import annotations

import ast

from app.pipeline.context import PipelineContext


class SyntaxChecker:
    """Validates that the submitted code can be parsed."""

    name = "syntax_checker"

    def run(self, context: PipelineContext) -> PipelineContext:
        if context.language.lower() != "python":
            # Non-Python languages skip AST-based analysis entirely but the
            # pipeline still proceeds with text-based heuristics downstream.
            context.valid_syntax = True
            context.ast_tree = None
            context.syntax_errors = []
            return context

        try:
            tree = ast.parse(context.code)
            context.ast_tree = tree
            context.valid_syntax = True
            context.syntax_errors = []
        except SyntaxError as exc:
            context.ast_tree = None
            context.valid_syntax = False
            context.syntax_errors = [
                {
                    "line": exc.lineno or 1,
                    "issue": f"SyntaxError: {exc.msg}",
                    "severity": "high",
                    "fix": "Fix the syntax error before the code can be analyzed further.",
                }
            ]

        return context
