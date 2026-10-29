from ingest.quality import flag_low_text_pages, flag_missing_metadata, flag_sparse_tables


def make_element(type="text", text="", page=1):
    return {"type": type, "text": text, "page": page, "bbox": [0, 0, 0, 0], "section_path": ""}


def test_flag_low_text_pages_detects_sparse_page():
    elements = [
        make_element(text="a" * 100, page=1),
        make_element(text="x", page=2),
    ]
    assert flag_low_text_pages(elements, threshold=50) == [2]


def test_flag_low_text_pages_no_issues():
    elements = [make_element(text="a" * 100, page=1)]
    assert flag_low_text_pages(elements, threshold=50) == []


def test_flag_sparse_tables_detects_empty_cells():
    sparse_table = "| A | B |\n|---|---|\n|   |   |"
    elements = [make_element(type="table", text=sparse_table, page=5)]
    result = flag_sparse_tables(elements, empty_ratio=0.3)
    assert len(result) == 1
    assert result[0]["page"] == 5


def test_flag_sparse_tables_no_issues():
    dense_table = "| A | B |\n|---|---|\n| x | y |"
    elements = [make_element(type="table", text=dense_table, page=3)]
    assert flag_sparse_tables(elements, empty_ratio=0.3) == []


def test_flag_missing_metadata_detects_missing():
    manuals = [{"id": "doc1"}, {"id": "doc2", "sha256": "abc123"}]
    assert flag_missing_metadata(manuals) == ["doc1"]


def test_flag_missing_metadata_all_present():
    manuals = [{"id": "doc1", "sha256": "abc"}, {"id": "doc2", "sha256": "def"}]
    assert flag_missing_metadata(manuals) == []
