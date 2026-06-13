"""Unit tests for individual pipeline services."""
import ast

from app.pipeline.context import PipelineContext
from app.services.complexity_analyzer import ComplexityAnalyzer
from app.services.optimizer import Optimizer
from app.services.scorer import Scorer
from app.services.security_scanner import SecurityScanner
from app.services.syntax_checker import SyntaxChecker


def _context(code: str) -> PipelineContext:
    ctx = PipelineContext(code=code, language="python")
    return SyntaxChecker().run(ctx)


def test_syntax_checker_valid_code():
    ctx = _context("x = 1\n")
    assert ctx.valid_syntax is True
    assert isinstance(ctx.ast_tree, ast.AST)


def test_syntax_checker_invalid_code():
    ctx = _context("def f(:\n  pass")
    assert ctx.valid_syntax is False
    assert ctx.syntax_errors[0]["severity"] == "high"


def test_complexity_analyzer_nested_loops():
    code = (
        "def f(items):\n"
        "    for i in items:\n"
        "        for j in items:\n"
        "            print(i, j)\n"
    )
    ctx = _context(code)
    ctx = ComplexityAnalyzer().run(ctx)
    assert ctx.complexity["time"] == "O(n^2)"


def test_complexity_analyzer_recursion():
    code = (
        "def fib(n):\n"
        "    if n < 2:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 2)\n"
    )
    ctx = _context(code)
    ctx = ComplexityAnalyzer().run(ctx)
    assert ctx.complexity["time"] == "O(2^n)"


def test_security_scanner_flags_eval_and_secrets():
    code = (
        "API_KEY = \"abcd1234efgh\"\n"
        "result = eval(user_input)\n"
    )
    ctx = _context(code)
    ctx = SecurityScanner().run(ctx)
    issues = " ".join(i["issue"] for i in ctx.security_issues)
    assert "eval" in issues
    assert "secret" in issues.lower() or "credential" in issues.lower()


def test_optimizer_fixes_none_comparison_and_bare_except():
    code = (
        "def f(x):\n"
        "    if x == None:\n"
        "        return\n"
        "    try:\n"
        "        return 1 / x\n"
        "    except:\n"
        "        return 0\n"
    )
    ctx = _context(code)
    ctx = Optimizer().run(ctx)
    assert "is None" in ctx.optimized_code
    assert "except Exception" in ctx.optimized_code
    # optimized code must still be valid Python
    ast.parse(ctx.optimized_code)


def test_scorer_penalizes_high_severity_bugs():
    ctx = _context("x = 1\n")
    ctx.bugs = [{"line": 1, "issue": "bad", "severity": "high", "fix": "fix it"}]
    ctx.security_issues = []
    ctx.complexity = {"time": "O(1)", "space": "O(1)"}
    ctx = Scorer().run(ctx)
    assert ctx.score["correctness"] == 82
    assert ctx.score["overall"] < 100
