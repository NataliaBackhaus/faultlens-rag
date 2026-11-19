"""Batch-generate VLM descriptions for all cropped figure PNGs.

Writes one JSON line per figure to data/figure_descriptions.jsonl.
Re-running the script skips figures already described (resume-safe).
"""

import json
from pathlib import Path

from generation.llm_client import OllamaClient

FIGURES_DIR = Path("data/figures")
OUT_PATH = Path("data/figure_descriptions.jsonl")

PROMPT = (
    "You are analyzing a technical figure from an inverter installation manual. "
    "Describe the figure in detail: what it shows, every label and terminal visible, "
    "any error or status codes, LED states or indicator lights, and what a service "
    "technician would use this figure for. Be specific and factual. "
    "If the figure contains a table or list, include the values. "
    "Respond in English only."
)


def _load_done() -> set[tuple[str, int, int]]:
    if not OUT_PATH.exists():
        return set()
    done = set()
    with open(OUT_PATH) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                done.add((entry["doc_id"], entry["page"], entry["bbox_left"]))
    return done


def main():
    client = OllamaClient()
    done = _load_done()

    png_paths = sorted(FIGURES_DIR.glob("*/*.png"))
    total = len(png_paths)
    print(f"Found {total} figures, {len(done)} already described")

    with open(OUT_PATH, "a") as out:
        for i, path in enumerate(png_paths, 1):
            doc_id = path.parent.name
            stem = path.stem  # e.g. "0001_0153"
            parts = stem.split("_")
            page = int(parts[0])
            bbox_left = int(parts[1])

            if (doc_id, page, bbox_left) in done:
                continue

            description = client.generate(PROMPT, images=[path])

            entry = {
                "doc_id": doc_id,
                "page": page,
                "bbox_left": bbox_left,
                "description": description,
            }
            out.write(json.dumps(entry) + "\n")
            out.flush()

            print(f"[{i}/{total}] {doc_id} p{page} left={bbox_left}: {description[:60]}...")


if __name__ == "__main__":
    main()
