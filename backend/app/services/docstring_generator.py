"""Stage 6: Auto docstring generation.

Depends on Stages 1-5 (the final stage of the pipeline). Generates a
concise module-level docstring summarizing the (optimized) code: its
purpose, the functions/classes it defines, and notable findings from
earlier stages (bugs fixed, security issues addressed, complexity).

Falls back to a deterministic template-based summary when no LLM is
configured.
"""
from __future__ import annotations

import ast

from app.llm.client import call_llm_json
from app.pipeline.context import PipelineContext
from app.utils.helpers import get_class_defs, get_function_defs
from app.utils.prompts import DOCSTRING_PROMPT


class DocstringGenerator:
    """Generates a summary docstring for the analyzed module."""

    name = "docstring_generator"

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.valid_syntax:
            context.docstring = (
                '"""This module could not be parsed due to a syntax error and was not documented."""'
            )
            return context

        if context.language.lower() == "python":
            llm_doc = self._llm_docstring(context)
            if llm_doc:
                context.docstring = self._wrap(llm_doc)
                return context

        context.docstring = self._wrap(self._heuristic_docstring(context))
        return context

    def _heuristic_docstring(self, context: PipelineContext) -> str:
        tree = context.ast_tree
        if tree is None:
            return "This module contains source code that was analyzed by CognifyAI."

        functions = [f.name for f in get_function_defs(tree)]
        classes = [c.name for c in get_class_defs(tree)]

        parts: list[str] = []

        if classes and functions:
            parts.append(
                f"This module defines {len(classes)} class(es) ({', '.join(classes[:5])}) "
                f"and {len(functions)} function(s) ({', '.join(functions[:5])})."
            )
        elif classes:
            parts.append(f"This module defines {len(classes)} class(es): {', '.join(classes[:5])}.")
        elif functions:
            parts.append(f"This module defines {len(functions)} function(s): {', '.join(functions[:5])}.")
        else:
            parts.append("This module contains top-level script logic with no function or class definitions.")

        if context.bugs:
            high = sum(1 for b in context.bugs if b.get("severity") == "high")
            parts.append(
                f"Static analysis identified {len(context.bugs)} potential bug(s)"
                + (f", including {high} high-severity issue(s)." if high else ".")
            )
        else:
            parts.append("No bugs were identified during static analysis.")

        if context.security_issues:
            parts.append(f"{len(context.security_issues)} security finding(s) were flagged for review.")
        else:
            parts.append("No security issues were detected.")

        parts.append(
            f"Estimated complexity is {context.complexity.get('time', 'unknown')} time and "
            f"{context.complexity.get('space', 'unknown')} space."
        )

        return " ".join(parts)

    def _llm_docstring(self, context: PipelineContext) -> str | None:
        prompt = DOCSTRING_PROMPT.format(language=context.language, code=context.optimized_code or context.code)
        result = call_llm_json(prompt)
        if result and isinstance(result.get("docstring"), str):
            return result["docstring"].strip()
        return None

    @staticmethod
    def _wrap(text: str) -> str:
        text = text.strip()
        if text.startswith('"""') and text.endswith('"""'):
            return text
        return f'"""{text}"""'
