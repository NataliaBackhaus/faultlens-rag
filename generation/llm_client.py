import base64
import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


class LLMClient(ABC):
    @abstractmethod
    def generate(self, text, images=None, json_schema=None):
        pass


class OllamaClient(LLMClient):
    def __init__(self):
        with open(Path(__file__).parent.parent / "config.yaml") as f:
            config = yaml.safe_load(f)
        self.text_model = config["models"]["text"]
        self.vision_model = config["models"]["vision"]

    def _cache_key(self, model: str, text: str, images_b64: list[str] | None) -> str:
        raw = json.dumps({"model": model, "text": text, "images": images_b64}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _cache_get(self, key: str) -> str | None:
        path = Path("data/cache") / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None

    def _cache_set(self, key: str, value: str) -> None:
        path = Path("data/cache") / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def _to_base(self, image) -> str:
        if isinstance(image, Path):
            return base64.b64encode(image.read_bytes()).decode()
        return base64.b64encode(image).decode()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def generate(self, text, images=None, json_schema=None):
        images_b64 = [self._to_base(img) for img in images] if images else None

        model = self.vision_model if images_b64 else self.text_model
        key = self._cache_key(model, text, images_b64)

        cached = self._cache_get(key)
        if cached is not None:
            return cached

        if images is None:
            payload = {"model": self.text_model, "prompt": text, "stream": False}
            response = httpx.post(OLLAMA_GENERATE_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()["response"]
        else:
            payload = {
                "model": self.vision_model,
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": text,
                        "images": images_b64,
                    }
                ],
            }
            response = httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()["message"]["content"]

        self._cache_set(key, result)

        return result
