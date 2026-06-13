"""API integration tests for the /api/analyze and /api/history endpoints."""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_cognify.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_ENGINE = create_engine("sqlite:///./test_cognify.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)
    if os.path.exists("test_cognify.db"):
        os.remove("test_cognify.db")


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint_returns_strict_json_shape():
    payload = {
        "code": "def add(a, b):\n    return a + b\n",
        "language": "python",
        "filename": "math_utils.py",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert "id" in body
    result = body["result"]

    for key in ["bugs", "security_issues", "complexity", "optimized_code", "docstring", "score"]:
        assert key in result

    for key in ["correctness", "readability", "security", "performance", "documentation", "overall"]:
        assert key in result["score"]
        assert 0 <= result["score"][key] <= 100


def test_analyze_rejects_empty_code():
    response = client.post("/api/analyze", json={"code": "   ", "language": "python"})
    assert response.status_code == 400


def test_history_and_get_by_id():
    payload = {"code": "x = 1\n", "language": "python"}
    create_resp = client.post("/api/analyze", json=payload)
    analysis_id = create_resp.json()["id"]

    history_resp = client.get("/api/history")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert history["total"] >= 1
    assert any(item["id"] == analysis_id for item in history["items"])

    detail_resp = client.get(f"/api/analysis/{analysis_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == analysis_id


def test_get_analysis_404():
    response = client.get("/api/analysis/does-not-exist")
    assert response.status_code == 404
