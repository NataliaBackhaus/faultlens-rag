from ingest.chunk import MAX_CHARS, OVERLAP_CHARS, chunk_document, chunk_text

DOC_META = {
    "doc_id": "sma_test",
    "manufacturer": "SMA",
    "models": ["SB 2500HF"],
    "firmware_range": None,
    "revision": None,
}


def make_elem(etype, text, section="Section 1", page=1, bbox=None):
    return {
        "type": etype,
        "text": text,
        "section_path": section,
        "page": page,
        "bbox": bbox or [0.0, 0.0, 100.0, 50.0],
    }


# --- chunk_text ---


def test_short_text_returns_single_chunk():
    result = chunk_text("Short text.")
    assert result == ["Short text."]


def test_long_text_splits_into_multiple_chunks():
    para = "A" * 600
    text = f"{para}\n\n{para}\n\n{para}"
    result = chunk_text(text)
    assert len(result) > 1


def test_no_chunk_exceeds_max_chars():
    para = "A" * 600
    text = f"{para}\n\n{para}\n\n{para}"
    for chunk in chunk_text(text):
        assert len(chunk) <= MAX_CHARS + OVERLAP_CHARS


def test_consecutive_chunks_have_overlap():
    para = "A" * 600
    text = f"{para}\n\n{para}\n\n{para}"
    chunks = chunk_text(text)
    assert len(chunks) >= 2
    tail = chunks[0][-OVERLAP_CHARS:]
    assert chunks[1].startswith(tail)


def test_empty_string_returns_single_chunk():
    assert chunk_text("") == [""]


# --- chunk_document ---


def test_prose_record_type():
    elems = [make_elem("text", "Some prose text.")]
    records = chunk_document(elems, DOC_META)
    assert all(r.record_type == "prose" for r in records)


def test_table_record_type():
    elems = [make_elem("table", "| Col1 | Col2 |\n| A | B |")]
    records = chunk_document(elems, DOC_META)
    assert any(r.record_type == "table" for r in records)


def test_figure_record_type():
    elems = [make_elem("figure", "")]
    records = chunk_document(elems, DOC_META)
    assert any(r.record_type == "figure" for r in records)


def test_records_carry_doc_id():
    elems = [make_elem("text", "Some text.")]
    records = chunk_document(elems, DOC_META)
    assert all(r.doc_id == "sma_test" for r in records)


def test_records_carry_page():
    elems = [make_elem("text", "Some text.", page=5)]
    records = chunk_document(elems, DOC_META)
    assert all(r.page == 5 for r in records)


def test_records_carry_section_path():
    elems = [make_elem("text", "Some text.", section="3 Troubleshooting")]
    records = chunk_document(elems, DOC_META)
    assert all(r.section_path == "3 Troubleshooting" for r in records)


def test_warning_stays_in_same_section():
    elems = [
        make_elem("text", "Step 1: do this.", section="Section 1"),
        make_elem("text", "WARNING: be careful.", section="Section 1"),
    ]
    records = chunk_document(elems, DOC_META)
    assert len(records) == 1
    assert "WARNING" in records[0].text


def test_new_section_creates_new_records():
    elems = [
        make_elem("text", "Text in section 1.", section="Section 1"),
        make_elem("text", "Text in section 2.", section="Section 2"),
    ]
    records = chunk_document(elems, DOC_META)
    sections = [r.section_path for r in records]
    assert "Section 1" in sections
    assert "Section 2" in sections


def test_long_section_splits_into_multiple_records():
    long_text = "A" * 600
    elems = [
        make_elem("text", long_text, section="Section 1"),
        make_elem("text", long_text, section="Section 1"),
        make_elem("text", long_text, section="Section 1"),
    ]
    records = chunk_document(elems, DOC_META)
    prose = [r for r in records if r.record_type == "prose"]
    assert len(prose) > 1


def test_empty_elements_returns_empty():
    assert chunk_document([], DOC_META) == []
