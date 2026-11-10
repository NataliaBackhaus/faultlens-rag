import pytest

from retrieval.query import extract_with_regex, parse_query

# --- error code extraction ---


@pytest.mark.parametrize(
    "text, expected_code",
    [
        ("event 34 on my inverter", "34"),
        ("error 34 appeared", "34"),
        ("fault 34 triggered", "34"),
        ("code 34 on display", "34"),
        ("E34 showed up", "34"),
        ("Event 65 on the inverter", "65"),
        ("event 1 appeared this morning", "1"),
        ("event 75 clean fan", "75"),
        ("what is event 9", "9"),
        ("no code here", None),
    ],
)
def test_error_code_extraction(text, expected_code):
    result = extract_with_regex(text)
    assert result["error_code"] == expected_code


# --- model extraction ---


@pytest.mark.parametrize(
    "text, expected_model",
    [
        ("event 34 on SB 2500HF", "sma_sunnyboy_hf_2-3kw"),
        ("SB2500HF shows event 34", "sma_sunnyboy_hf_2-3kw"),
        ("SB-2500HF fault", "sma_sunnyboy_hf_2-3kw"),
        ("my SB 3000HF has event 35", "sma_sunnyboy_hf_2-3kw"),
        ("SB 3000TL event 34", "sma_sunnyboy_tl_3-5kw"),
        ("SB 5000TL shows error 65", "sma_sunnyboy_tl_3-5kw"),
        ("Sunny Boy 5000TL fault 34", "sma_sunnyboy_tl_3-5kw"),
        ("Symo 10.0 error", "fronius_symo_10-20kw"),
        ("Fronius Symo 10.0 shows fault", "fronius_symo_10-20kw"),
        ("unknown model XYZ event 34", None),
    ],
)
def test_model_extraction(text, expected_model):
    result = extract_with_regex(text)
    assert result["model"] == expected_model


# --- parse_query ---


def test_parse_query_both_fields_extracted():
    result = parse_query("event 34 on SB 2500HF")
    assert result["error_code"] == "34"
    assert result["model"] == "sma_sunnyboy_hf_2-3kw"
    assert result["clarification"] is None


def test_parse_query_missing_model_sets_clarification():
    result = parse_query("event 34 on my inverter")
    assert result["error_code"] == "34"
    assert result["model"] is None
    assert result["clarification"] is not None
    assert isinstance(result["clarification"], str)


def test_parse_query_missing_error_code():
    result = parse_query("SB 2500HF is not working")
    assert result["error_code"] is None
    assert result["model"] == "sma_sunnyboy_hf_2-3kw"


def test_parse_query_nothing_found_sets_clarification():
    result = parse_query("my inverter is broken")
    assert result["error_code"] is None
    assert result["model"] is None
    assert result["clarification"] is not None


def test_parse_query_source_is_regex():
    result = parse_query("event 34 on SB 2500HF")
    assert result["source"] == "regex"


def test_parse_query_fronius_model():
    result = parse_query("Fronius Symo 10.0 shows fault 34")
    assert result["model"] == "fronius_symo_10-20kw"
    assert result["clarification"] is None


def test_parse_query_tl_model_variant():
    result = parse_query("SB 4000TL event 36")
    assert result["model"] == "sma_sunnyboy_tl_3-5kw"
    assert result["error_code"] == "36"


def test_parse_query_empty_string():
    result = parse_query("")
    assert result["error_code"] is None
    assert result["model"] is None
    assert result["clarification"] is not None


def test_parse_query_no_llm_does_not_raise():
    result = parse_query("event 34 SB 2500HF", llm=None)
    assert isinstance(result, dict)
