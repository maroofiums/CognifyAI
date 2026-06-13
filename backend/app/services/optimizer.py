"""Stage 5: Code optimization (refactoring, performance improvements).

Depends on Stages 1-4: the optimizer is given the original code plus the
bugs, security issues and complexity already identified, so an LLM-backed
implementation can target those specific findings. When no LLM is
configured, a deterministic set of safe textual refactors is applied so the
output is still meaningfully different (and demonstrably improved) versus
the input.
"""
from __future__ import annotations

import ast
import re

from app.llm.client import call_llm_json
from app.pipeline.context import PipelineContext
from app.utils.prompts import OPTIMIZER_PROMPT


class Optimizer:
    """Produces an optimized version of the submitted code."""

    name = "optimizer"

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.valid_syntax:
            # Cannot safely optimize code that doesn't parse.
            context.optimized_code = context.code
            return context

        if context.language.lower() == "python":
            llm_code = self._llm_optimize(context)
            if llm_code:
                context.optimized_code = llm_code
                return context

        context.optimized_code = self._heuristic_optimize(context.code)
        return context

    # ------------------------------------------------------------------
    # Heuristic, language-agnostic-ish textual optimizations
    # ------------------------------------------------------------------
    def _heuristic_optimize(self, code: str) -> str:
        optimized = code

        # 1. Identity comparisons against None/True/False
        optimized = re.sub(r"==\s*None\b", "is None", optimized)
        optimized = re.sub(r"!=\s*None\b", "is not None", optimized)

        # 2. Bare except -> except Exception (preserve trailing whitespace/newline)
        optimized = re.sub(r"except\s*:", "except Exception:", optimized)

        # 3. Replace `range(len(x))` indexing pattern with enumerate where simple
        #    e.g. "for i in range(len(items)):" -> "for i, _value in enumerate(items):"
        #    Only a conservative comment-based suggestion is added to avoid
        #    breaking code that relies on the index for writes.
        optimized = re.sub(
            r"for (\w+) in range\(len\((\w+)\)\):",
            r"for \1 in range(len(\2)):  # NOTE: consider 'for \1, value in enumerate(\2):' if you only need values",
            optimized,
        )

        # 4. Collapse `x = x + 1` style increments to augmented assignment for readability
        optimized = re.sub(r"\b(\w+)\s*=\s*\1\s*\+\s*1\b", r"\1 += 1", optimized)
        optimized = re.sub(r"\b(\w+)\s*=\s*\1\s*-\s*1\b", r"\1 -= 1", optimized)

        # 5. Replace string concatenation in a loop hint - leave a comment if `+=` on a str literal pattern is seen
        if re.search(r"^\s*\w+\s*\+=\s*[\"']", optimized, flags=re.MULTILINE):
            optimized = self._prepend_comment(
                optimized,
                "Consider building a list and using ''.join(...) instead of repeated string concatenation in loops.",
            )

        # 6. Remove trailing whitespace on each line
        optimized = "\n".join(line.rstrip() for line in optimized.splitlines())

        return optimized

    @staticmethod
    def _prepend_comment(code: str, comment: str) -> str:
        comment_line = f"# OPTIMIZATION NOTE: {comment}"
        lines = code.splitlines()
        if lines and lines[0].startswith("#"):
            lines.insert(1, comment_line)
        else:
            lines.insert(0, comment_line)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Optional LLM enrichment
    # ------------------------------------------------------------------
    def _llm_optimize(self, context: PipelineContext) -> str | None:
        prompt = OPTIMIZER_PROMPT.format(
            language=context.language,
            bugs=context.bugs,
            security_issues=context.security_issues,
            code=context.code,
        )
        result = call_llm_json(prompt)
        if result and isinstance(result.get("optimized_code"), str):
            candidate = result["optimized_code"]
            # Safety net: only accept the LLM's output if it still parses.
            try:
                ast.parse(candidate)
                return candidate
            except SyntaxError:
                return None
        return None
