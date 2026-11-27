"""SQLite store for user feedback on /ask responses."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path("feedback/feedback.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            trace_id  TEXT PRIMARY KEY,
            question  TEXT NOT NULL,
            vote      TEXT NOT NULL CHECK(vote IN ('up', 'down')),
            created   TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_feedback(trace_id: str, question: str, vote: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO feedback (trace_id, question, vote, created) "
            "VALUES (?, ?, ?, ?)",
            (trace_id, question, vote, datetime.now(UTC).isoformat()),
        )


def export_negative(path: Path) -> int:
    """Write thumbs-down rows to a JSONL file. Returns the row count."""
    import json

    rows = []
    with _connect() as conn:
        rows = conn.execute(
            "SELECT trace_id, question FROM feedback WHERE vote = 'down' ORDER BY created"
        ).fetchall()

    with open(path, "w") as f:
        for trace_id, question in rows:
            f.write(json.dumps({"trace_id": trace_id, "question": question}) + "\n")

    return len(rows)
