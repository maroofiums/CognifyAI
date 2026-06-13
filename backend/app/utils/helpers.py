"""Small shared helper functions used across pipeline services."""
import ast
import json
import re
from typing import Any, Optional


def safe_json_loads(raw: str) -> Optional[dict]:
    """Best-effort JSON parsing of LLM output.

    Strips markdown code fences (```json ... ```) if present and tries to
    locate the first top-level JSON object if extra text surrounds it.
    """
    if not raw:
        return None

    text = raw.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back: find the first balanced {...} block
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for idx in range(start, len(text)):
        if text[idx] == "{":
            depth += 1
        elif text[idx] == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start: idx + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


def get_function_defs(tree: ast.AST) -> list[ast.FunctionDef]:
    """Return all top-level and nested function definitions in an AST tree."""
    return [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def get_class_defs(tree: ast.AST) -> list[ast.ClassDef]:
    """Return all class definitions in an AST tree."""
    return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def has_docstring(node: ast.AST) -> bool:
    """Check whether a module/function/class node has a docstring."""
    return ast.get_docstring(node) is not None


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def truncate(text: str, length: int = 160) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= length else text[: length - 1] + "..."


def code_to_snippet(code: str, lines: int = 3) -> str:
    return "\n".join(code.strip().splitlines()[:lines])
