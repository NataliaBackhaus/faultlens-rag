import json
from pathlib import Path

import pytest

PARSED_DIR = Path("data/parsed")


def load_elements(doc_id: str) -> list[dict]:
    path = PARSED_DIR / f"{doc_id}.json"
    if not path.exists():
        pytest.skip(f"{doc_id}.json not available — run ingest first")
    return json.loads(path.read_text())["elements"]


def test_sma_hf_heading_and_table_counts():
    elements = load_elements("sma_sunnyboy_hf_2-3kw")
    heading_count = len([e for e in elements if e["type"] == "heading"])
    table_count = len([e for e in elements if e["type"] == "table"])
    assert heading_count == 211
    assert table_count == 71


def test_fronius_heading_and_table_counts():
    elements = load_elements("fronius_symo_10-20kw")
    heading_count = len([e for e in elements if e["type"] == "heading"])
    table_count = len([e for e in elements if e["type"] == "table"])
    assert heading_count == 63
    assert table_count == 2
