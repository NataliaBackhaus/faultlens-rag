import json
from unittest.mock import MagicMock, patch

from generation.llm_client import OllamaClient


def test_generate_returns_cached_result(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    client = OllamaClient()

    key = client._cache_key("qwen2.5:3b", "hello", None)

    cache_dir = tmp_path / "data" / "cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / f"{key}.json").write_text(json.dumps("cached response"))

    # Act
    with patch("generation.llm_client.httpx.post") as mock_post:
        result = client.generate("hello")

    # Assert
    assert result == "cached response"
    mock_post.assert_not_called()


def test_generate_calls_ollama_and_caches(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    client = OllamaClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "ollama response"}
    mock_response.raise_for_status.return_value = None

    # Act
    with patch("generation.llm_client.httpx.post", return_value=mock_response) as mock_post:
        result = client.generate("hello")

    # Assert
    assert result == "ollama response"
    mock_post.assert_called_once()

    # Checks if the cache folder was created
    key = client._cache_key("qwen2.5:3b", "hello", None)
    cache_file = tmp_path / "data" / "cache" / f"{key}.json"
    assert cache_file.exists()
    assert json.loads(cache_file.read_text()) == "ollama response"
