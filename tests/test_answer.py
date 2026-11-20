import json
from unittest.mock import MagicMock

from generation.answer import build_prompt, generate_answer

PASSAGES = [
    {
        "doc_id": "sma_sunnyboy_hf_2-3kw",
        "page": 42,
        "record_type": "table_row",
        "text": "34 | Grid voltage too high | Check grid voltage at AC terminals",
        "bbox": [0.0, 0.0, 100.0, 50.0],
        "section_path": "Event list",
    },
    {
        "doc_id": "sma_sunnyboy_hf_2-3kw",
        "page": 41,
        "record_type": "prose",
        "text": "WARNING: Disconnect AC and DC before servicing.",
        "bbox": [0.0, 0.0, 100.0, 50.0],
        "section_path": "Safety",
    },
    {
        "doc_id": "sma_sunnyboy_hf_2-3kw",
        "page": 10,
        "record_type": "prose",
        "text": "Event 34 indicates an overvoltage condition on the AC side.",
        "bbox": [0.0, 0.0, 100.0, 50.0],
        "section_path": "Troubleshooting",
    },
]

FIXED_RESPONSE = {
    "diagnosis": "Event 34 indicates AC grid voltage is too high.",
    "causes": ["Grid voltage above limit"],
    "steps": ["Check AC terminals", "Contact grid operator"],
    "safety": ["Disconnect AC and DC before servicing"],
    "citations": ["[1] sma_sunnyboy_hf_2-3kw p.41", "[2] sma_sunnyboy_hf_2-3kw p.42"],
}

QUESTIONS = [
    "What does event 34 mean on the SB 2500HF?",
    "What does event 35 mean on the SB 3000HF?",
    "Event 65 on SB 2500HF — what is the cause?",
    "What does event 75 indicate on the SB 2500HF?",
    "What does event 1 mean on the SB 3000TL?",
    "Event 34 on SB 5000TL — what should I do?",
    "What does event 9 mean on the SB 2500HF?",
    "What does event 10 mean on the SB 2000HF?",
    "Event 36 on SB 2500HF — what is it?",
    "What does event 37 mean on the SB 2500HF?",
]


# --- build_prompt ---


def test_build_prompt_contains_query():
    prompt = build_prompt("What does event 34 mean?", PASSAGES)
    assert "What does event 34 mean?" in prompt


def test_build_prompt_contains_passage_text():
    prompt = build_prompt("What does event 34 mean?", PASSAGES)
    assert "Grid voltage too high" in prompt


def test_build_prompt_safety_passage_comes_first():
    prompt = build_prompt("What does event 34 mean?", PASSAGES)
    warning_pos = prompt.index("WARNING")
    table_pos = prompt.index("Grid voltage too high")
    assert warning_pos < table_pos


def test_build_prompt_includes_doc_and_page():
    prompt = build_prompt("What does event 34 mean?", PASSAGES)
    assert "sma_sunnyboy_hf_2-3kw" in prompt
    assert "p.42" in prompt


def test_build_prompt_numbers_passages():
    prompt = build_prompt("What does event 34 mean?", PASSAGES)
    assert "[1]" in prompt
    assert "[2]" in prompt
    assert "[3]" in prompt


# --- generate_answer ---


def _make_client(response: dict) -> MagicMock:
    client = MagicMock()
    client.generate.return_value = json.dumps(response)
    return client


def test_generate_answer_returns_dict():
    client = _make_client(FIXED_RESPONSE)
    result = generate_answer(client, QUESTIONS[0], PASSAGES)
    assert isinstance(result, dict)


def test_generate_answer_has_required_keys():
    client = _make_client(FIXED_RESPONSE)
    result = generate_answer(client, QUESTIONS[0], PASSAGES)
    assert set(result.keys()) >= {"diagnosis", "causes", "steps", "safety", "citations"}


def test_generate_answer_citations_not_empty():
    client = _make_client(FIXED_RESPONSE)
    result = generate_answer(client, QUESTIONS[0], PASSAGES)
    assert len(result["citations"]) > 0


def test_generate_answer_strips_markdown_fence():
    client = MagicMock()
    client.generate.return_value = f"```json\n{json.dumps(FIXED_RESPONSE)}\n```"
    result = generate_answer(client, QUESTIONS[0], PASSAGES)
    assert isinstance(result, dict)
    assert "diagnosis" in result


def test_generate_answer_no_images_when_no_figures():
    client = _make_client(FIXED_RESPONSE)
    generate_answer(client, QUESTIONS[0], PASSAGES)
    _, kwargs = client.generate.call_args
    assert kwargs.get("images") is None


def test_generate_answer_passes_image_for_figure_passage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fig_dir = tmp_path / "data" / "figures" / "sma_sunnyboy_hf_2-3kw"
    fig_dir.mkdir(parents=True)
    png = fig_dir / "0005_0050.png"
    png.write_bytes(b"fake")

    passages_with_fig = PASSAGES + [
        {
            "doc_id": "sma_sunnyboy_hf_2-3kw",
            "page": 5,
            "record_type": "figure",
            "text": "Wiring diagram",
            "bbox": [50.0, 100.0, 300.0, 50.0],
            "section_path": "Installation",
        }
    ]

    client = _make_client(FIXED_RESPONSE)
    generate_answer(client, QUESTIONS[0], passages_with_fig)
    _, kwargs = client.generate.call_args
    assert kwargs.get("images") is not None
    assert len(kwargs["images"]) == 1


def test_generate_answer_snapshot_structure():
    """All 10 fixed questions return a dict with the expected schema."""
    client = _make_client(FIXED_RESPONSE)
    for q in QUESTIONS:
        result = generate_answer(client, q, PASSAGES)
        assert isinstance(result.get("diagnosis"), str)
        assert isinstance(result.get("causes"), list)
        assert isinstance(result.get("steps"), list)
        assert isinstance(result.get("safety"), list)
        assert isinstance(result.get("citations"), list)
