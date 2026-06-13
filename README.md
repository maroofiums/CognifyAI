# CognifyAI - AI Code Optimiser Platform

CognifyAI runs submitted source code through a strictly sequential AI
analysis pipeline - **syntax validation → bug detection → security scanning
→ complexity analysis → optimization → docstring generation** - and returns
a structured JSON report with an overall quality score. A React + TypeScript
frontend (Monaco editor, live pipeline status, diff viewer, score dashboard)
consumes the API.

## Folder Structure

```
CognifyAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/        # analysis.py, history.py, health.py
│   │   │   └── router.py
│   │   ├── core/               # config, database, security
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── pipeline/             # PipelineContext + AnalysisPipeline orchestrator
│   │   ├── services/             # 6 pipeline stages + scorer + analyzer service
│   │   ├── repositories/         # DB access layer
│   │   ├── llm/                  # optional LangChain/Mistral wrapper
│   │   ├── utils/                # helpers + prompt templates
│   │   └── main.py               # FastAPI app entrypoint
│   ├── tests/                    # pytest suite (pipeline, services, API)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts         # axios + streaming fetch client
│   │   ├── components/           # CodeEditor, DiffViewer, ScoreDashboard, StatusStream, FindingsTable, Navbar
│   │   ├── context/AnalysisContext.tsx
│   │   ├── pages/                # Home, Results, History
│   │   ├── types/index.ts
│   │   ├── App.tsx, main.tsx, styles.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/                          # architecture, API design, prompt docs
├── docker-compose.yml
└── README.md
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL, Pydantic v2
- **AI Layer**: AST-based heuristic analyzers + optional LangChain/Mistral
  enrichment (toggled via `USE_LLM`)
- **Frontend**: React 18, TypeScript, Vite, Monaco Editor (`@monaco-editor/react`)
- **DevOps**: Docker, docker-compose, Nginx (frontend reverse proxy)

---

## Run with Docker (recommended)

Requires Docker and Docker Compose.

```bash
git clone <this-repo>
cd CognifyAI
docker-compose up --build
```

This starts three services:

| Service  | URL                          | Description                     |
|----------|------------------------------|----------------------------------|
| frontend | http://localhost:5173        | React app (served via Nginx)     |
| backend  | http://localhost:8000        | FastAPI + Swagger at `/docs`     |
| db       | localhost:5432               | PostgreSQL 16                    |

The frontend's Nginx config proxies `/api/*` to the backend container, so
the UI works out of the box at **http://localhost:5173**.

To stop: `docker-compose down` (add `-v` to also remove the Postgres volume).

### Enabling the LLM layer (optional)

By default `USE_LLM=false`, so every pipeline stage uses deterministic,
fully local heuristics - no API key required. To enable LangChain/Mistral
enrichment, edit `docker-compose.yml` (or set environment variables for the
`backend` service):

```yaml
environment:
  USE_LLM: "true"
  MISTRAL_API_KEY: "your-mistral-api-key"
  LLM_MODEL: "mistral-small-latest"
```

---

## Run Locally (without Docker)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # defaults to a local SQLite DB
uvicorn app.main:app --reload --port 8000
```

The API is now available at http://localhost:8000 (interactive docs at
`/docs`). By default `DATABASE_URL=sqlite:///./cognify.db` if you don't set
it, so PostgreSQL is optional for local development.

To use PostgreSQL locally, set in `.env`:

```
DATABASE_URL=postgresql://cognify:cognify@localhost:5432/cognifydb
```

and run Postgres via Docker:

```bash
docker run -d --name cognify-db -e POSTGRES_USER=cognify -e POSTGRES_PASSWORD=cognify \
  -e POSTGRES_DB=cognifydb -p 5432:5432 postgres:16-alpine
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env                # VITE_API_BASE_URL=/api
npm run dev
```

Vite's dev server proxies `/api` to `http://localhost:8000` (see
`vite.config.ts`). Open http://localhost:5173.

### 3. Run the test suite

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

---

## Using the App

1. **Home** - paste or write code in the Monaco editor, choose a language,
   and click **Analyze Code**. A live status panel shows each pipeline
   stage as it runs.
2. **Results** - view the overall + per-category scores, complexity
   estimate, bug/security findings (with line numbers, severity and
   suggested fixes), the generated docstring, and a side-by-side diff of
   the original vs. optimized code.
3. **History** - browse all past analyses with pagination; click **View**
   to reopen a stored result.

## Strict JSON Output Contract

Every analysis produces:

```json
{
  "bugs": [{ "line": 0, "issue": "", "severity": "low|medium|high", "fix": "" }],
  "security_issues": [{ "line": 0, "issue": "", "severity": "low|medium|high", "fix": "" }],
  "complexity": { "time": "O(n)", "space": "O(1)" },
  "optimized_code": "string",
  "docstring": "string",
  "score": {
    "correctness": 0,
    "readability": 0,
    "security": 0,
    "performance": 0,
    "documentation": 0,
    "overall": 0
  }
}
```

See `docs/api_design.md` for full endpoint documentation, `docs/architecture.md`
for the layered architecture and pipeline design, and `docs/prompts.md` for
the optional LLM prompt templates.
