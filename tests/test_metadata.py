from ingest.metadata import (
    _normalize,
    extract_metadata,
    extract_with_regex,
    narrow_models_from_tables,
)


def make_element(text: str, page: int = 1) -> dict:
    return {"type": "text", "text": text, "page": page, "bbox": [0, 0, 0, 0], "section_path": ""}


def test_manufacturer_sma():
    elements = [make_element("SMA Sunny Boy Installation Manual")]
    result = extract_with_regex(elements)
    assert result["manufacturer"] == "SMA"


def test_manufacturer_fronius():
    elements = [make_element("Fronius Symo Operating Instructions")]
    result = extract_with_regex(elements)
    assert result["manufacturer"] == "Fronius"


def test_product_family_sunny_boy():
    elements = [make_element("Sunny Boy 2500HF Installation Guide")]
    result = extract_with_regex(elements)
    assert result["product_family"] == "Sunny Boy"


def test_revision_extracted():
    elements = [make_element("Revision 1.4 | SMA Solar Technology AG")]
    result = extract_with_regex(elements)
    assert result["revision"] == "1.4"


def test_no_manufacturer_returns_none():
    elements = [make_element("Generic inverter manual page 1")]
    result = extract_with_regex(elements)
    assert result["manufacturer"] is None


def test_extract_metadata_without_llm_uses_regex():
    elements = [make_element("SMA Sunny Boy Rev. 2.0")]
    result = extract_metadata(elements)
    assert result["manufacturer"] == "SMA"
    assert result["source"] == "regex"


def make_table(text: str) -> dict:
    return {"type": "table", "text": text, "page": 1, "bbox": [0, 0, 0, 0], "section_path": ""}


MODEL_TABLE = "| Model | Rated power |\n|---|---|\n| SB 2500HF | 2500 W |\n| SB 3000HF | 3000 W |"


def test_narrow_keeps_only_models_in_table():
    elements = [make_table(MODEL_TABLE)]
    models = ["SB 2500HF", "SB 3000HF", "SB 5000HF"]
    result = narrow_models_from_tables(elements, models)
    assert result == ["SB 2500HF", "SB 3000HF"]


def test_narrow_no_model_table_returns_original():
    table = "| Code | Message |\n|---|---|\n| 1 | Grid fault |"
    elements = [make_table(table)]
    models = ["SB 2500HF", "SB 3000HF"]
    result = narrow_models_from_tables(elements, models)
    assert result == models


def test_narrow_no_match_returns_original_not_empty():
    elements = [make_table(MODEL_TABLE)]
    models = ["SB 9999HF"]
    result = narrow_models_from_tables(elements, models)
    assert result == models


def test_narrow_empty_models_returns_empty():
    elements = [make_table(MODEL_TABLE)]
    result = narrow_models_from_tables(elements, [])
    assert result == []


def test_narrow_normalizes_separators():
    table = "| Model | Power |\n|---|---|\n| SB-2500HF | 2500 W |"
    elements = [make_table(table)]
    models = ["SB 2500HF"]
    result = narrow_models_from_tables(elements, models)
    assert result == ["SB 2500HF"]


def test_normalize_strips_spaces_hyphens_dots():
    assert _normalize("SB-2500HF") == _normalize("SB 2500HF")
    assert _normalize("SB.2500HF") == _normalize("sb2500hf")
