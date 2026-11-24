"""Integration tests for the FastAPI service.

Uses the seed Qdrant index (eval/seed_index) and a mocked LLM so the tests
run in CI without Ollama or the full Docker Qdrant.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from api.server import app

SEED_PATH = "eval/seed_index"

MOCK_ANSWER = {
    "diagnosis": "DC overvoltage detected.",
    "causes": ["DC input voltage too high"],
    "steps": ["Disconnect PV array"],
    "safety": ["WARNING: Disconnect before servicing"],
    "citations": ["[1] sma_sunnyboy_hf_2-3kw p.68"],
}


@pytest.fixture(scope="module")
def api_client():
    """TestClient wired to the seed index with a mocked LLM.

    Uses yield so the lifespan (app.state setup) stays active for the
    whole test — TestClient must be used as a context manager for that.
    """
    seed_qdrant = QdrantClient(path=SEED_PATH)
    mock_llm = MagicMock()
    mock_llm.generate.return_value = json.dumps(MOCK_ANSWER)

    with (
        patch("api.server.get_client", return_value=seed_qdrant),
        patch("api.server.OllamaClient", return_value=mock_llm),
    ):
        with TestClient(app) as client:
            yield client, mock_llm


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


def test_health_returns_ok(api_client):
    client, _ = api_client
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /ask — resposta normal
# ---------------------------------------------------------------------------


def test_ask_returns_diagnosis(api_client):
    client, _ = api_client
    resp = client.post("/ask", json={"question": "Event 34 on SB 2500HF?", "model": "SB 2500HF"})
    assert resp.status_code == 200
    assert resp.json()["diagnosis"] != ""


def test_ask_includes_citations(api_client):
    client, _ = api_client
    resp = client.post("/ask", json={"question": "Event 34 on SB 2500HF?", "model": "SB 2500HF"})
    citations = resp.json()["citations"]
    assert len(citations) >= 1
    first = citations[0]
    assert "ref" in first
    assert "doc_id" in first
    assert "page" in first
    assert "page_image_url" in first


def test_ask_citation_url_has_correct_format(api_client):
    client, _ = api_client
    resp = client.post("/ask", json={"question": "Event 34 on SB 2500HF?", "model": "SB 2500HF"})
    url = resp.json()["citations"][0]["page_image_url"]
    assert url.startswith("/pages/sma_sunnyboy_hf_2-3kw/68")


# ---------------------------------------------------------------------------
# /ask — abstain
# ---------------------------------------------------------------------------


def test_ask_abstains_for_unanswerable(api_client):
    client, _ = api_client
    with patch("api.server.should_abstain", return_value=True):
        resp = client.post("/ask", json={"question": "What is the price of the SB 2500HF?"})
    assert resp.status_code == 200
    assert resp.json()["abstained"] is True
    assert resp.json()["diagnosis"] == ""
