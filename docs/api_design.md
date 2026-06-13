# CognifyAI API Design

Base URL: `/api`

## POST /api/analyze

Run the full sequential pipeline synchronously and persist the result.

**Request body** (`AnalyzeRequest`):

```json
{
  "code": "def add(a, b):\n    return a + b\n",
  "language": "python",
  "filename": "math_utils.py"
}
```

**Response** `201 Created` (`AnalyzeResponse`):

```json
{
  "id": "uuid",
  "created_at": "2026-06-12T09:00:00Z",
  "result": {
    "bugs": [
      {"line": 3, "issue": "...", "severity": "medium", "fix": "..."}
    ],
    "security_issues": [],
    "complexity": {"time": "O(n)", "space": "O(1)"},
    "optimized_code": "...",
    "docstring": "\"\"\"...\"\"\"",
    "score": {
      "correctness": 90,
      "readability": 95,
      "security": 100,
      "performance": 85,
      "documentation": 70,
      "overall": 88.7
    }
  }
}
```

`400 Bad Request` if `code` is empty/whitespace.

## POST /api/analyze/stream

Same input as `/api/analyze`, but returns `application/x-ndjson` with one
JSON object per line:

- `{"type": "stage", "stage": "<stage_name>", "status": "running" | "done" | "error", "detail"?: string}`
- `{"type": "result", "data": <AnalyzeResponse>}` (final line)

Stage names, in order: `syntax_checker`, `bug_detector`, `security_scanner`,
`complexity_analyzer`, `optimizer`, `docstring_generator`, `scorer`.

## GET /api/history

Query params: `skip` (default 0), `limit` (default 20, max 100).

**Response** (`HistoryResponse`):

```json
{
  "total": 42,
  "items": [
    {
      "id": "uuid",
      "created_at": "2026-06-12T09:00:00Z",
      "language": "python",
      "filename": "math_utils.py",
      "overall_score": 88.7,
      "snippet": "def add(a, b):"
    }
  ]
}
```

## GET /api/analysis/{id}

Returns the same `AnalyzeResponse` shape as `POST /api/analyze`.
`404 Not Found` if the id does not exist.

## GET /api/health

Liveness probe: `{"status": "ok", "service": "CognifyAI"}`.
