"""Retrieval regression check for CI.

Reads eval/seed_index (committed to the repo) — no Docker, no LLM needed.
Exits 1 if recall@10 drops below THRESHOLD.
"""

import json
import sys
from statistics import mean

from qdrant_client import QdrantClient

from eval.metrics import recall_at_k
from retrieval.search import search

SEED_PATH = "eval/seed_index"
THRESHOLD = 0.40


def main() -> None:
    with open("eval/questions.jsonl") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    client = QdrantClient(path=SEED_PATH)

    recalls = []
    for q in questions:
        results = search(
            client,
            q["question"],
            model=None,
            manufacturer=None,
            k=10,
            prefetch_k=20,
            mode="hybrid",
        )
        recalls.append(recall_at_k(results, q["gold_doc"], q["gold_page"], k=10))

    mean_recall = mean(recalls)
    print(f"recall@10 (seed index, hybrid-20): {mean_recall:.3f}  threshold: {THRESHOLD}")

    if mean_recall < THRESHOLD:
        print("FAIL: recall@10 dropped below threshold")
        sys.exit(1)

    print("PASS")


if __name__ == "__main__":
    main()
