from unittest.mock import MagicMock

import pytest

from scripts.eval_answers import (
    MODEL_TO_DOC,
    citation_accuracy,
    compute_abstain_metrics,
    judge_answer,
)

PASSAGES = [
    {
        "doc_id": "sma_sunnyboy_hf_2-3kw",
        "page": 68,
        "text": "34 | DC overvoltage | Disconnect generator",
    },
    {
        "doc_id": "sma_sunnyboy_hf_2-3kw",
        "page": 69,
        "text": "35 | Insulation resist. | Check generator",
    },
]

QUESTION_HF = {
    "id": "q002",
    "question": "Event 34 on SB 2500HF — what should I do?",
    "model": "SB 2500HF",
    "gold_doc": "sma_sunnyboy_hf_2-3kw",
    "gold_page": 68,
    "gold_answer": "DC overvoltage. Disconnect the inverter from the PV array.",
    "type": "code_lookup",
}

QUESTION_NO_GOLD = {
    "id": "q023",
    "question": "What does event 9 mean on the SB 2500HF?",
    "model": "SB 2500HF",
    "gold_doc": None,
    "gold_page": None,
    "gold_answer": "Event 9 is not documented for the SB 2500HF.",
    "type": "wrong_model_trap",
}

ANSWER = {
    "diagnosis": "DC overvoltage detected.",
    "causes": ["DC input voltage too high"],
    "steps": ["Disconnect PV array"],
    "safety": ["WARNING: Disconnect before servicing"],
    "citations": ["[1] sma_sunnyboy_hf_2-3kw p.68"],
}


# --- citation_accuracy ---


def test_citation_accuracy_returns_none_when_no_gold_doc():
    assert citation_accuracy(ANSWER, QUESTION_NO_GOLD) is None


def test_citation_accuracy_returns_1_when_citation_matches():
    assert citation_accuracy(ANSWER, QUESTION_HF) == 1.0


def test_citation_accuracy_returns_0_when_no_match():
    answer = {**ANSWER, "citations": ["[1] sma_sunnyboy_hf_2-3kw p.99"]}
    assert citation_accuracy(answer, QUESTION_HF) == 0.0


def test_citation_accuracy_returns_0_when_wrong_doc():
    answer = {**ANSWER, "citations": ["[1] fronius_symo_10-20kw p.68"]}
    assert citation_accuracy(answer, QUESTION_HF) == 0.0


def test_citation_accuracy_returns_0_when_empty_citations():
    answer = {**ANSWER, "citations": []}
    assert citation_accuracy(answer, QUESTION_HF) == 0.0


def test_citation_accuracy_finds_match_among_multiple_citations():
    answer = {
        **ANSWER,
        "citations": [
            "[1] sma_sunnyboy_hf_2-3kw p.99",
            "[2] sma_sunnyboy_hf_2-3kw p.68",
        ],
    }
    assert citation_accuracy(answer, QUESTION_HF) == 1.0


# --- judge_answer ---


def _make_llm(response: str) -> MagicMock:
    llm = MagicMock()
    llm.generate.return_value = response
    return llm


def test_judge_answer_both_yes():
    llm = _make_llm("FAITHFUL: YES\nCORRECT: YES")
    faithful, correct = judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    assert faithful is True
    assert correct is True


def test_judge_answer_both_no():
    llm = _make_llm("FAITHFUL: NO\nCORRECT: NO")
    faithful, correct = judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    assert faithful is False
    assert correct is False


def test_judge_answer_faithful_yes_correct_no():
    llm = _make_llm("FAITHFUL: YES\nCORRECT: NO")
    faithful, correct = judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    assert faithful is True
    assert correct is False


def test_judge_answer_case_insensitive():
    llm = _make_llm("faithful: yes\ncorrect: yes")
    faithful, correct = judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    assert faithful is True
    assert correct is True


def test_judge_answer_prompt_contains_question():
    llm = _make_llm("FAITHFUL: YES\nCORRECT: YES")
    judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    prompt = llm.generate.call_args[0][0]
    assert QUESTION_HF["question"] in prompt


def test_judge_answer_prompt_contains_gold_answer():
    llm = _make_llm("FAITHFUL: YES\nCORRECT: YES")
    judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    prompt = llm.generate.call_args[0][0]
    assert QUESTION_HF["gold_answer"] in prompt


def test_judge_answer_prompt_contains_passage_text():
    llm = _make_llm("FAITHFUL: YES\nCORRECT: YES")
    judge_answer(llm, PASSAGES, QUESTION_HF, ANSWER)
    prompt = llm.generate.call_args[0][0]
    assert "DC overvoltage" in prompt


# --- compute_abstain_metrics ---

QUESTIONS = [
    {"id": "q001", "type": "code_lookup"},
    {"id": "q002", "type": "code_lookup"},
    {"id": "q023", "type": "wrong_model_trap"},
    {"id": "q024", "type": "wrong_model_trap"},
    {"id": "q031", "type": "unanswerable"},
]


def test_compute_abstain_perfect_precision_and_recall():
    results = [
        {"id": "q023", "abstained": True},
        {"id": "q024", "abstained": True},
        {"id": "q031", "abstained": True},
        {"id": "q001", "abstained": False},
        {"id": "q002", "abstained": False},
    ]
    precision, recall = compute_abstain_metrics(results, QUESTIONS)
    assert precision == 1.0
    assert recall == 1.0


def test_compute_abstain_no_abstentions():
    results = [{"id": q["id"], "abstained": False} for q in QUESTIONS]
    precision, recall = compute_abstain_metrics(results, QUESTIONS)
    assert precision == 0.0
    assert recall == 0.0


def test_compute_abstain_false_positive():
    results = [
        {"id": "q001", "abstained": True},
        {"id": "q023", "abstained": False},
        {"id": "q024", "abstained": False},
        {"id": "q031", "abstained": False},
        {"id": "q002", "abstained": False},
    ]
    precision, recall = compute_abstain_metrics(results, QUESTIONS)
    assert precision == 0.0
    assert recall == 0.0


def test_compute_abstain_partial_recall():
    results = [
        {"id": "q023", "abstained": True},
        {"id": "q024", "abstained": False},
        {"id": "q031", "abstained": False},
        {"id": "q001", "abstained": False},
        {"id": "q002", "abstained": False},
    ]
    precision, recall = compute_abstain_metrics(results, QUESTIONS)
    assert precision == 1.0
    assert recall == pytest.approx(1 / 3)


def test_compute_abstain_zero_division_no_did_abstain():
    results = [{"id": q["id"], "abstained": False} for q in QUESTIONS]
    precision, recall = compute_abstain_metrics(results, QUESTIONS)
    assert precision == 0.0


# --- MODEL_TO_DOC ---


def test_model_to_doc_hf_models():
    for model in ("SB 2000HF", "SB 2500HF", "SB 3000HF"):
        assert MODEL_TO_DOC[model] == "sma_sunnyboy_hf_2-3kw"


def test_model_to_doc_tl_models():
    for model in ("SB 3000TL", "SB 4000TL", "SB 5000TL"):
        assert MODEL_TO_DOC[model] == "sma_sunnyboy_tl_3-5kw"


def test_model_to_doc_fronius_models():
    for model in ("Fronius Symo 10.0-3-M", "Fronius Symo 20.0-3-M"):
        assert MODEL_TO_DOC[model] == "fronius_symo_10-20kw"
