"""Stage 4: Complexity analysis (Big-O time/space).

Depends on Stages 1-3. Estimates time and space complexity using AST-based
heuristics: nested loop depth drives the time complexity estimate, and the
presence of growing data structures (lists/dicts/sets built inside loops)
drives the space complexity estimate. Recursive functions are detected and
bumped to exponential time unless memoization is present.

When LLM enrichment is enabled, the heuristic result is used as a fallback
if the LLM does not return a parseable response.
"""
from __future__ import annotations

import ast

from app.llm.client import call_llm_json
from app.pipeline.context import PipelineContext
from app.utils.prompts import COMPLEXITY_PROMPT

_ORDER = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]


class ComplexityAnalyzer:
    """Estimates Big-O time and space complexity of the analyzed code."""

    name = "complexity_analyzer"

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.valid_syntax or context.ast_tree is None:
            context.complexity = {"time": "unknown", "space": "unknown"}
            return context

        heuristic = self._heuristic_complexity(context.ast_tree)

        if context.language.lower() == "python":
            llm_result = self._llm_complexity(context)
            if llm_result and "time" in llm_result and "space" in llm_result:
                context.complexity = {"time": str(llm_result["time"]), "space": str(llm_result["space"])}
                return context

        context.complexity = heuristic
        return context

    def _heuristic_complexity(self, tree: ast.AST) -> dict[str, str]:
        # Consider the whole module (covers top-level loops) as well as
        # each function body individually (covers loops inside functions).
        max_depth = self._max_loop_depth(tree)
        has_recursion = False
        has_growing_structure = self._has_append_in_loop(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                max_depth = max(max_depth, self._max_loop_depth(node))
                if self._is_recursive(node):
                    has_recursion = True
                if self._has_append_in_loop(node):
                    has_growing_structure = True

        if has_recursion:
            time_complexity = "O(2^n)"
        elif max_depth >= 3:
            time_complexity = "O(n^3)"
        elif max_depth == 2:
            time_complexity = "O(n^2)"
        elif max_depth == 1:
            time_complexity = "O(n)"
        else:
            time_complexity = "O(1)"

        space_complexity = "O(n)" if (has_growing_structure or has_recursion) else "O(1)"

        return {"time": time_complexity, "space": space_complexity}

    def _max_loop_depth(self, node: ast.AST, current: int = 0) -> int:
        max_depth = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                depth = self._max_loop_depth(child, current + 1)
            else:
                depth = self._max_loop_depth(child, current)
            max_depth = max(max_depth, depth)
        return max_depth

    def _is_recursive(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                name = None
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                if name == func.name:
                    return True
        return False

    def _has_append_in_loop(self, func: ast.AST) -> bool:
        for node in ast.walk(func):
            if isinstance(node, (ast.For, ast.While)):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
                        if inner.func.attr in {"append", "add", "update", "extend"}:
                            return True
                    if isinstance(inner, (ast.ListComp, ast.DictComp, ast.SetComp)):
                        return True
        return False

    def _llm_complexity(self, context: PipelineContext) -> dict | None:
        prompt = COMPLEXITY_PROMPT.format(language=context.language, code=context.code)
        return call_llm_json(prompt)
