"""Tests for the sequential analysis pipeline."""
from app.pipeline.analysis_pipeline import AnalysisPipeline

GOOD_CODE = '''
def add(a, b):
    """Add two numbers."""
    return a + b
'''

BUGGY_CODE = '''
def divide(total, count):
    result = total / count
    return result

def append_item(item, items=[]):
    items.append(item)
    return items

try:
    x = 1 / 0
except:
    pass
'''

BAD_SYNTAX_CODE = "def broken(:\n    pass"

INSECURE_CODE = '''
import os

def run(cmd):
    os.system(cmd)
    eval("print(1)")
    password = "supersecret123"
    return password
'''


def test_pipeline_runs_in_order_for_valid_code():
    pipeline = AnalysisPipeline()
    context = pipeline.run(GOOD_CODE, language="python")

    assert context.valid_syntax is True
    assert context.stages_completed == [
        "syntax_checker",
        "bug_detector",
        "security_scanner",
        "complexity_analyzer",
        "optimizer",
        "docstring_generator",
        "scorer",
    ]
    assert context.complexity["time"] == "O(1)"
    assert "docstring" in context.docstring or context.docstring.startswith('"""')
    assert 0 <= context.score["overall"] <= 100


def test_pipeline_detects_bugs():
    pipeline = AnalysisPipeline()
    context = pipeline.run(BUGGY_CODE, language="python")

    assert context.valid_syntax is True
    issues = " ".join(b["issue"] for b in context.bugs)
    assert "mutable default argument" in issues
    assert "Bare 'except:'" in issues
    assert any(b["severity"] == "high" for b in context.bugs)


def test_pipeline_handles_syntax_errors():
    pipeline = AnalysisPipeline()
    context = pipeline.run(BAD_SYNTAX_CODE, language="python")

    assert context.valid_syntax is False
    assert context.bugs[0]["severity"] == "high"
    assert context.score["correctness"] == 0 or context.score["overall"] < 100
    # Downstream stages should not crash even though syntax is invalid
    assert context.optimized_code == BAD_SYNTAX_CODE
    assert context.complexity == {"time": "unknown", "space": "unknown"}


def test_pipeline_detects_security_issues():
    pipeline = AnalysisPipeline()
    context = pipeline.run(INSECURE_CODE, language="python")

    issues = " ".join(s["issue"] for s in context.security_issues)
    assert "os.system" in issues
    assert "eval" in issues
    assert "Hardcoded credential" in issues
    assert context.score["security"] < 100


def test_streaming_emits_stage_events_then_result():
    pipeline = AnalysisPipeline()
    events = list(pipeline.run_streaming(GOOD_CODE, language="python"))

    stage_events = [e for e in events if e["type"] == "stage"]
    result_events = [e for e in events if e["type"] == "result"]

    assert len(result_events) == 1
    assert "score" in result_events[0]["data"]

    # Each stage should emit a "running" then "done" event, in order
    stage_names = [e["stage"] for e in stage_events if e["status"] == "done"]
    assert stage_names == [
        "syntax_checker",
        "bug_detector",
        "security_scanner",
        "complexity_analyzer",
        "optimizer",
        "docstring_generator",
        "scorer",
    ]
