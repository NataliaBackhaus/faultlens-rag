from unittest.mock import MagicMock, patch

import pytest
from qdrant_client.models import Filter

from ingest.index import get_client
from retrieval.search import build_filter, exact_code_lookup, retrieve


def qdrant_available() -> bool:
    try:
        get_client().get_collections()
        return True
    except Exception:
        return False


requires_qdrant = pytest.mark.skipif(not qdrant_available(), reason="Qdrant not running")


# --- build_filter ---


def test_build_filter_no_args_returns_none():
    assert build_filter(None, None) is None


def test_build_filter_model_only():
    f = build_filter("sma_sunnyboy_hf_2-3kw", None)
    assert isinstance(f, Filter)
    assert len(f.must) == 1
    assert f.must[0].key == "models"


def test_build_filter_manufacturer_only():
    f = build_filter(None, "SMA")
    assert isinstance(f, Filter)
    assert len(f.must) == 1
    assert f.must[0].key == "manufacturer"


def test_build_filter_both():
    f = build_filter("sma_sunnyboy_hf_2-3kw", "SMA")
    assert isinstance(f, Filter)
    assert len(f.must) == 2
    keys = {c.key for c in f.must}
    assert keys == {"models", "manufacturer"}


# --- exact_code_lookup ---


def test_exact_code_lookup_returns_list():
    client = MagicMock()
    client.scroll.return_value = ([], None)
    result = exact_code_lookup(client, "34", None)
    assert isinstance(result, list)


def test_exact_code_lookup_filters_by_error_code_and_record_type():
    client = MagicMock()
    client.scroll.return_value = ([], None)
    exact_code_lookup(client, "34", None)
    f = client.scroll.call_args.kwargs["scroll_filter"]
    keys = [c.key for c in f.must]
    assert "error_codes" in keys
    assert "record_type" in keys


def test_exact_code_lookup_adds_model_condition():
    client = MagicMock()
    client.scroll.return_value = ([], None)
    exact_code_lookup(client, "34", "sma_sunnyboy_hf_2-3kw")
    f = client.scroll.call_args.kwargs["scroll_filter"]
    keys = [c.key for c in f.must]
    assert "models" in keys


def test_exact_code_lookup_no_model_omits_models_condition():
    client = MagicMock()
    client.scroll.return_value = ([], None)
    exact_code_lookup(client, "34", None)
    f = client.scroll.call_args.kwargs["scroll_filter"]
    keys = [c.key for c in f.must]
    assert "models" not in keys


# --- retrieve ---


def test_retrieve_uses_exact_lookup_when_code_present():
    client = MagicMock()
    fake_result = [{"text": "event 34 row", "record_type": "table_row"}]
    with patch("retrieval.search.exact_code_lookup", return_value=fake_result) as mock_lookup:
        with patch("retrieval.search.search") as mock_search:
            result = retrieve(client, "event 34 on SB 2500HF")
    mock_lookup.assert_called_once()
    mock_search.assert_not_called()
    assert result == fake_result


def test_retrieve_falls_back_to_search_when_lookup_empty():
    client = MagicMock()
    fake_search = [{"text": "prose result"}]
    with patch("retrieval.search.exact_code_lookup", return_value=[]):
        with patch("retrieval.search.search", return_value=fake_search) as mock_search:
            result = retrieve(client, "event 34 on SB 2500HF")
    mock_search.assert_called_once()
    assert result == fake_search


def test_retrieve_skips_lookup_when_no_error_code():
    client = MagicMock()
    fake_search = [{"text": "some result"}]
    with patch("retrieval.search.exact_code_lookup") as mock_lookup:
        with patch("retrieval.search.search", return_value=fake_search):
            result = retrieve(client, "SB 2500HF is not working")
    mock_lookup.assert_not_called()
    assert result == fake_search


def test_retrieve_manufacturer_fallback_when_search_empty():
    client = MagicMock()
    fallback_result = [{"text": "manufacturer doc"}]
    with patch("retrieval.search.exact_code_lookup", return_value=[]):
        with patch("retrieval.search.search", side_effect=[[], fallback_result]) as mock_search:
            result = retrieve(client, "event 34 on SB 2500HF")
    assert mock_search.call_count == 2
    assert result[0]["_manufacturer_fallback"] is True


def test_retrieve_no_fallback_when_results_found():
    client = MagicMock()
    good_result = [{"text": "model-specific doc"}]
    with patch("retrieval.search.exact_code_lookup", return_value=[]):
        with patch("retrieval.search.search", return_value=good_result):
            result = retrieve(client, "event 34 on SB 2500HF")
    assert "_manufacturer_fallback" not in result[0]
