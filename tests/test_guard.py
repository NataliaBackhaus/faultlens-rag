from generation.guard import check_citations, should_abstain, wrong_model_abstain

PASSAGES = [
    {"doc_id": "sma_sunnyboy_hf_2-3kw", "page": 42, "record_type": "table_row", "text": "34 | ..."},
    {"doc_id": "sma_sunnyboy_hf_2-3kw", "page": 41, "record_type": "prose", "text": "WARNING: ..."},
    {"doc_id": "sma_sunnyboy_hf_2-3kw", "page": 10, "record_type": "prose", "text": "Event 34 ..."},
]

ANSWER = {
    "diagnosis": "Event 34 means overvoltage.",
    "causes": ["Grid voltage too high"],
    "steps": ["Check AC terminals"],
    "safety": ["Disconnect before servicing"],
    "citations": [
        "[1] sma_sunnyboy_hf_2-3kw p.41",
        "[2] sma_sunnyboy_hf_2-3kw p.42",
    ],
}


# --- check_citations ---


def test_check_citations_keeps_valid_citations():
    answer = {**ANSWER, "citations": ["[1] sma_sunnyboy_hf_2-3kw p.41"]}
    result = check_citations(answer, PASSAGES)
    assert "[1] sma_sunnyboy_hf_2-3kw p.41" in result["citations"]


def test_check_citations_removes_invented_citation():
    answer = {**ANSWER, "citations": ["[1] sma_sunnyboy_hf_2-3kw p.99"]}
    result = check_citations(answer, PASSAGES)
    assert result["citations"] == []


def test_check_citations_keeps_only_valid():
    answer = {
        **ANSWER,
        "citations": [
            "[1] sma_sunnyboy_hf_2-3kw p.41",
            "[2] sma_sunnyboy_hf_2-3kw p.99",
        ],
    }
    result = check_citations(answer, PASSAGES)
    assert len(result["citations"]) == 1
    assert "[1] sma_sunnyboy_hf_2-3kw p.41" in result["citations"]


def test_check_citations_removes_wrong_doc_id():
    answer = {**ANSWER, "citations": ["[1] fronius_symo_10-20kw p.42"]}
    result = check_citations(answer, PASSAGES)
    assert result["citations"] == []


def test_check_citations_preserves_other_fields():
    answer = {**ANSWER, "citations": ["[1] sma_sunnyboy_hf_2-3kw p.41"]}
    result = check_citations(answer, PASSAGES)
    assert result["diagnosis"] == ANSWER["diagnosis"]
    assert result["steps"] == ANSWER["steps"]


def test_check_citations_empty_citations():
    answer = {**ANSWER, "citations": []}
    result = check_citations(answer, PASSAGES)
    assert result["citations"] == []


# --- should_abstain ---


def test_should_abstain_empty_scores():
    assert should_abstain([]) is True


def test_should_abstain_below_threshold():
    assert should_abstain([-2.0, -3.5], threshold=0.0) is True


def test_should_abstain_above_threshold():
    assert should_abstain([1.5, 0.3], threshold=0.0) is False


def test_should_abstain_exactly_at_threshold():
    assert should_abstain([0.0], threshold=0.0) is False


def test_should_abstain_uses_max_score():
    assert should_abstain([-5.0, 2.0], threshold=0.0) is False


# --- wrong_model_abstain ---


def test_wrong_model_abstain_no_model_queried():
    result = wrong_model_abstain(PASSAGES, queried_model=None)
    assert result is None


def test_wrong_model_abstain_correct_model():
    result = wrong_model_abstain(PASSAGES, queried_model="sma_sunnyboy_hf_2-3kw")
    assert result is None


def test_wrong_model_abstain_all_passages_wrong_model():
    passages = [
        {"doc_id": "fronius_symo_10-20kw", "page": 5, "text": "..."},
        {"doc_id": "fronius_symo_10-20kw", "page": 6, "text": "..."},
    ]
    result = wrong_model_abstain(passages, queried_model="sma_sunnyboy_hf_2-3kw")
    assert result is not None
    assert result["abstain"] is True
    assert "fronius_symo_10-20kw" in result["reason"]
    assert "sma_sunnyboy_hf_2-3kw" in result["reason"]


def test_wrong_model_abstain_mixed_passages_no_abstain():
    passages = [
        {"doc_id": "fronius_symo_10-20kw", "page": 5, "text": "..."},
        {"doc_id": "sma_sunnyboy_hf_2-3kw", "page": 6, "text": "..."},
    ]
    result = wrong_model_abstain(passages, queried_model="sma_sunnyboy_hf_2-3kw")
    assert result is None


def test_wrong_model_abstain_returns_most_frequent_other_model():
    passages = [
        {"doc_id": "fronius_symo_10-20kw", "page": 1, "text": "..."},
        {"doc_id": "fronius_symo_10-20kw", "page": 2, "text": "..."},
        {"doc_id": "sma_sunnyboy_tl_3-5kw", "page": 3, "text": "..."},
    ]
    result = wrong_model_abstain(passages, queried_model="sma_sunnyboy_hf_2-3kw")
    assert result is not None
    assert "fronius_symo_10-20kw" in result["reason"]
