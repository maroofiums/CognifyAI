"""Stage 2: Bug detection (logic + runtime issues).

Depends on Stage 1 (syntax_checker). If the code failed to parse, the
syntax errors detected in Stage 1 are surfaced here as the bug list and no
further AST analysis is attempted.

When LLM enrichment is enabled, the heuristic findings are merged with
LLM-suggested findings (deduplicated by line + issue).
"""
from __future__ import annotations

import ast

from app.llm.client import call_llm_json
from app.pipeline.context import PipelineContext
from app.utils.prompts import BUG_DETECTION_PROMPT


class BugDetector:
    """Finds common logic/runtime bugs via static AST heuristics."""

    name = "bug_detector"

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.valid_syntax:
            context.bugs = list(context.syntax_errors)
            return context

        bugs: list[dict] = []

        if context.ast_tree is not None:
            bugs.extend(self._heuristic_checks(context.ast_tree, context.code))

        if context.language.lower() == "python":
            llm_bugs = self._llm_bugs(context)
            bugs.extend(self._dedupe(bugs, llm_bugs))

        context.bugs = bugs
        return context

    # ------------------------------------------------------------------
    # Heuristic (AST-based) checks
    # ------------------------------------------------------------------
    def _heuristic_checks(self, tree: ast.AST, code: str) -> list[dict]:
        bugs: list[dict] = []

        for node in ast.walk(tree):
            # Bare `except:` swallows everything including KeyboardInterrupt
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                bugs.append({
                    "line": node.lineno,
                    "issue": "Bare 'except:' clause catches all exceptions, including system-exiting ones.",
                    "severity": "medium",
                    "fix": "Catch a specific exception type, e.g. 'except Exception as exc:'.",
                })

            # Mutable default arguments (list/dict/set literals)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in list(node.args.defaults) + list(node.args.kw_defaults):
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        bugs.append({
                            "line": node.lineno,
                            "issue": f"Function '{node.name}' uses a mutable default argument, which is shared across calls.",
                            "severity": "high",
                            "fix": "Use 'None' as the default and initialize the mutable value inside the function body.",
                        })

            # Comparisons to None/True/False using == or !=
            if isinstance(node, ast.Compare):
                for op, comparator in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant):
                        if comparator.value is None or isinstance(comparator.value, bool):
                            symbol = "==" if isinstance(op, ast.Eq) else "!="
                            replacement = "is" if isinstance(op, ast.Eq) else "is not"
                            bugs.append({
                                "line": node.lineno,
                                "issue": f"Used '{symbol}' to compare against {comparator.value!r}; identity comparison is preferred.",
                                "severity": "low",
                                "fix": f"Use '{replacement} {comparator.value!r}' instead of '{symbol} {comparator.value!r}'.",
                            })

            # Loop variable shadowed and unused / `for _ in` style not used - skip false positives,
            # but flag re-assignment of the loop variable inside the loop body which often hides bugs.
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                loop_var = node.target.id
                for child in node.body:
                    for sub in ast.walk(child):
                        if isinstance(sub, ast.Assign):
                            for tgt in sub.targets:
                                if isinstance(tgt, ast.Name) and tgt.id == loop_var:
                                    bugs.append({
                                        "line": sub.lineno,
                                        "issue": f"Loop variable '{loop_var}' is reassigned inside the loop body, which can cause confusing iteration behaviour.",
                                        "severity": "low",
                                        "fix": f"Use a different variable name for the reassigned value instead of overwriting '{loop_var}'.",
                                    })

            # Division that could raise ZeroDivisionError on a variable denominator
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Name):
                    bugs.append({
                        "line": node.lineno,
                        "issue": f"Possible division by zero: '{node.right.id}' is not validated before being used as a divisor.",
                        "severity": "medium",
                        "fix": f"Add a guard such as 'if {node.right.id} != 0:' before performing the division.",
                    })

            # Using assert for input validation (asserts are stripped with -O)
            if isinstance(node, ast.Assert):
                bugs.append({
                    "line": node.lineno,
                    "issue": "'assert' is used for validation; assertions are removed when Python runs with -O.",
                    "severity": "low",
                    "fix": "Raise an explicit exception (e.g. ValueError) for input validation instead of 'assert'.",
                })

        return bugs

    # ------------------------------------------------------------------
    # Optional LLM enrichment
    # ------------------------------------------------------------------
    def _llm_bugs(self, context: PipelineContext) -> list[dict]:
        prompt = BUG_DETECTION_PROMPT.format(language=context.language, code=context.code)
        result = call_llm_json(prompt)
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        if isinstance(result, dict) and isinstance(result.get("bugs"), list):
            return result["bugs"]
        return []

    @staticmethod
    def _dedupe(existing: list[dict], candidates: list[dict]) -> list[dict]:
        seen = {(b.get("line"), b.get("issue")) for b in existing}
        unique = []
        for c in candidates:
            key = (c.get("line"), c.get("issue"))
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique
