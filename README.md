# CognifyAI

<p align="center">
  <h3 align="center">AI-Powered Code Optimization & Analysis Platform</h3>
  <p align="center">
    Analyze, secure, optimize, and document code using a multi-stage AI pipeline.
  </p>
</p>

---

## Overview

CognifyAI is a full-stack AI-assisted code analysis platform designed to help developers improve code quality through a structured analysis pipeline.

Users can submit source code and receive:

* Syntax validation
* Bug detection
* Security vulnerability analysis
* Complexity estimation
* Code optimization suggestions
* Automated docstring generation
* Overall quality scoring

The platform combines deterministic static analysis with optional LLM-powered enrichment, providing fast and reliable results while remaining cost-efficient.

---

## Screenshots

### Home Page

The main workspace where users can write or paste source code, select a programming language, and start the analysis pipeline.

![Home Page](./screenshot/home.jpeg)

---

### Analysis Results

Displays bug reports, security findings, complexity analysis, optimization suggestions, generated documentation, and overall quality scores.

![Results Page](./screenshot/result.jpeg)

---

### Analysis History

Browse previously analyzed code submissions and reopen detailed reports.

![History Page](./screenshot/history.jpeg)


## Features

### Multi-Stage Analysis Pipeline

Every code submission passes through a strictly sequential pipeline:

```text
Syntax Validation
      ↓
Bug Detection
      ↓
Security Scanning
      ↓
Complexity Analysis
      ↓
Code Optimization
      ↓
Docstring Generation
```

### Analysis Capabilities

* AST-based static code analysis
* Bug detection with line-level explanations
* Security vulnerability scanning
* Time complexity estimation
* Space complexity estimation
* Code optimization suggestions
* Automatic documentation generation
* Quality scoring engine

### Interactive Frontend

* Monaco Editor
* Live pipeline progress tracking
* Analysis dashboard
* Historical analysis records
* Side-by-side diff viewer
* Optimized code comparison

### AI-Powered Enhancements

Supports two execution modes:

#### Deterministic Mode

* No API key required
* Fully local analysis
* Fast execution
* Rule-based heuristics

#### LLM Enrichment Mode

* LangChain integration
* Mistral AI support
* Enhanced explanations
* Smarter optimization recommendations
* More contextual code reviews

---

## Architecture

```text
Frontend (React + TypeScript)
            │
            ▼
      FastAPI Backend
            │
 ┌──────────┼──────────┐
 ▼          ▼          ▼
Pipeline   Database   LLM Layer
            │
            ▼
      PostgreSQL
```

---

## Technology Stack

### Backend

* Python 3.11
* FastAPI
* SQLAlchemy 2.0
* PostgreSQL
* Pydantic v2

### Frontend

* React 18
* TypeScript
* Vite
* Monaco Editor

### AI Layer

* AST Analysis
* LangChain
* Mistral AI

### DevOps

* Docker
* Docker Compose
* Nginx

### Testing

* Pytest

---

## Project Structure

```text
CognifyAI/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── docs/
│   ├── api_design.md
│   ├── architecture.md
│   └── prompts.md
│
├── screenshot/
│   ├── home.jpeg
│   ├── result.jpeg
│   └── history.jpeg
│
├── docker-compose.yml
└── README.md
```

---

## Run With Docker

### Clone Repository

```bash
git clone https://github.com/maroofiums/CognifyAI.git
cd CognifyAI
```

### Start Application

```bash
docker-compose up --build
```

### Available Services

| Service      | URL                        |
| ------------ | -------------------------- |
| Frontend     | http://localhost:5173      |
| Backend API  | http://localhost:8000      |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL   | localhost:5432             |

The frontend automatically communicates with the backend through Nginx proxy configuration.

### Stop Services

```bash
docker-compose down
```

Remove database volume:

```bash
docker-compose down -v
```

---

## Enable LLM Layer

By default:

```env
USE_LLM=false
```

To enable LangChain + Mistral enrichment:

```yaml
environment:
  USE_LLM: "true"
  MISTRAL_API_KEY: "your-api-key"
  LLM_MODEL: "mistral-small-latest"
```

---

## Local Development

### Backend Setup

```bash
cd backend

python -m venv .venv

source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## PostgreSQL Configuration

For local PostgreSQL:

```env
DATABASE_URL=postgresql://cognify:cognify@localhost:5432/cognifydb
```

Run PostgreSQL:

```bash
docker run -d \
  --name cognify-db \
  -e POSTGRES_USER=cognify \
  -e POSTGRES_PASSWORD=cognify \
  -e POSTGRES_DB=cognifydb \
  -p 5432:5432 \
  postgres:16-alpine
```

---

## Using CognifyAI

### Step 1

Open the Home page and paste source code into the Monaco editor.

### Step 2

Select the programming language.

### Step 3

Click Analyze Code.

### Step 4

Watch live pipeline progress updates.

### Step 5

Review:

* Quality score
* Security findings
* Bug reports
* Complexity analysis
* Generated documentation
* Optimized code suggestions

### Step 6

Browse historical analyses from the History page.

---

## API Example

### Request

```json
{
  "language": "python",
  "code": "def add(a,b): return a+b"
}
```

### Response

```json
{
  "bugs": [],
  "security_issues": [],
  "complexity": {
    "time": "O(1)",
    "space": "O(1)"
  },
  "optimized_code": "def add(a: int, b: int) -> int:\n    return a + b",
  "docstring": "Returns the sum of two integers.",
  "score": {
    "correctness": 95,
    "readability": 90,
    "security": 100,
    "performance": 95,
    "documentation": 85,
    "overall": 93
  }
}
```

---

## JSON Output Contract

```json
{
  "bugs": [],
  "security_issues": [],
  "complexity": {
    "time": "O(n)",
    "space": "O(1)"
  },
  "optimized_code": "",
  "docstring": "",
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

---

## Testing

Run the complete backend test suite:

```bash
cd backend

pytest -q
```

Coverage includes:

* API tests
* Pipeline tests
* Service tests
* Security checks
* Syntax validation
* Score calculation

---

## Documentation

Additional documentation can be found inside the docs directory.

| File            | Purpose              |
| --------------- | -------------------- |
| architecture.md | System architecture  |
| api_design.md   | API documentation    |
| prompts.md      | LLM prompt templates |

---

## Future Roadmap

### Version 2

* Redis integration
* Celery background workers
* WebSocket status updates
* Authentication & authorization
* Multi-language support
* Team workspaces

### Version 3

* LangGraph orchestration
* RAG-powered recommendations
* GitHub repository analysis
* Pull request reviews
* CI/CD integration
* AI code review reports

---

## Why CognifyAI?

Most code review tools focus on one aspect of software quality.

CognifyAI combines:

* Static Analysis
* Security Review
* Optimization
* Documentation Generation
* AI-Assisted Insights

into a single developer workflow.

The project demonstrates production-grade software engineering concepts including:

* Clean Architecture
* Repository Pattern
* Service Layer Pattern
* REST API Design
* Containerized Deployment
* AI Workflow Pipelines
* Frontend-Backend Integration

---

## Author

**Maroof**

AI/ML Developer • Backend Engineer • FastAPI Enthusiast

GitHub: https://github.com/maroofiums

---

## License

MIT License

Feel free to use, modify, and contribute.
