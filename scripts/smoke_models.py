"""Smoke test for local Ollama models.

Sends one text prompt to qwen2.5:3b and one image prompt to qwen2.5vl:7b,
then reports tokens/second for each. Used to decide whether ingestion
can run locally or needs a Kaggle GPU notebook.
"""

import base64
import time
from pathlib import Path

import httpx

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
TEXT_MODEL = "qwen2.5:3b"
VISION_MODEL = "qwen2.5vl:7b"


def generate(model: str, prompt: str) -> dict:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = httpx.post(OLLAMA_GENERATE_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def chat_with_image(model: str, prompt: str, image_b64: str) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
    }
    response = httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def tokens_per_second(result: dict) -> float:
    eval_count = result.get("eval_count", 0)
    eval_duration_ns = result.get("eval_duration", 1)
    return eval_count / (eval_duration_ns / 1e9)


def make_test_image() -> str:
    """Create a 64x64 grey PNG encoded as base64, without external dependencies."""
    import struct
    import zlib

    width, height = 64, 64
    raw_rows = b"".join(b"\x00" + bytes([128] * width * 3) for _ in range(height))
    compressed = zlib.compress(raw_rows)

    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )
    return base64.b64encode(png).decode()


def smoke_text() -> None:
    print(f"\n--- Text model: {TEXT_MODEL} ---")
    prompt = "What is a solar inverter? Answer in one sentence."
    t0 = time.perf_counter()
    result = generate(TEXT_MODEL, prompt)
    elapsed = time.perf_counter() - t0
    tps = tokens_per_second(result)
    print(f"Response: {result['response'].strip()}")
    print(f"Tokens/s: {tps:.1f}  |  Total time: {elapsed:.1f}s")


def smoke_vision(image_path: Path | None = None) -> None:
    print(f"\n--- Vision model: {VISION_MODEL} ---")
    if image_path and image_path.exists():
        image_b64 = base64.b64encode(image_path.read_bytes()).decode()
        print(f"Image: {image_path}")
    else:
        image_b64 = make_test_image()
        print("Image: synthetic 64x64 grey PNG (no real page provided)")
    prompt = "Describe what you see in this image in one sentence."
    t0 = time.perf_counter()
    result = chat_with_image(VISION_MODEL, prompt, image_b64)
    elapsed = time.perf_counter() - t0
    message = result.get("message", {}).get("content", "").strip()
    tps = tokens_per_second(result)
    print(f"Response: {message}")
    print(f"Tokens/s: {tps:.1f}  |  Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Smoke test for local Ollama models")
    parser.add_argument("--image", type=Path, help="Path to a manual page PNG or PDF page image")
    args = parser.parse_args()

    smoke_text()
    smoke_vision(args.image)
    print("\nSmoke test complete.")
