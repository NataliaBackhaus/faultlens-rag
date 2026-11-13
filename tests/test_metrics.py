import pytest

from eval.metrics import mrr, recall_at_k, wrong_model_rate

GOLD_DOC = "sma_sunnyboy_hf_2-3kw"
GOLD_PAGE = 66

HIT = {"doc_id": GOLD_DOC, "page": GOLD_PAGE, "models": [GOLD_DOC]}
MISS = {"doc_id": "fronius_symo_10-20kw", "page": 1, "models": ["fronius_symo_10-20kw"]}


# --- recall_at_k ---


def test_recall_at_k_hit_within_k():
    assert recall_at_k([HIT], GOLD_DOC, GOLD_PAGE, k=5) == 1.0


def test_recall_at_k_miss_returns_zero():
    assert recall_at_k([MISS], GOLD_DOC, GOLD_PAGE, k=5) == 0.0


def test_recall_at_k_hit_outside_k_returns_zero():
    results = [MISS, MISS, MISS, MISS, MISS, HIT]
    assert recall_at_k(results, GOLD_DOC, GOLD_PAGE, k=5) == 0.0


def test_recall_at_k_empty_results():
    assert recall_at_k([], GOLD_DOC, GOLD_PAGE, k=5) == 0.0


# --- mrr ---


def test_mrr_hit_at_first_position():
    assert mrr([HIT], GOLD_DOC, GOLD_PAGE) == 1.0


def test_mrr_hit_at_second_position():
    assert mrr([MISS, HIT], GOLD_DOC, GOLD_PAGE) == pytest.approx(0.5)


def test_mrr_hit_at_third_position():
    assert mrr([MISS, MISS, HIT], GOLD_DOC, GOLD_PAGE) == pytest.approx(1 / 3)


def test_mrr_no_hit_returns_zero():
    assert mrr([MISS, MISS], GOLD_DOC, GOLD_PAGE) == 0.0


def test_mrr_empty_results():
    assert mrr([], GOLD_DOC, GOLD_PAGE) == 0.0


# --- wrong_model_rate ---


def test_wrong_model_rate_all_correct():
    results = [HIT, HIT]
    assert wrong_model_rate(results, GOLD_DOC) == 0.0


def test_wrong_model_rate_all_wrong():
    results = [MISS, MISS]
    assert wrong_model_rate(results, GOLD_DOC) == 1.0


def test_wrong_model_rate_half_wrong():
    results = [HIT, MISS]
    assert wrong_model_rate(results, GOLD_DOC) == pytest.approx(0.5)


def test_wrong_model_rate_empty_results():
    assert wrong_model_rate([], GOLD_DOC) == 0.0
