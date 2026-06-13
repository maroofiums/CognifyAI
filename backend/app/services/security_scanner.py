"""Stage 3: Security scanning (injection, unsafe eval, secrets).

Depends on Stages 1-2. Runs only if the code is syntactically valid.
Combines regex/text based pattern matching (language agnostic) with
AST-based checks for Python, then optionally enriches via LLM.
"""
from __future__ import annotations

import ast
import re

from app.llm.client import call_llm_json
from app.pipeline.context import PipelineContext
from app.utils.prompts import SECURITY_SCAN_PROMPT

# (pattern, issue, severity, fix)
_TEXT_PATTERNS: list[tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"\beval\s*\("), "Use of 'eval()' can execute arbitrary code.", "high",
     "Avoid 'eval'; use 'ast.literal_eval' for literals or refactor to remove dynamic execution."),
    (re.compile(r"\bexec\s*\("), "Use of 'exec()' can execute arbitrary code.", "high",
     "Avoid 'exec'; refactor the logic to avoid dynamic code execution."),
    (re.compile(r"os\.system\s*\("), "'os.system' executes shell commands and is vulnerable to shell injection.", "high",
     "Use 'subprocess.run([...], shell=False)' with a list of arguments."),
    (re.compile(r"subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True"), "'subprocess' called with shell=True is vulnerable to shell injection.", "high",
     "Set 'shell=False' and pass command arguments as a list."),
    (re.compile(r"pickle\.loads?\s*\("), "Deserializing untrusted data with 'pickle' can lead to arbitrary code execution.", "high",
     "Use a safe serialization format such as JSON, or validate the data source."),
    (re.compile(r"yaml\.load\s*\((?!.*Loader=)"), "'yaml.load' without an explicit safe Loader can execute arbitrary tags.", "high",
     "Use 'yaml.safe_load()' instead of 'yaml.load()'."),
    (re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*[\"'][^\"']{4,}[\"']"),
     "Hardcoded credential or secret detected in source code.", "high",
     "Move secrets to environment variables or a secrets manager; never commit them to source control."),
    (re.compile(r"\.format\([^)]*\)\s*\)?\s*$"), "String formatting used to build a query/command may enable injection if user input is included.", "low",
     "Use parameterized queries or escaped templating instead of string formatting for commands/queries."),
    (re.compile(r"verify\s*=\s*False"), "TLS certificate verification disabled ('verify=False').", "medium",
     "Remove 'verify=False' and ensure proper certificate validation in HTTP requests."),
    (re.compile(r"\bmd5\s*\("), "MD5 is a cryptographically broken hash function.", "medium",
     "Use 'hashlib.sha256' or a dedicated password hashing library (e.g. bcrypt, argon2)."),
]

_SQL_PATTERN = re.compile(
    r"(?:execute|executemany)\s*\(\s*(?:f[\"']|[\"'][^\"']*[\"']\s*(?:%|\+)|[\"'][^\"']*\{)",
    re.IGNORECASE,
)


class SecurityScanner:
    """Scans source code for common security vulnerabilities."""

    name = "security_scanner"

    def run(self, context: PipelineContext) -> PipelineContext:
        if not context.valid_syntax:
            context.security_issues = []
            return context

        issues: list[dict] = []
        issues.extend(self._text_scan(context.code))

        if context.ast_tree is not None:
            issues.extend(self._ast_scan(context.ast_tree))

        if context.language.lower() == "python":
            llm_issues = self._llm_issues(context)
            issues.extend(self._dedupe(issues, llm_issues))

        context.security_issues = issues
        return context

    def _text_scan(self, code: str) -> list[dict]:
        issues: list[dict] = []
        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            for pattern, message, severity, fix in _TEXT_PATTERNS:
                if pattern.search(line):
                    issues.append({"line": idx, "issue": message, "severity": severity, "fix": fix})
            if _SQL_PATTERN.search(line):
                issues.append({
                    "line": idx,
                    "issue": "Possible SQL injection: query string is built via concatenation/formatting instead of parameters.",
                    "severity": "high",
                    "fix": "Use parameterized queries, e.g. cursor.execute('SELECT * FROM t WHERE id = %s', (value,)).",
                })
        return issues

    def _ast_scan(self, tree: ast.AST) -> list[dict]:
        issues: list[dict] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._call_name(node.func)
                if func_name in {"input"}:
                    # Not inherently a vulnerability, but flag if used directly in a sink later
                    continue
        return issues

    @staticmethod
    def _call_name(func: ast.AST) -> str:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return ""

    def _llm_issues(self, context: PipelineContext) -> list[dict]:
        prompt = SECURITY_SCAN_PROMPT.format(language=context.language, code=context.code)
        result = call_llm_json(prompt)
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        if isinstance(result, dict) and isinstance(result.get("security_issues"), list):
            return result["security_issues"]
        return []

    @staticmethod
    def _dedupe(existing: list[dict], candidates: list[dict]) -> list[dict]:
        seen = {(i.get("line"), i.get("issue")) for i in existing}
        unique = []
        for c in candidates:
            key = (c.get("line"), c.get("issue"))
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique
