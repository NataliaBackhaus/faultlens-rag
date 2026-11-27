"""Shared pytest fixtures."""

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


@pytest.fixture(scope="session")
def api_client():
    """TestClient wired to the seed index with a mocked LLM."""
    seed_qdrant = QdrantClient(path=SEED_PATH)
    mock_llm = MagicMock()
    mock_llm.generate.return_value = json.dumps(MOCK_ANSWER)

    with (
        patch("api.server.get_client", return_value=seed_qdrant),
        patch("api.server.OllamaClient", return_value=mock_llm),
    ):
        with TestClient(app) as client:
            yield client, mock_llm
