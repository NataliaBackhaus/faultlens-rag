from unittest.mock import MagicMock, patch


def fake_ollama_response(eval_count: int = 10, eval_duration_ns: int = 1_000_000_000) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {
        "response": "A solar inverter converts DC to AC.",
        "eval_count": eval_count,
        "eval_duration": eval_duration_ns,
        "done": True,
    }
    mock.raise_for_status.return_value = None
    return mock


def test_tokens_per_second():
    from scripts.smoke_models import tokens_per_second

    result = {"eval_count": 20, "eval_duration": 2_000_000_000}
    assert tokens_per_second(result) == 10.0


def test_generate_sends_correct_payload():
    from scripts.smoke_models import generate

    with patch("scripts.smoke_models.httpx.post", return_value=fake_ollama_response()) as mock_post:
        result = generate("qwen2.5:3b", "hello")

    payload = mock_post.call_args.kwargs["json"]
    assert payload["model"] == "qwen2.5:3b"
    assert payload["prompt"] == "hello"
    assert payload["stream"] is False
    assert result["response"] == "A solar inverter converts DC to AC."
