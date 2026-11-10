import json
from pathlib import Path

QUESTIONS_PATH = Path("eval/questions.jsonl")
VALID_TYPES = {"code_lookup", "figure_question", "wrong_model_trap", "unanswerable"}
REQUIRED_FIELDS = {"id", "question", "model", "gold_doc", "gold_page", "gold_answer", "type"}


def load_questions() -> list[dict]:
    assert QUESTIONS_PATH.exists(), f"{QUESTIONS_PATH} not found"
    questions = []
    for i, line in enumerate(QUESTIONS_PATH.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            questions.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Line {i} is not valid JSON: {exc}") from exc
    return questions


def test_file_exists():
    assert QUESTIONS_PATH.exists()


def test_minimum_question_count():
    questions = load_questions()
    assert len(questions) >= 30, f"Expected at least 30 questions, got {len(questions)}"


def test_minimum_unanswerable_count():
    questions = load_questions()
    unanswerable = [q for q in questions if q.get("type") == "unanswerable"]
    assert len(unanswerable) >= 5, f"Expected at least 5 unanswerable, got {len(unanswerable)}"


def test_all_required_fields_present():
    for q in load_questions():
        missing = REQUIRED_FIELDS - q.keys()
        assert not missing, f"Question {q.get('id')} is missing fields: {missing}"


def test_ids_are_unique():
    questions = load_questions()
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "Duplicate question ids found"


def test_valid_type_values():
    for q in load_questions():
        assert q["type"] in VALID_TYPES, (
            f"Question {q['id']} has invalid type '{q['type']}'. Expected one of {VALID_TYPES}"
        )


def test_field_types():
    for q in load_questions():
        qid = q["id"]
        assert isinstance(q["id"], str), f"{qid}: id must be str"
        assert isinstance(q["question"], str), f"{qid}: question must be str"
        assert isinstance(q["gold_answer"], str), f"{qid}: gold_answer must be str"
        assert isinstance(q["type"], str), f"{qid}: type must be str"
        assert q["model"] is None or isinstance(q["model"], str), (
            f"{qid}: model must be str or null"
        )
        assert q["gold_doc"] is None or isinstance(q["gold_doc"], str), (
            f"{qid}: gold_doc must be str or null"
        )
        assert q["gold_page"] is None or isinstance(q["gold_page"], int), (
            f"{qid}: gold_page must be int or null"
        )


def test_code_lookup_questions_have_gold_doc():
    for q in load_questions():
        if q["type"] == "code_lookup":
            assert q["gold_doc"] is not None, f"Question {q['id']}: code_lookup must have gold_doc"
            assert q["gold_page"] is not None, (
                f"Question {q['id']}: code_lookup must have gold_page"
            )


def test_unanswerable_questions_have_null_gold_doc():
    for q in load_questions():
        if q["type"] == "unanswerable":
            assert q["gold_doc"] is None, (
                f"Question {q['id']}: unanswerable must have null gold_doc"
            )
            assert q["gold_page"] is None, (
                f"Question {q['id']}: unanswerable must have null gold_page"
            )


def test_mix_of_question_types():
    questions = load_questions()
    types_present = {q["type"] for q in questions}
    for expected_type in ("code_lookup", "figure_question", "wrong_model_trap", "unanswerable"):
        assert expected_type in types_present, f"No questions of type '{expected_type}' found"
