from ingest.metadata import extract_metadata, extract_with_regex


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
