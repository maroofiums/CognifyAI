# CognifyAI Architecture

## Overview

CognifyAI is a layered FastAPI application that runs source code through a
strictly sequential, six-stage AI analysis pipeline and persists the
results in PostgreSQL. The React/TypeScript frontend provides a Monaco-based
editor, real-time pipeline progress, a diff viewer, and a score dashboard.

## Layered Architecture (Backend)

```
routes  ->  services  ->  pipeline  ->  database
```

- **routes** (`app/api/routes/*`): FastAPI route handlers. Responsible for
  request validation (via Pydantic schemas), HTTP status codes, and shaping
  responses. Contains no business logic.
- **services** (`app/services/*`): Business logic layer.
  - `AnalyzerService` is the entry point used by routes; it runs the
    pipeline and persists results via the repository.
  - The remaining service modules (`syntax_checker`, `bug_detector`,
    `security_scanner`, `complexity_analyzer`, `optimizer`,
    `docstring_generator`, `scorer`) are the individual pipeline stages.
- **pipeline** (`app/pipeline/*`): `AnalysisPipeline` orchestrates the
  ordered execution of stages over a shared `PipelineContext`. Provides both
  a synchronous `run()` and a streaming `run_streaming()` generator.
- **repositories** (`app/repositories/*`): SQLAlchemy data-access layer.
  `AnalysisRepository` is the only module that talks to the ORM directly.
- **models** (`app/models/*`): SQLAlchemy ORM models (`Analysis`, `User`).
- **schemas** (`app/schemas/*`): Pydantic request/response models, matching
  the strict JSON contract required by the spec.
- **llm** (`app/llm/*`): Optional LangChain/Mistral wrapper. Every pipeline
  stage that can be LLM-enhanced calls `call_llm_json()`, which returns
  `None` when `USE_LLM=false` or no API key is configured - at which point
  the stage transparently falls back to its deterministic heuristic
  implementation. This keeps the platform fully runnable with zero external
  dependencies while remaining "LLM-ready".

## The Sequential Pipeline

```
SyntaxChecker -> BugDetector -> SecurityScanner -> ComplexityAnalyzer -> Optimizer -> DocstringGenerator -> Scorer
```

Each stage receives and mutates a single `PipelineContext` dataclass:

1. **SyntaxChecker** - parses the code with `ast.parse`. Sets
   `valid_syntax`, `ast_tree`, and `syntax_errors`.
2. **BugDetector** - if syntax is invalid, surfaces the syntax error as the
   only bug and skips further analysis. Otherwise walks the AST for common
   logic/runtime issues (mutable defaults, bare excepts, `== None`,
   div-by-variable, etc.), optionally merged with LLM findings.
3. **SecurityScanner** - regex + AST scan for `eval`/`exec`, `os.system`,
   `subprocess(shell=True)`, hardcoded secrets, `pickle.loads`,
   `yaml.load`, SQL string concatenation, etc.
4. **ComplexityAnalyzer** - estimates Big-O time complexity from loop
   nesting depth and recursion, and space complexity from growing data
   structures.
5. **Optimizer** - given the code *and* the bugs/security findings from
   stages 2-3, produces `optimized_code`. Heuristic mode applies safe
   textual refactors (e.g. `== None` -> `is None`, bare `except:` ->
   `except Exception:`); LLM mode asks the model to refactor while
   preserving behaviour, and validates the result still parses before
   accepting it.
6. **DocstringGenerator** - produces a module-level `docstring` summarizing
   the (optimized) code, referencing the findings from all previous stages.
7. **Scorer** - aggregates everything into the final `score` block
   (correctness, readability, security, performance, documentation,
   overall).

Because each stage only reads fields already populated by earlier stages and
writes its own fields, the dependency order is enforced by construction -
reordering `AnalysisPipeline.stages` would break later stages that rely on
`context.bugs`, `context.security_issues`, etc.

## Streaming

`POST /api/analyze/stream` returns `application/x-ndjson`. Each line is a
JSON object:

```json
{"type": "stage", "stage": "syntax_checker", "status": "running"}
{"type": "stage", "stage": "syntax_checker", "status": "done"}
...
{"type": "result", "data": {"id": "...", "created_at": "...", "result": {...}}}
```

The frontend consumes this with the Fetch Streams API
(`src/api/client.ts::analyzeCodeStream`) to drive the `StatusStream`
component in real time.

## Frontend Architecture

- `AnalysisProvider` (React Context) holds the most recent analysis result
  and the source code that produced it, so the Home page (editor) and
  Results page (diff/scores) can share state without prop drilling.
- `pages/Home.tsx` - Monaco editor + language/filename controls + streaming
  status panel. On completion, navigates to `/results`.
- `pages/Results.tsx` - score dashboard, complexity card, bug/security
  findings tables, generated docstring, and a Monaco `DiffEditor` comparing
  original vs. optimized code. Also handles `/analysis/:id` for viewing
  historical records.
- `pages/History.tsx` - paginated table backed by `GET /api/history`.
