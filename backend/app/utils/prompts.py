"""Prompt templates used by the LLM-backed pipeline stages.

These are only used when ``settings.USE_LLM`` is true and a valid
``MISTRAL_API_KEY`` is configured. Each stage that supports LLM enrichment
falls back to a deterministic heuristic implementation otherwise.
"""

BUG_DETECTION_PROMPT = """You are a senior software engineer reviewing the following {language} code for bugs.
Return ONLY a JSON array of objects with keys: line (int), issue (string), severity ("low"|"medium"|"high"), fix (string).
If there are no bugs, return an empty array [].

Code:
```{language}
{code}
```
"""

SECURITY_SCAN_PROMPT = """You are a security engineer auditing the following {language} code.
Identify injection risks, unsafe eval/exec usage, hardcoded secrets, insecure deserialization and similar issues.
Return ONLY a JSON array of objects with keys: line (int), issue (string), severity ("low"|"medium"|"high"), fix (string).
If there are no issues, return an empty array [].

Code:
```{language}
{code}
```
"""

COMPLEXITY_PROMPT = """Analyze the time and space complexity (Big-O) of the following {language} code.
Return ONLY a JSON object with keys: time (string, e.g. "O(n log n)") and space (string, e.g. "O(n)").

Code:
```{language}
{code}
```
"""

OPTIMIZER_PROMPT = """You are an expert {language} performance engineer.
Refactor and optimize the following code for performance and readability while preserving behaviour.
Take into account these known bugs: {bugs}
And these security issues: {security_issues}
Return ONLY a JSON object with a single key "optimized_code" containing the full optimized source code as a string.

Code:
```{language}
{code}
```
"""

DOCSTRING_PROMPT = """Write a concise module-level docstring (3-6 sentences) summarizing what the following
{language} code does, its inputs/outputs and any side effects. Return ONLY a JSON object with a single
key "docstring" containing the docstring text.

Code:
```{language}
{code}
```
"""
