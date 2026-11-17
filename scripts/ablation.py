import json
from statistics import mean

from eval.metrics import mrr, recall_at_k
from ingest.index import get_client
from retrieval.search import search

CONFIGS = [
    {"mode": "dense", "prefetch_k": None},
    {"mode": "bm25", "prefetch_k": None},
    {"mode": "hybrid", "prefetch_k": 20},
    {"mode": "hybrid", "prefetch_k": 40},
    {"mode": "hybrid", "prefetch_k": 60},
]


def main():
    with open("eval/questions.jsonl") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    client = get_client()

    for config in CONFIGS:
        config_recall = []
        config_mrr = []

        for q in questions:
            results = search(
                client,
                q["question"],
                model=None,
                manufacturer=None,
                k=10,
                prefetch_k=config["prefetch_k"],
                mode=config["mode"],
            )
            config_recall.append(recall_at_k(results, q["gold_doc"], q["gold_page"], k=10))
            config_mrr.append(mrr(results, q["gold_doc"], q["gold_page"]))

        label = f"{config['mode']}-{config['prefetch_k'] or 'only'}"
        print(f"{label:20s} recall@10={mean(config_recall):.3f} mrr={mean(config_mrr):.3f}")


if __name__ == "__main__":
    main()
