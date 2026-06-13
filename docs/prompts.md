# LLM Prompts

These prompts are only sent when `USE_LLM=true` and `MISTRAL_API_KEY` is set
(see `app/llm/client.py`). Each is invoked via LangChain's `ChatMistralAI` and
the response is parsed as JSON via `app.utils.helpers.safe_json_loads`.
Defined in `app/utils/prompts.py`.

| Stage | Prompt constant | Expected JSON shape |
|---|---|---|
| Bug Detector | `BUG_DETECTION_PROMPT` | `[{"line": int, "issue": str, "severity": "low\|medium\|high", "fix": str}, ...]` |
| Security Scanner | `SECURITY_SCAN_PROMPT` | Same shape as above |
| Complexity Analyzer | `COMPLEXITY_PROMPT` | `{"time": "O(...)", "space": "O(...)"}` |
| Optimizer | `OPTIMIZER_PROMPT` | `{"optimized_code": "<full source>"}` |
| Docstring Generator | `DOCSTRING_PROMPT` | `{"docstring": "<text>"}` |

## Fallback behaviour

If `call_llm_json()` returns `None` (LLM disabled, network error, or
unparseable response), each stage falls back to a deterministic heuristic:

- **Bug Detector / Security Scanner**: AST + regex based static analysis
  only (no LLM findings merged in).
- **Complexity Analyzer**: loop-nesting-depth + recursion heuristic.
- **Optimizer**: safe textual refactors (`== None` -> `is None`, bare
  `except:` -> `except Exception:`, etc.). The LLM result is also
  re-validated with `ast.parse` before being accepted, so a malformed LLM
  response can never produce broken `optimized_code`.
- **Docstring Generator**: template-based summary referencing the function
  /class names and the findings from earlier stages.
