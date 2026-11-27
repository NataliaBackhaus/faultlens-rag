"""Tests for POST /feedback and feedback.store."""

import sqlite3

import pytest

from feedback.store import export_negative, save_feedback

# ---------------------------------------------------------------------------
# feedback.store unit tests (use a tmp DB)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("feedback.store.DB_PATH", tmp_path / "feedback.db")


def test_save_and_retrieve(tmp_path, monkeypatch):
    monkeypatch.setattr("feedback.store.DB_PATH", tmp_path / "feedback.db")
    save_feedback("trace-1", "Event 34?", "down")
    conn = sqlite3.connect(tmp_path / "feedback.db")
    rows = conn.execute("SELECT * FROM feedback").fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "trace-1"
    assert rows[0][2] == "down"


def test_export_negative_writes_jsonl(tmp_path, monkeypatch):
    monkeypatch.setattr("feedback.store.DB_PATH", tmp_path / "feedback.db")
    save_feedback("t1", "bad question", "down")
    save_feedback("t2", "good question", "up")
    out = tmp_path / "draft.jsonl"
    n = export_negative(out)
    assert n == 1
    lines = out.read_text().splitlines()
    assert len(lines) == 1
    assert "bad question" in lines[0]


# ---------------------------------------------------------------------------
# POST /feedback via TestClient
# ---------------------------------------------------------------------------


def test_feedback_endpoint_returns_204(api_client):
    client, _ = api_client
    resp = client.post(
        "/feedback",
        json={"trace_id": "abc", "question": "Event 34?", "vote": "down"},
    )
    assert resp.status_code == 204


def test_feedback_endpoint_rejects_invalid_vote(api_client):
    client, _ = api_client
    resp = client.post(
        "/feedback",
        json={"trace_id": "abc", "question": "Event 34?", "vote": "meh"},
    )
    assert resp.status_code == 422


def test_ask_response_includes_trace_id(api_client):
    client, _ = api_client
    resp = client.post("/ask", json={"question": "Event 34 on SB 2500HF?", "model": "SB 2500HF"})
    assert resp.status_code == 200
    assert "trace_id" in resp.json()
    assert len(resp.json()["trace_id"]) == 36  # uuid4 length
