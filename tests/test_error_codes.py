import json
from pathlib import Path

import pytest

from ingest.error_codes import extract_rows, join_tables

PARSED_DIR = Path("data/parsed")


def load_rows(doc_id: str) -> list[dict]:
    path = PARSED_DIR / f"{doc_id}.json"
    if not path.exists():
        pytest.skip(f"{doc_id}.json not available — run ingest first")
    data = json.loads(path.read_text())
    tables = join_tables(data["elements"])
    rows = []
    for t in tables:
        rows.extend(extract_rows(t, doc_id))
    return [r for r in rows if r.get("code", "").strip() and "type" not in r]


def find_row(rows: list[dict], code: str) -> dict | None:
    return next((r for r in rows if r["code"].strip() == code), None)


def test_sma_hf_event_1_grid_fault():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "1")
    assert row is not None
    assert "Grid fault" in row["message"]
    assert row["page"] == 66


def test_sma_hf_event_2_grid_fault():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "2")
    assert row is not None
    assert "Grid fault" in row["message"]
    assert "miniature circuit-breaker" in row["remedy"]


def test_sma_hf_event_5_frequency():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "5")
    assert row is not None
    assert "power frequency" in row["message"].lower()


def test_sma_hf_event_3_10min_voltage():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "3")
    assert row is not None
    assert "10-minute" in row["message"]
    assert row["page"] == 67


def test_sma_hf_event_4_grid_parallel():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "4")
    assert row is not None
    assert "grid parallel operation" in row["message"]
    assert row["page"] == 67


def test_sma_hf_event_6_internal_monitoring():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "6")
    assert row is not None
    assert "internal monitoring" in row["message"]
    assert row["page"] == 68


def test_sma_hf_event_7_frequency_not_permitted():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "7")
    assert row is not None
    assert "Frq. not permitted" in row["message"]
    assert row["page"] == 68


def test_sma_hf_event_8_waiting_for_grid():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "8")
    assert row is not None
    assert "Waiting for grid voltage" in row["message"]
    assert row["page"] == 68


def test_sma_hf_event_33_unstable_operation():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "33")
    assert row is not None
    assert "Unstable operation" in row["message"]
    assert row["page"] == 68


def test_sma_hf_event_34_dc_overvoltage():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "34")
    assert row is not None
    assert "DC overvoltage" in row["message"]
    assert row["page"] == 68


def test_sma_hf_event_35_insulation():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "35")
    assert row is not None
    assert "Insulation" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_38_dc_overcurrent():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "38")
    assert row is not None
    assert "DC overcurrent" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_39_waiting_dc():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "39")
    assert row is not None
    assert "DC start conditions" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_42_wrong_earthing():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "42")
    assert row is not None
    assert "earthing" in row["message"].lower()
    assert row["page"] == 69


def test_sma_hf_event_65_overtemperature():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "65")
    assert row is not None
    assert "Overtemperature" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_66_overload():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "66")
    assert row is not None
    assert "Overload" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_67_comm_disturbed():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "67")
    assert row is not None
    assert "Comm. disturbed" in row["message"]
    assert row["page"] == 69


def test_sma_hf_event_70_sensor_fault():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "70")
    assert row is not None
    assert "fan" in row["message"].lower()
    assert row["page"] == 70


def test_sma_hf_event_71_sd_card():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "71")
    assert row is not None
    assert "SD card" in row["message"] or "param" in row["message"].lower()
    assert row["page"] == 70


def test_sma_hf_event_72_data_storage():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "72")
    assert row is not None
    assert "Data stor" in row["message"]
    assert row["page"] == 70


def test_sma_hf_event_73_update_failed():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "73")
    assert row is not None
    assert "Update" in row["message"]
    assert row["page"] == 70


def test_sma_hf_event_74_varistor():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "74")
    assert row is not None
    assert "Varistor" in row["message"]
    assert row["page"] == 71


def test_sma_hf_event_75_fan_fault():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "75")
    assert row is not None
    assert "Fan fault" in row["message"]
    assert row["page"] == 71


def test_sma_hf_event_77_interference():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "77")
    assert row is not None
    assert "Interference" in row["message"]
    assert row["page"] == 71


def test_sma_hf_event_80_derating():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "80")
    assert row is not None
    assert "Derating" in row["message"]
    assert row["page"] == 71


def test_sma_hf_event_81_comm_disturbed():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "81")
    assert row is not None
    assert "Comm. disturbed" in row["message"]
    assert row["page"] == 71


def test_sma_hf_event_90_inst_code_invalid():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    row = find_row(rows, "90")
    assert row is not None
    assert "Inst. code invalid" in row["message"] or "Grid param" in row["message"]
    assert row["page"] == 71


def test_sma_hf_total_rows_count():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    assert len(rows) >= 30


def test_sma_hf_all_rows_have_doc_id():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    assert all(r["doc_id"] == "sma_sunnyboy_hf_2-3kw" for r in rows)


def test_sma_hf_all_rows_have_page():
    rows = load_rows("sma_sunnyboy_hf_2-3kw")
    assert all(isinstance(r["page"], int) and r["page"] > 0 for r in rows)
